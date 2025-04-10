
import streamlit as st
import geopandas as gpd
import requests
import zipfile
import io
import os

st.set_page_config(page_title="Linhas de Ônibus RJ", layout="wide")
st.title("Linhas de Ônibus do Município do Rio de Janeiro")

# Caminho local para cache
local_zip_path = "gtfs_rio.zip"
local_geojson_path = "onibus_rj.geojson"

# URL oficial do GTFS
gtfs_url = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio.zip"

def baixar_arquivo_gtfs():
    try:
        st.info("Baixando dados atualizados do Data.Rio...")
        response = requests.get(gtfs_url)
        if response.ok:
            with open(local_zip_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
            return False
    except Exception as e:
        st.error(f"Erro ao baixar os dados: {e}")
        return False

def extrair_shape_para_geojson(zip_path, geojson_path):
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall("gtfs_temp")
        shapes_path = os.path.join("gtfs_temp", "shapes.txt")
        routes_path = os.path.join("gtfs_temp", "routes.txt")
        trips_path = os.path.join("gtfs_temp", "trips.txt")

        import pandas as pd
        shapes = pd.read_csv(shapes_path)
        routes = pd.read_csv(routes_path)
        trips = pd.read_csv(trips_path)

        # Pega apenas colunas essenciais
        shapes = shapes.sort_values(["shape_id", "shape_pt_sequence"])
        linhas = []

        for shape_id, group in shapes.groupby("shape_id"):
            coords = list(zip(group["shape_pt_lon"], group["shape_pt_lat"]))
            linha = {"shape_id": shape_id, "geometry": {"type": "LineString", "coordinates": coords}}
            linhas.append(linha)

        gdf = gpd.GeoDataFrame(linhas)
        gdf.set_geometry(gpd.GeoSeries.from_wkt(gdf["geometry"].astype(str)), inplace=True)
        gdf.to_file(geojson_path, driver="GeoJSON")
        return gdf
    except Exception as e:
        st.error(f"Erro ao processar os dados do GTFS: {e}")
        return None

# Tenta baixar e atualizar os dados
if baixar_arquivo_gtfs() or os.path.exists(local_zip_path):
    gdf = None
    if not os.path.exists(local_geojson_path):
        gdf = extrair_shape_para_geojson(local_zip_path, local_geojson_path)
    else:
        try:
            gdf = gpd.read_file(local_geojson_path)
        except:
            gdf = extrair_shape_para_geojson(local_zip_path, local_geojson_path)

    if gdf is not None and not gdf.empty:
        st.success("Dados carregados com sucesso!")
        st.map(gdf)
    else:
        st.warning("Nenhuma linha encontrada para exibir.")
else:
    st.error("Não foi possível carregar os dados do GTFS.")
