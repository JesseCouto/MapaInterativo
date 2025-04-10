
import streamlit as st
import geopandas as gpd
import requests
import zipfile
import io
import os

st.set_page_config(layout="wide")
st.title("Mapa Interativo de Linhas de Ônibus - Município do RJ")

GTFS_URL = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio.zip"
GTFS_ZIP_PATH = "gtfs_rio.zip"
ROUTES_GEOJSON = "onibus_rj.geojson"

def baixar_gtfs(url, path):
    try:
        st.info("Baixando dados atualizados do Data.Rio...")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
        return False

def extrair_rotas_do_gtfs(zip_path, geojson_path):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            routes = z.read("routes.txt").decode("utf-8").splitlines()
            shapes = z.read("shapes.txt").decode("utf-8").splitlines()

        import pandas as pd
        from shapely.geometry import LineString

        routes_df = pd.read_csv(io.StringIO("\n".join(routes)))
        shapes_df = pd.read_csv(io.StringIO("\n".join(shapes)))

        linhas = []
        for shape_id, grupo in shapes_df.groupby("shape_id"):
            linha = routes_df[routes_df["route_id"] == shape_id]
            if linha.empty:
                continue
            coords = grupo.sort_values("shape_pt_sequence")[["shape_pt_lon", "shape_pt_lat"]].values
            linhas.append({
                "route_id": shape_id,
                "route_name": linha.iloc[0]["route_short_name"],
                "geometry": LineString(coords)
            })

        gdf = gpd.GeoDataFrame(linhas, crs="EPSG:4326")
        gdf.to_file(geojson_path, driver="GeoJSON")
        return gdf

    except Exception as e:
        st.error(f"Erro ao extrair dados do GTFS: {e}")
        return None

# Fluxo principal
if not os.path.exists(GTFS_ZIP_PATH):
    baixar_gtfs(GTFS_URL, GTFS_ZIP_PATH)

if not os.path.exists(ROUTES_GEOJSON):
    if os.path.exists(GTFS_ZIP_PATH):
        gdf = extrair_rotas_do_gtfs(GTFS_ZIP_PATH, ROUTES_GEOJSON)
    else:
        gdf = None
else:
    gdf = gpd.read_file(ROUTES_GEOJSON)

if gdf is not None:
    linhas = sorted(gdf["route_name"].dropna().unique())
    linhas_sel = st.multiselect("Selecione uma ou mais linhas:", linhas)
    if linhas_sel:
        selecao = gdf[gdf["route_name"].isin(linhas_sel)]
        st.map(selecao)
    else:
        st.map(gdf)
else:
    st.error("Não foi possível carregar os dados de linhas de ônibus.")
