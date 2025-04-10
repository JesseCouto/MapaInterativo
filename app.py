
import streamlit as st
import geopandas as gpd
import os
import requests

st.set_page_config(layout="wide")
st.title("Mapa Interativo de Linhas de Ônibus do Rio de Janeiro")

geojson_url = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio/gtfs_lines.geojson"
local_path = "onibus_rj.geojson"

@st.cache_data(show_spinner=True)
def baixar_geojson():
    try:
        response = requests.get(geojson_url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        st.error(f"Erro ao baixar dados: {e}")

def carregar_dados():
    if not os.path.exists(local_path):
        baixar_geojson()
    try:
        gdf = gpd.read_file(local_path)
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

gdf = carregar_dados()

if gdf is not None and not gdf.empty:
    linhas = sorted(gdf["name"].unique())
    linhas_selecionadas = st.multiselect("Selecione uma ou mais linhas:", linhas)
    if linhas_selecionadas:
        gdf_filtrado = gdf[gdf["name"].isin(linhas_selecionadas)]
        st.map(gdf_filtrado)
    else:
        st.info("Selecione ao menos uma linha para visualizar o itinerário.")
else:
    st.warning("Nenhuma linha carregada.")
