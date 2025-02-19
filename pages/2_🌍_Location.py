import streamlit as st
from src.pages.location import render_location_page

st.set_page_config(
    page_title='Analyse Géographique des Accidents',
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_location_page()