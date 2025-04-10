import streamlit as st
import pandas as pd

# Simulação dos dados carregados (substitua isso pelo seu carregamento real)
dados = [
    {"codigoLinha": "001", "latitude": -22.9, "longitude": -43.2, "hora": "12:00"},
    {"codigoLinha": "002", "latitude": -22.91, "longitude": -43.21, "hora": "12:10"},
    {"codigoLinha": "001", "latitude": -22.89, "longitude": -43.19, "hora": "12:05"}
]

df = pd.DataFrame(dados)

st.title("Visualização de Linhas de Ônibus")

# Mostrar checkbox para exibir exemplo de dados
if st.checkbox("Mostrar exemplo de dado carregado"):
    st.markdown("**Exemplo de dado carregado:**")
    st.json(df.iloc[0].to_dict())

# Seleção de linha
linhas_disponiveis = df["codigoLinha"].unique()
linha_selecionada = st.selectbox("Selecione uma linha:", linhas_disponiveis)

# Filtrando os dados pela linha selecionada
df_filtrado = df[df["codigoLinha"] == linha_selecionada]

# Exibindo o mapa com os dados filtrados
st.map(df_filtrado.rename(columns={"latitude": "lat", "longitude": "lon"}))
