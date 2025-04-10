
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa Interativo - Linhas de Ônibus OSM (RJ)")

# Carrega os dados GeoJSON
gdf = gpd.read_file("dados/onibus_osm_rj.geojson")

# Extrai os nomes das linhas
linhas_disponiveis = sorted(gdf["name"].dropna().unique())

# Interface para seleção múltipla
linhas_selecionadas = st.multiselect(
    "Selecione uma ou mais linhas para visualizar no mapa:",
    linhas_disponiveis,
    default=linhas_disponiveis[:1]
)

# Filtra os dados conforme seleção
gdf_filtrado = gdf[gdf["name"].isin(linhas_selecionadas)]

# Cria o mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=11)

# Adiciona os itinerários filtrados no mapa
for _, row in gdf_filtrado.iterrows():
    folium.GeoJson(row["geometry"], tooltip=row["name"]).add_to(m)

# Mostra o mapa no Streamlit
st_data = st_folium(m, width=800, height=600)
