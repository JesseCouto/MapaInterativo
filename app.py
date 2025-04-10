import requests
import folium
from streamlit_folium import st_folium
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("Mapa em Tempo Real dos Ônibus do Rio")

# Auto refresh a cada 30 segundos
st_autorefresh(interval=30_000, key="auto_refresh")
st.caption("Atualiza a cada 30 segundos automaticamente")

# Função para buscar dados da API pública
@st.cache_data(ttl=30)
def buscar_onibus():
    url = "https://dados.mobilidade.rio/gps/sppo"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Erro ao acessar a API.")
            return []
    except Exception as e:
        st.error(f"Erro: {e}")
        return []

# Buscar dados
dados = buscar_onibus()

# Pegar todas as linhas disponíveis
linhas_disponiveis = sorted(set(v.get("codigoLinha") for v in dados if "codigoLinha" in v))

# Seleção de linha(s)
linhas_selecionadas = st.multiselect(
    "Selecione as linhas que deseja ver no mapa:",
    options=linhas_disponiveis,
    default=["422"]
)

# Filtrar ônibus por linha selecionada
onibus_filtrados = [
    v for v in dados if v["codigoLinha"] in linhas_selecionadas
] if linhas_selecionadas else dados

# Criar o mapa
if onibus_filtrados:
    lat_inicial = onibus_filtrados[0]["latitude"]
    lon_inicial = onibus_filtrados[0]["longitude"]
    mapa = folium.Map(location=[lat_inicial, lon_inicial], zoom_start=13)

    for v in onibus_filtrados:
        popup = f"Linha: {v['codigoLinha']}<br>Placa: {v['ordem']}<br>Hora: {v['dataHora']}<br>Sentido: {v['sentido']}"
        folium.Marker([v["latitude"], v["longitude"]], popup=popup, icon=folium.Icon(color="blue")).add_to(mapa)

    st_folium(mapa, width=1000, height=600)
else:
    st.warning("Nenhum ônibus encontrado para a linha selecionada.")
