import streamlit as st
from src.pages.financial import render_financial_page

st.set_page_config(
    page_title='Analyse de l\'Impact Financier',
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded"
)

render_financial_page()