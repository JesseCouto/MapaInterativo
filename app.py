import streamlit as st
import json
import folium
from streamlit_folium import st_folium

# Tentando carregar os dados
try:
    with open("dados/viagens.json", "r", encoding="utf-8") as f:
        dados = json.load(f)
    st.write("Exemplo de dado carregado:", dados[:1])
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    dados = []

# Exibir mapa básico
m = folium.Map(location=[-22.9, -43.2], zoom_start=12)
st_folium(m, width=700)
