
import streamlit as st
import pandas as pd
import geopandas as gpd
import requests
import zipfile
import io
from shapely.geometry import LineString
import os

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

GTFS_URL = "https://dados.mobilidade.rio/gpsgtfs/gtfs_rio.zip"
LOCAL_ZIP = "gtfs_rio.zip"

@st.cache_data
def baixar_e_extrair_arquivos_gtfs():
    try:
        response = requests.get(GTFS_URL, timeout=10)
        response.raise_for_status()
        with open(LOCAL_ZIP, "wb") as f:
            f.write(response.content)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            z.extractall("gtfs_data")
    except Exception as e:
        st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
        if not Path("gtfs_data").exists():
            st.error("Nenhum dado GTFS disponível.")
            return None
    return "gtfs_data"

def carregar_itinerarios(gtfs_dir):
    try:
        stops = pd.read_csv(f"{gtfs_dir}/stops.txt")
        stop_times = pd.read_csv(f"{gtfs_dir}/stop_times.txt")
        trips = pd.read_csv(f"{gtfs_dir}/trips.txt")
        routes = pd.read_csv(f"{gtfs_dir}/routes.txt")

        df = pd.merge(trips, routes, on="route_id")
        df = pd.merge(df, stop_times, on="trip_id")
        df = pd.merge(df, stops, on="stop_id")
        
        linhas = df["route_short_name"].unique()
        linha_escolhida = st.selectbox("Selecione uma linha:", sorted(linhas))

        df_linha = df[df["route_short_name"] == linha_escolhida]
        coords_grouped = df_linha.groupby("trip_id").apply(
            lambda x: LineString(zip(x.sort_values("stop_sequence")["stop_lon"],
                                     x.sort_values("stop_sequence")["stop_lat"]))
        )

        gdf = gpd.GeoDataFrame(geometry=coords_grouped)
        gdf = gdf.set_crs("EPSG:4326")
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

gtfs_path = baixar_e_extrair_arquivos_gtfs()
if gtfs_path:
    gdf = carregar_itinerarios(gtfs_path)
    if gdf is not None and not gdf.empty:
        st.map(gdf)
