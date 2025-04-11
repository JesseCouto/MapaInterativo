import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import pydeck as pdk

st.set_page_config(page_title="GTFS Rio - Análise Completa", layout="wide", page_icon="🚌")

GTFS_URL = "https://dados.mobilidade.rio/gis/gtfs.zip"

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

st.title("🚌 GTFS Rio de Janeiro - Análise e Visualização de Linhas")

# Tenta carregar do link
gtfs = carregar_dados_gtfs(GTFS_URL)

# Caso falhe, permite upload manual
if not gtfs:
    st.warning("⚠️ Não foi possível carregar os dados automaticamente. Faça o upload manual do arquivo GTFS (.zip).")
    uploaded_file = st.file_uploader("📁 Faça o upload do GTFS.zip", type="zip")
    if uploaded_file:
        gtfs = carregar_dados_gtfs_manual(uploaded_file)

if gtfs:
    routes = gtfs["routes.txt"]
    trips = gtfs["trips.txt"]
    shapes = gtfs["shapes.txt"]
    stops = gtfs["stops.txt"]
    stop_times = gtfs["stop_times.txt"]

    trips_routes = trips.merge(routes, on="route_id")
    linhas = trips_routes[["route_id", "route_short_name", "route_long_name", "trip_id", "shape_id"]].drop_duplicates()
    linhas["linha_nome"] = linhas["route_short_name"].fillna('').astype(str) + " - " + linhas["route_long_name"].fillna('').astype(str)

    st.sidebar.title("🔍 Filtros de Busca")
    linha_escolhida = st.sidebar.selectbox("Selecione uma linha de ônibus:", linhas["linha_nome"].unique())
    linha_dados = linhas[linhas["linha_nome"] == linha_escolhida].iloc[0]
    shape_id = linha_dados["shape_id"]
    trip_id = linha_dados["trip_id"]

    st.subheader(f"🛣️ Trajeto da Linha: `{linha_escolhida}`")

    shape_data = shapes[shapes["shape_id"] == shape_id].sort_values("shape_pt_sequence")
    paradas_viagem = stop_times[stop_times["trip_id"] == trip_id].merge(stops, on="stop_id")

    if not shape_data.empty:
        path = shape_data[["shape_pt_lon", "shape_pt_lat"]].values.tolist()
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state=pdk.ViewState(
                latitude=shape_data["shape_pt_lat"].mean(),
                longitude=shape_data["shape_pt_lon"].mean(),
                zoom=12,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    "PathLayer",
                    data=[{"path": path}],
                    get_path="path",
                    get_color=[0, 100, 250],
                    width_scale=5,
                    width_min_pixels=3,
                ),
                pdk.Layer(
                    "ScatterplotLayer",
                    data=paradas_viagem,
                    get_position='[stop_lon, stop_lat]',
                    get_radius=30,
                    get_fill_color=[255, 0, 0, 160],
                )
            ],
        ))

    st.markdown("### 📅 Horários da Viagem")
    st.dataframe(paradas_viagem[["stop_name", "arrival_time", "departure_time"]], use_container_width=True)

    st.markdown("### 📄 Detalhes da Linha")
    st.dataframe(linhas[linhas["linha_nome"] == linha_escolhida], use_container_width=True)

    with st.expander("📋 Ver Todas as Linhas"):
        st.dataframe(linhas.sort_values("linha_nome"), use_container_width=True)

    with st.expander("⬇️ Exportar Dados"):
        csv = paradas_viagem.to_csv(index=False).encode("utf-8")
        nome_arquivo = f"paradas_{linha_escolhida.replace('/', '_').replace(' ', '_')}.csv"
        st.download_button("💾 Baixar CSV de paradas", csv, nome_arquivo, "text/csv")

else:
    st.error("❌ Não foi possível carregar dados do GTFS.")
