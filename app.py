import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import pydeck as pdk
from google.transit import gtfs_realtime_pb2
import datetime
import time

st.set_page_config(page_title="GTFS Rio - Análise Completa", layout="wide", page_icon="🚌")

GTFS_URL = "https://dados.mobilidade.rio/gis/gtfs.zip"
GTFS_REALTIME_VP = "https://dados.mobilidade.rio/gps/gtfs-rt-vp"

# Estilo customizado
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        color: white;
        background-color: #0d6efd;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
    }
    .stDownloadButton>button {
        background-color: #198754;
        color: white;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def carregar_dados_gtfs(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return None
        z = zipfile.ZipFile(io.BytesIO(response.content))
        dados = {name: pd.read_csv(z.open(name)) for name in z.namelist() if name.endswith('.txt')}
        return dados
    except Exception:
        return None

@st.cache_data
def carregar_dados_gtfs_manual(uploaded_file):
    try:
        z = zipfile.ZipFile(uploaded_file)
        dados = {name: pd.read_csv(z.open(name)) for name in z.namelist() if name.endswith('.txt')}
        return dados
    except Exception:
        st.error("Erro ao processar o arquivo GTFS enviado.")
        return None

def carregar_dados_realtime():
    feed = gtfs_realtime_pb2.FeedMessage()
    try:
        response = requests.get(GTFS_REALTIME_VP)
        feed.ParseFromString(response.content)
        dados = []
        for entity in feed.entity:
            if entity.HasField("vehicle"):
                info = entity.vehicle
                dados.append({
                    "trip_id": info.trip.trip_id,
                    "route_id": info.trip.route_id,
                    "vehicle_id": info.vehicle.id,
                    "latitude": info.position.latitude,
                    "longitude": info.position.longitude,
                    "timestamp": datetime.datetime.fromtimestamp(info.timestamp).strftime("%H:%M:%S") if info.timestamp else "",
                })
        return pd.DataFrame(dados)
    except:
        return pd.DataFrame([])

# Continuação igual ao canvas original...

