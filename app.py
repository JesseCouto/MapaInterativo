import streamlit as st
import pandas as pd
import zipfile
import io
import requests
import pydeck as pdk

st.set_page_config(page_title="GTFS Rio - Análise Completa", layout="wide")

GTFS_URL = "https://dados.mobilidade.rio/gis/gtfs.zip"

@st.cache_data

def carregar_dados_gtfs(url):
    response = requests.get(url)
    if response.status_code != 200:
        st.error("Erro ao baixar GTFS.")
        return None

    z = zipfile.ZipFile(io.BytesIO(response.content))
    dados = {name: pd.read_csv(z.open(name)) for name in z.namelist() if name.endswith('.txt')}
    return dados

gtfs = carregar_dados_gtfs(GTFS_URL)

st.title("🚌 GTFS Rio de Janeiro - Análise e Visualização")

if gtfs:
    routes = gtfs["routes.txt"]
    trips = gtfs["trips.txt"]
    shapes = gtfs["shapes.txt"]
    stops = gtfs["stops.txt"]
    stop_times = gtfs["stop_times.txt"]

    trips_routes = trips.merge(routes, on="route_id")
    linhas = trips_routes[["route_id", "route_short_name", "route_long_name", "trip_id", "shape_id"]].drop_duplicates()
    linhas["linha_nome"] = linhas["route_short_name"].fillna('').astype(str) + " - " + linhas["route_long_name"].fillna('').astype(str)

    st.sidebar.title("🔍 Filtros")
    linha_escolhida = st.sidebar.selectbox("Selecione uma linha:", linhas["linha_nome"].unique())
    linha_dados = linhas[linhas["linha_nome"] == linha_escolhida].iloc[0]
    shape_id = linha_dados["shape_id"]
    trip_id = linha_dados["trip_id"]

    st.subheader(f"👉 Linha Selecionada: {linha_escolhida}")

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

    st.markdown("### 📅 Horários da viagem selecionada")
    st.dataframe(paradas_viagem[["stop_name", "arrival_time", "departure_time"]])

    st.markdown("### 📄 Dados da linha")
    st.dataframe(linhas[linhas["linha_nome"] == linha_escolhida])

    with st.expander("📂 Ver todas as linhas"):
        st.dataframe(linhas.sort_values("linha_nome"))

    with st.expander("🗂 Exportar dados da linha"):
        csv = paradas_viagem.to_csv(index=False).encode("utf-8")
        nome_arquivo = f"paradas_{linha_escolhida.replace('/', '_').replace(' ', '_')}.csv"
        st.download_button("🔽 Baixar CSV de paradas", csv, nome_arquivo, "text/csv")

else:
    st.error("Erro ao carregar dados do GTFS.")
