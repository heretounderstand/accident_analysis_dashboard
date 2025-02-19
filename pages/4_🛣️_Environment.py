import streamlit as st
from src.pages.environment import render_environment_page

st.set_page_config(
    page_title='Analyse Environnementale des Accidents',
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_environment_page()