
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from zipfile import ZipFile
from pathlib import Path

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

gtfs_zip_path = Path("GTFS/gtfs_rio-de-janeiro.zip")

if not gtfs_zip_path.exists():
    st.error("Arquivo GTFS não encontrado. Verifique se foi incluído corretamente no repositório.")
else:
    with ZipFile(gtfs_zip_path, "r") as z:
        z.extractall("gtfs_data")
    st.success("Dados carregados com sucesso.")

    shapes = pd.read_csv("gtfs_data/shapes.txt")
    routes = pd.read_csv("gtfs_data/routes.txt")
    trips = pd.read_csv("gtfs_data/trips.txt")

    # Merge para obter os nomes das rotas
    trips_routes = trips.merge(routes, on="route_id")
    shapes_trips = shapes.merge(trips_routes, on="shape_id")

    # Converter para GeoDataFrame
    shapes_trips = shapes_trips.sort_values(by=["shape_id", "shape_pt_sequence"])
    shapes_trips["geometry"] = shapes_trips.groupby("shape_id").apply(
        lambda x: gpd.points_from_xy(x["shape_pt_lon"], x["shape_pt_lat"]).tolist()
    ).explode().reset_index(drop=True)
    gdf = gpd.GeoDataFrame(shapes_trips, geometry=gpd.points_from_xy(shapes_trips["shape_pt_lon"], shapes_trips["shape_pt_lat"]), crs="EPSG:4326")

    linhas = sorted(gdf["route_long_name"].dropna().unique())
    linha_escolhida = st.selectbox("Escolha a linha", linhas)

    gdf_linha = gdf[gdf["route_long_name"] == linha_escolhida]

    m = folium.Map(location=[-22.9, -43.2], zoom_start=11)

    for shape_id, group in gdf_linha.groupby("shape_id"):
        coords = list(zip(group["shape_pt_lat"], group["shape_pt_lon"]))
        folium.PolyLine(locations=coords, color="blue", weight=3).add_to(m)

    folium_static(m)


