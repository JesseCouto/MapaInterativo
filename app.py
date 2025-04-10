
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import os
from pathlib import Path
import shutil

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

GTFS_DIR = Path("gtfs_data")
GTFS_ZIP = "gtfs.zip"

def extrair_gtfs(caminho_zip):
    if GTFS_DIR.exists():
        shutil.rmtree(GTFS_DIR)
    GTFS_DIR.mkdir(exist_ok=True)
    with zipfile.ZipFile(caminho_zip, "r") as z:
        z.extractall(GTFS_DIR)

def carregar_dados_gtfs():
    shapes_path = GTFS_DIR / "shapes.txt"
    routes_path = GTFS_DIR / "routes.txt"
    trips_path = GTFS_DIR / "trips.txt"

    shapes = pd.read_csv(shapes_path)
    routes = pd.read_csv(routes_path)
    trips = pd.read_csv(trips_path)

    merged = pd.merge(trips, routes, on="route_id")
    merged = pd.merge(merged, shapes, on="shape_id")

    gdf_list = []
    for shape_id, group in merged.groupby("shape_id"):
        line = gpd.GeoSeries(gpd.points_from_xy(group.shape_pt_lon, group.shape_pt_lat)).unary_union
        route_name = group.iloc[0]["route_long_name"]
        gdf_list.append({
            "shape_id": shape_id,
            "route_name": route_name,
            "geometry": line
        })

    gdf = gpd.GeoDataFrame(gdf_list, crs="EPSG:4326")
    return gdf

# Upload de arquivo
upload = st.file_uploader("Envie o arquivo GTFS (.zip):", type="zip")

# Se o usuário fizer upload, usa esse arquivo
if upload is not None:
    with open(GTFS_ZIP, "wb") as f:
        f.write(upload.read())
    extrair_gtfs(GTFS_ZIP)
    st.success("Arquivo GTFS carregado com sucesso.")
elif not GTFS_DIR.exists():
    st.error("Erro: Nenhum GTFS carregado e nenhum cache local encontrado.")
    st.stop()

# Carregar dados
gdf = carregar_dados_gtfs()
linhas = sorted(gdf["route_name"].dropna().unique())
linha_selecionada = st.selectbox("Selecione a linha:", linhas)

# Filtrar geometria
gdf_filtrado = gdf[gdf["route_name"] == linha_selecionada]

# Criar mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
for _, row in gdf_filtrado.iterrows():
    if hasattr(row["geometry"], "geoms"):
        for geom in row["geometry"].geoms:
            folium.PolyLine(locations=[(p.y, p.x) for p in geom.coords]).add_to(m)
    else:
        folium.PolyLine(locations=[(p.y, p.x) for p in row["geometry"].coords]).add_to(m)

st_folium(m, width=1000, height=600)
