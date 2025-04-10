
import streamlit as st
import requests
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Rotas de Ônibus do Rio de Janeiro (via OpenStreetMap)")

# Overpass API Query
query = """
[out:json][timeout:25];
area["name"="Rio de Janeiro"]->.searchArea;
(
  relation["route"="bus"](area.searchArea);
);
out geom;
"""

st.write("Carregando dados de rotas de ônibus do OpenStreetMap...")
url = "http://overpass-api.de/api/interpreter"
response = requests.post(url, data={"data": query})

if response.status_code != 200:
    st.error("Erro ao buscar dados do OpenStreetMap.")
else:
    data = response.json()
    m = folium.Map(location=[-22.9068, -43.1729], zoom_start=12)

    for element in data["elements"]:
        if "geometry" in element:
            coords = [(point["lat"], point["lon"]) for point in element["geometry"]]
            folium.PolyLine(coords, color="blue", weight=2).add_to(m)

    st.write(f"Total de rotas carregadas: {len(data['elements'])}")
    st_data = st_folium(m, width=1200, height=700)
