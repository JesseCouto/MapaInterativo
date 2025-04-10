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

# Obter as linhas disponíveis
linhas_disponiveis = sorted(set(v["codigoLinha"] for v in dados))
linha_selecionada = st.multiselect("Selecione uma ou mais linhas:", linhas_disponiveis)

# Filtrar dados com base nas linhas selecionadas
dados_filtrados = [v for v in dados if v["codigoLinha"] in linha_selecionada]

# Criar o mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=12)

# Adicionar marcadores
for viagem in dados_filtrados:
    folium.Marker(
        location=[viagem["latitude"], viagem["longitude"]],
        popup=f"Linha: {viagem['codigoLinha']} - Hora: {viagem['hora']}",
        icon=folium.Icon(color="blue", icon="bus", prefix="fa")
    ).add_to(m)

# Exibir mapa no Streamlit
st_folium(m, width=700)
