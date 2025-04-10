
import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import requests
import zipfile
from io import BytesIO
from pathlib import Path  # Correção incluída aqui

st.set_page_config(layout="wide")
st.title("Itinerários de Ônibus do Município do RJ")

@st.cache_data(show_spinner="Baixando e processando dados GTFS...")
def baixar_e_extrair_arquivos_gtfs():
    url = "https://www.data.rio/datasets/8ffe62ad3b2f42e49814bf941654ea6c_0.zip"
    try:
        response = requests.get(url)
        response.raise_for_status()
        if not Path("gtfs_data").exists():
            Path("gtfs_data").mkdir()
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            z.extractall("gtfs_data")
        return "gtfs_data"
    except Exception as e:
        st.warning("Não foi possível baixar os dados atualizados. Usando cache local se disponível.")
        return "gtfs_data" if Path("gtfs_data").exists() else None

def carregar_itinerarios(gtfs_path):
    if gtfs_path is None:
        return None

    try:
        shapes = pd.read_csv(f"{gtfs_path}/shapes.txt")
        routes = pd.read_csv(f"{gtfs_path}/routes.txt")
        
        gdfs = []
        for shape_id, group in shapes.groupby("shape_id"):
            line = group.sort_values("shape_pt_sequence")
            geometry = gpd.points_from_xy(line.shape_pt_lon, line.shape_pt_lat).to_list()
            gdf = gpd.GeoDataFrame({
                "shape_id": [shape_id],
                "geometry": [gpd.GeoSeries(geometry).unary_union]
            }, geometry="geometry", crs="EPSG:4326")
            gdfs.append(gdf)
        gdf_final = pd.concat(gdfs, ignore_index=True)

        # Juntar com nomes de linhas
        gdf_final = gdf_final.merge(routes[["route_id", "route_short_name"]], left_on="shape_id", right_on="route_id", how="left")
        gdf_final = gdf_final.rename(columns={"route_short_name": "route_name"})
        return gdf_final

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

gtfs_path = baixar_e_extrair_arquivos_gtfs()
gdf = carregar_itinerarios(gtfs_path)

if gdf is not None:
    linhas = sorted(gdf["route_name"].dropna().unique())
    linhas_selecionadas = st.multiselect("Selecione uma ou mais linhas de ônibus", linhas)

    m = folium.Map(location=[-22.9, -43.2], zoom_start=11)
    for linha in linhas_selecionadas:
        subset = gdf[gdf["route_name"] == linha]
        for _, row in subset.iterrows():
            folium.PolyLine(locations=[(p.y, p.x) for p in row["geometry"].geoms if hasattr(row["geometry"], "geoms") else row["geometry"].coords],
                            color="blue", weight=3, opacity=0.8).add_to(m)

    st_folium(m, width=1000, height=600)
else:
    st.error("Não foi possível carregar os itinerários.")
