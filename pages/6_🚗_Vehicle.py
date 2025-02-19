import streamlit as st
from src.pages.vehicle import render_vehicle_page

st.set_page_config(
    page_title='Analyse des Facteurs liés aux Véhicules',
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_vehicle_page()