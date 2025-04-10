import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
from pathlib import Path
import zipfile
import shutil

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

GTFS_DIR = Path("gtfs_data")
GTFS_ZIP = Path("gtfs_data.zip")

def extrair_gtfs(caminho_zip):
    if GTFS_DIR.exists():
        shutil.rmtree(GTFS_DIR)
    with zipfile.ZipFile(caminho_zip, "r") as zip_ref:
        zip_ref.extractall(GTFS_DIR)

def carregar_dados_gtfs():
    shapes = pd.read_csv(GTFS_DIR / "shapes.txt")
    routes = pd.read_csv(GTFS_DIR / "routes.txt")
    trips = pd.read_csv(GTFS_DIR / "trips.txt")

    merged = pd.merge(trips, routes, on="route_id")
    merged = pd.merge(merged, shapes, on="shape_id")
    merged.sort_values(by=["shape_id", "shape_pt_sequence"], inplace=True)

    shapes_grouped = merged.groupby("shape_id")
    geoms = []
    nomes = []
    for shape_id, group in shapes_grouped:
        coords = list(zip(group["shape_pt_lon"], group["shape_pt_lat"]))
        geoms.append(coords)
        nomes.append(group["route_short_name"].iloc[0])

    gdf = gpd.GeoDataFrame({"route_name": nomes, "geometry": [gpd.points_from_xy(*zip(*line)) for line in geoms]})
    return gdf

# Upload do usuário
upload_novo = st.checkbox("Deseja enviar um novo arquivo GTFS (.zip)?")
if upload_novo:
    uploaded_file = st.file_uploader("Envie o arquivo .ZIP com o GTFS", type=["zip"])
    if uploaded_file:
        with open(GTFS_ZIP, "wb") as f:
            f.write(uploaded_file.read())
        extrair_gtfs(GTFS_ZIP)
        st.success("Arquivo GTFS carregado com sucesso.")
elif GTFS_DIR.exists():
    st.info("Usando o último arquivo GTFS disponível.")
else:
    st.warning("Nenhum arquivo GTFS disponível. Envie um para continuar.")
    st.stop()

# Processamento
gdf = carregar_dados_gtfs()

# Mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=11, tiles="CartoDB Positron")
for _, row in gdf.iterrows():
    pontos = [(p.y, p.x) for p in row["geometry"]]
    folium.PolyLine(locations=pontos, color="blue", weight=2).add_to(m)
st_folium(m, width=1000, height=600)
