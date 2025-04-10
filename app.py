
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Mapa Interativo - Linhas de Ônibus do Rio de Janeiro")

# Carrega os dados GeoJSON
gdf = gpd.read_file("dados/onibus_osm_rj.geojson")

# Lista de linhas únicas
linhas_disponiveis = gdf['name'].unique().tolist()

# Seleção de linhas
linhas_selecionadas = st.multiselect("Selecione uma ou mais linhas de ônibus:", sorted(linhas_disponiveis))

# Cria o mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=12)

# Filtra e plota as linhas selecionadas
if linhas_selecionadas:
    gdf_filtrado = gdf[gdf['name'].isin(linhas_selecionadas)]
    for _, row in gdf_filtrado.iterrows():
        folium.PolyLine(locations=[(coord[1], coord[0]) for coord in row['geometry'].coords],
                        tooltip=row['name'],
                        color='blue',
                        weight=4).add_to(m)
else:
    st.info("Selecione uma ou mais linhas para visualizar o itinerário no mapa.")

# Exibe o mapa
st_folium(m, width=1000, height=600)
