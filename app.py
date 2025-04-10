import streamlit as st
import pandas as pd
import requests

st.title("Monitoramento em tempo real - Ônibus RJ")

# URL com os dados em tempo real
url = "http://www.consorcio.rio/baixar/VehiclesPositions.json"

# Fazer a requisição dos dados
try:
    response = requests.get(url)
    data = response.json()

    # Transformar os dados em DataFrame
    df = pd.DataFrame(data)

    # Renomear para uso no mapa
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})

    # Selecionar linha
    linhas = df["CodigoLinha"].unique()
    linha_escolhida = st.selectbox("Escolha a linha:", sorted(linhas))

    df_linha = df[df["CodigoLinha"] == linha_escolhida]

    # Mostrar dados no mapa
    st.map(df_linha[["lat", "lon"]])

    # Mostrar tabela opcional
    if st.checkbox("Mostrar dados brutos"):
        st.dataframe(df_linha)

except Exception as e:
    st.error("Erro ao carregar os dados: " + str(e))
