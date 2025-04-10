
import streamlit as st
import pandas as pd
import geopandas as gpd
import zipfile
import requests
import io
import os
from shapely.geometry import LineString

st.set_page_config(layout="wide")
st.title("Linhas de Ônibus do Município do RJ - GTFS Estático")

GTFS_URL = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio.zip"
LOCAL_ZIP = "gtfs_rio.zip"

def baixar_arquivo_gtfs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(LOCAL_ZIP, "wb") as f:
            f.write(response.content)
        return LOCAL_ZIP
    except Exception as e:
        st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
        if os.path.exists(LOCAL_ZIP):
            return LOCAL_ZIP
        else:
            st.error("Nenhum dado disponível.")
            return None

def processar_gtfs_em_geojson(gtfs_zip_path):
    with zipfile.ZipFile(gtfs_zip_path, "r") as z:
        routes = pd.read_csv(z.open("routes.txt"))
        shapes = pd.read_csv(z.open("shapes.txt"))

    # Organiza pontos por sequência
    shapes = shapes.sort_values(by=["shape_id", "shape_pt_sequence"])
    geometries = []
    route_names = []

    # Agrupa por shape_id
    for shape_id, group in shapes.groupby("shape_id"):
        line = LineString(zip(group["shape_pt_lon"], group["shape_pt_lat"]))
        geometries.append(line)

        # Pega o nome da rota associada (se existir)
        route = routes[routes["shape_id"] == shape_id]
        if not route.empty:
            route_names.append(route.iloc[0]["route_short_name"])
        else:
            route_names.append("Desconhecida")

    gdf = gpd.GeoDataFrame({"route_short_name": route_names, "geometry": geometries}, crs="EPSG:4326")
    gdf.to_file("onibus_rj.geojson", driver="GeoJSON")
    return gdf

# Carrega ou processa os dados
gtfs_zip_path = baixar_arquivo_gtfs(GTFS_URL)
if gtfs_zip_path:
    try:
        if not os.path.exists("onibus_rj.geojson"):
            gdf = processar_gtfs_em_geojson(gtfs_zip_path)
        else:
            gdf = gpd.read_file("onibus_rj.geojson")
    except Exception as e:
        st.error(f"Erro ao processar os dados: {e}")
        gdf = None

    if gdf is not None and not gdf.empty:
        linhas = sorted(gdf["route_short_name"].dropna().unique())
        linhas_selecionadas = st.multiselect("Selecione uma ou mais linhas:", linhas)

        if linhas_selecionadas:
            gdf_filtrado = gdf[gdf["route_short_name"].isin(linhas_selecionadas)]
            st.map(gdf_filtrado)
        else:
            st.info("Selecione uma ou mais linhas para visualizar no mapa.")
