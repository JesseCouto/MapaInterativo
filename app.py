
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from pathlib import Path
import zipfile
import shutil

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

GTFS_DIR = Path("gtfs_data")
GTFS_ZIP = Path("gtfs_data.zip")

def extrair_gtfs(arquivo_zip):
    if GTFS_DIR.exists():
        shutil.rmtree(GTFS_DIR)
    with zipfile.ZipFile(arquivo_zip, 'r') as zip_ref:
        zip_ref.extractall(GTFS_DIR)

# Interface para escolha do arquivo GTFS
usar_arquivo_existente = False
if GTFS_ZIP.exists():
    usar_arquivo_existente = st.radio(
        "Deseja usar o último GTFS carregado ou enviar um novo?",
        ["Usar último arquivo", "Enviar novo arquivo"]
    ) == "Usar último arquivo"

if not usar_arquivo_existente:
    uploaded_file = st.file_uploader("Envie o arquivo .zip com os dados GTFS", type="zip")
    if uploaded_file is not None:
        with open(GTFS_ZIP, "wb") as f:
            f.write(uploaded_file.read())
        extrair_gtfs(GTFS_ZIP)
else:
    if GTFS_ZIP.exists():
        extrair_gtfs(GTFS_ZIP)
    else:
        st.error("Nenhum arquivo GTFS anterior disponível. Faça o upload de um novo.")
        st.stop()

# Processamento dos dados GTFS
try:
    shapes = gpd.read_file(GTFS_DIR / "shapes.txt")
    routes = gpd.read_file(GTFS_DIR / "routes.txt")
    trips = gpd.read_file(GTFS_DIR / "trips.txt")
except Exception as e:
    st.error(f"Erro ao ler arquivos do GTFS: {e}")
    st.stop()

# Exemplo de mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
folium.Marker(location=[-22.9, -43.2], popup="Centro do RJ").add_to(m)
folium_static(m)
