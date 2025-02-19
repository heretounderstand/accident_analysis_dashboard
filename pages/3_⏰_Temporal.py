import streamlit as st
from src.pages.temporal import render_temporal_page

st.set_page_config(
    page_title='Analyse Temporelle des Accidents',
    page_icon="⏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_temporal_page()