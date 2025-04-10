
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import LineString
from streamlit_folium import st_folium

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

@st.cache_data
def carregar_dados_gtfs():
    shapes = pd.read_csv("gtfs/shapes.txt")
    routes = pd.read_csv("gtfs/routes.txt")
    trips = pd.read_csv("gtfs/trips.txt")

    # Agrupar pontos por shape_id
    shapes.sort_values(by=["shape_id", "shape_pt_sequence"], inplace=True)
    shape_lines = shapes.groupby("shape_id").apply(
        lambda x: LineString(zip(x["shape_pt_lon"], x["shape_pt_lat"]))
    )
    gdf = gpd.GeoDataFrame(shape_lines, columns=["geometry"], crs="EPSG:4326")
    gdf = gdf.reset_index()

    # Relacionar com trips e routes para obter nome da linha
    gdf = gdf.merge(trips[["shape_id", "route_id"]], on="shape_id")
    gdf = gdf.merge(routes[["route_id", "route_short_name"]], on="route_id")
    gdf = gdf.rename(columns={"route_short_name": "route_name"})
    return gdf

gdf = carregar_dados_gtfs()

linhas = sorted(gdf["route_name"].dropna().unique())
linha_escolhida = st.selectbox("Selecione a linha:", linhas)

mapa = folium.Map(location=[-22.9, -43.2], zoom_start=11)
for _, row in gdf[gdf["route_name"] == linha_escolhida].iterrows():
    folium.PolyLine(locations=[(lat, lon) for lon, lat in row["geometry"].coords],
                    color="blue", weight=4, opacity=0.8).add_to(mapa)

st_data = st_folium(mapa, width=1000)

