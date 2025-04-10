
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
from io import BytesIO
import zipfile
from pathlib import Path

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

@st.cache_data
def baixar_e_extrair_arquivos_gtfs():
    url = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio/gtfs.zip"
    try:
        response = requests.get(url)
        response.raise_for_status()
        zip_data = BytesIO(response.content)
        with zipfile.ZipFile(zip_data, "r") as z:
            z.extractall("gtfs_data")
        return "gtfs_data"
    except Exception as e:
        st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
        if Path("gtfs_data").exists():
            return "gtfs_data"
        else:
            st.error("Erro ao baixar e não há cache local disponível.")
            return None

@st.cache_data
def carregar_itinerarios(path_gtfs):
    if path_gtfs is None:
        return gpd.GeoDataFrame()
    shapes_path = Path(path_gtfs) / "shapes.txt"
    routes_path = Path(path_gtfs) / "routes.txt"
    trips_path = Path(path_gtfs) / "trips.txt"

    if not (shapes_path.exists() and routes_path.exists() and trips_path.exists()):
        st.error("Arquivos GTFS necessários não encontrados.")
        return gpd.GeoDataFrame()

    import pandas as pd
    shapes = pd.read_csv(shapes_path)
    routes = pd.read_csv(routes_path)
    trips = pd.read_csv(trips_path)

    merged = trips.merge(routes, on="route_id").merge(shapes, on="shape_id")
    merged.sort_values(["shape_id", "shape_pt_sequence"], inplace=True)
    merged["geometry"] = merged.groupby("shape_id")[["shape_pt_lat", "shape_pt_lon"]].transform(lambda x: list(zip(x.shape_pt_lon, x.shape_pt_lat)))
    geometries = merged.groupby("shape_id").apply(lambda x: x.geometry.iloc[0]).apply(lambda coords: LineString(coords))
    gdf = gpd.GeoDataFrame(merged.drop_duplicates("shape_id"), geometry=geometries, crs="EPSG:4326")
    gdf["route_name"] = gdf["route_short_name"].astype(str)
    return gdf

from shapely.geometry import LineString

gtfs_path = baixar_e_extrair_arquivos_gtfs()
gdf = carregar_itinerarios(gtfs_path)

if gdf.empty:
    st.stop()

linhas = sorted(gdf["route_name"].dropna().unique())
linhas_selecionadas = st.multiselect("Selecione as linhas de ônibus", linhas)

m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
for _, row in gdf[gdf["route_name"].isin(linhas_selecionadas)].iterrows():
    geometry = row["geometry"]
    if hasattr(geometry, "geoms"):
        coords = [(p.y, p.x) for p in geometry.geoms]
    else:
        coords = [(p[1], p[0]) for p in geometry.coords]
    folium.PolyLine(locations=coords, color="blue", weight=3, opacity=0.7).add_to(m)

st_data = st_folium(m, width=1200, height=600)
