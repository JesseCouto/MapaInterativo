
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import zipfile
import requests
import os
from io import BytesIO

st.set_page_config(page_title="Linhas de Ônibus RJ", layout="wide")
st.title("Linhas de Ônibus - Município do Rio de Janeiro")

# Baixar GTFS do Data.Rio
gtfs_url = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio.zip"
gtfs_zip_path = "gtfs_rio.zip"

if not os.path.exists(gtfs_zip_path):
    try:
        r = requests.get(gtfs_url)
        with open(gtfs_zip_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        st.error(f"Erro ao baixar GTFS: {e}")

# Extrair os arquivos shapes.txt e routes.txt
with zipfile.ZipFile(gtfs_zip_path, "r") as z:
    shapes_df = pd.read_csv(z.open("shapes.txt"))
    routes_df = pd.read_csv(z.open("routes.txt"))

# Agrupar coordenadas por shape_id
shape_lines = shapes_df.groupby("shape_id").apply(
    lambda x: [[row['shape_pt_lat'], row['shape_pt_lon']] for _, row in x.sort_values('shape_pt_sequence').iterrows()]
).reset_index(name="coordinates")

# Juntar nomes das linhas pelas rotas
route_names = routes_df[["route_id", "route_short_name"]]
shape_lines["route_id"] = shape_lines["shape_id"].str.extract(r'(\d+)', expand=False)
shape_lines = shape_lines.merge(route_names, on="route_id", how="left")
shape_lines["route_name"] = shape_lines["route_short_name"].fillna("Sem nome")
shape_lines.dropna(subset=["coordinates"], inplace=True)

# Interface para seleção
unique_routes = shape_lines["route_name"].dropna().unique()
selected_routes = st.multiselect("Selecione uma ou mais linhas:", sorted(unique_routes))

# Mapa
m = folium.Map(location=[-22.9, -43.2], zoom_start=11)

if selected_routes:
    for _, row in shape_lines[shape_lines["route_name"].isin(selected_routes)].iterrows():
        folium.PolyLine(row["coordinates"], color="blue", weight=3).add_to(m)

st_folium(m, width=1000, height=600)
