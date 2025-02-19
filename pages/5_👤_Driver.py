import streamlit as st
from src.pages.driver import render_driver_page

st.set_page_config(
    page_title='Analyse des Facteurs liés aux Conducteurs',
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_driver_page()