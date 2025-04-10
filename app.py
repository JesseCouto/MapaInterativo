
import streamlit as st
import zipfile
import os
import pandas as pd
import geopandas as gpd
import folium
from folium import Map, LayerControl
from streamlit_folium import st_folium
from io import BytesIO
from pathlib import Path

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

CACHE_DIR = Path("gtfs_cache")
GTFS_ZIP = CACHE_DIR / "gtfs_rj.zip"
GTFS_DIR = CACHE_DIR / "gtfs_extracted"

def extrair_gtfs(zip_path):
    if GTFS_DIR.exists():
        shutil.rmtree(GTFS_DIR)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(GTFS_DIR)

def carregar_dados_gtfs(gtfs_path):
    trips = pd.read_csv(gtfs_path / "trips.txt")
    shapes = pd.read_csv(gtfs_path / "shapes.txt")
    routes = pd.read_csv(gtfs_path / "routes.txt")

    merged = pd.merge(trips, routes, on="route_id")
    shapes_grouped = shapes.groupby("shape_id")

    linhas_geo = []

    for shape_id, shape_data in shapes_grouped:
        shape_data = shape_data.sort_values(by="shape_pt_sequence")
        coords = list(zip(shape_data["shape_pt_lon"], shape_data["shape_pt_lat"]))
        linha = merged[merged["shape_id"] == shape_id].iloc[0]
        nome = linha["route_short_name"]
        linhas_geo.append({"route_name": nome, "geometry": coords})

    gdf = gpd.GeoDataFrame(linhas_geo)
    return gdf

CACHE_DIR.mkdir(exist_ok=True)

opcao = st.radio("Deseja usar o último arquivo GTFS salvo ou carregar um novo?", ["Usar cache", "Fazer upload de novo arquivo"])

if opcao == "Fazer upload de novo arquivo":
    uploaded_file = st.file_uploader("Faça upload do arquivo .zip contendo os dados GTFS", type=["zip"])
    if uploaded_file:
        GTFS_ZIP.write_bytes(uploaded_file.read())
        st.success("Novo arquivo GTFS carregado com sucesso.")
        extrair_gtfs(GTFS_ZIP)
elif GTFS_ZIP.exists():
    st.info("Usando o arquivo GTFS salvo anteriormente.")
    extrair_gtfs(GTFS_ZIP)
else:
    st.error("Nenhum arquivo GTFS encontrado. Por favor, envie um arquivo.")
    st.stop()

try:
    gdf = carregar_dados_gtfs(GTFS_DIR)

    m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
    for _, row in gdf.iterrows():
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in row["geometry"]],
            tooltip=f"Linha {row['route_name']}",
            color="blue",
            weight=2,
        ).add_to(m)
    folium.LayerControl().add_to(m)
    st_folium(m, width=1200, height=700)
except Exception as e:
    st.error(f"Erro ao processar os dados GTFS: {e}")
