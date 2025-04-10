
import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import os
import datetime

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do Rio de Janeiro")

# Caminho do arquivo local
local_file = "onibus_rj.geojson"

# URL dos dados do Data.Rio
data_url = "https://dados.mobilidade.rio/gis/rio_itinerarios.geojson"

def download_data():
    try:
        response = requests.get(data_url)
        if response.status_code == 200:
            with open(local_file, "wb") as f:
                f.write(response.content)
            return True
        else:
            return False
    except Exception as e:
        print(f"Erro ao baixar dados: {e}")
        return False

# Atualiza o arquivo local uma vez por dia
def update_if_needed():
    if not os.path.exists(local_file):
        download_data()
    else:
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(local_file))
        if (datetime.datetime.now() - mod_time).days >= 1:
            download_data()

update_if_needed()

# Carrega os dados
try:
    gdf = gpd.read_file(local_file)
    linhas = gdf["linha"].dropna().unique()
    linhas_selecionadas = st.multiselect("Selecione as linhas:", sorted(linhas))
    
    if linhas_selecionadas:
        gdf_filtrado = gdf[gdf["linha"].isin(linhas_selecionadas)]
        
        m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
        folium.TileLayer("cartodbpositron").add_to(m)
        
        for _, row in gdf_filtrado.iterrows():
            folium.GeoJson(row["geometry"], tooltip=row["linha"]).add_to(m)
        
        st_folium(m, width=1200, height=600)
    else:
        st.info("Selecione uma ou mais linhas para visualizar no mapa.")

except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
