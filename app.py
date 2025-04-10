
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

st.write("Conectando ao OpenStreetMap...")

try:
    url = "http://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query}, timeout=60)

    if response.status_code != 200:
        st.error(f"Erro na resposta do servidor: {response.status_code}")
        st.stop()

    data = response.json()
    if "elements" not in data or len(data["elements"]) == 0:
        st.warning("Nenhuma rota encontrada para o município do Rio de Janeiro.")
        st.stop()

    m = folium.Map(location=[-22.9068, -43.1729], zoom_start=12)

    for element in data["elements"]:
        if "geometry" in element:
            coords = [(point["lat"], point["lon"]) for point in element["geometry"]]
            folium.PolyLine(coords, color="blue", weight=2).add_to(m)

    st.success(f"Total de rotas carregadas: {len(data['elements'])}")
    st_folium(m, width=1200, height=700)

except requests.exceptions.Timeout:
    st.error("Tempo de resposta excedido. Tente novamente em alguns instantes.")
except requests.exceptions.ConnectionError:
    st.error("Erro de conexão. Verifique sua internet ou tente mais tarde.")
except Exception as e:
    st.error(f"Erro inesperado: {e}")
