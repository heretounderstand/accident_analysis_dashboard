"""Point d'entrée : streamlit run app.py"""
from functools import partial

import streamlit as st

from src.config import APP_SUBTITLE, APP_TITLE
from src.data_loader import DataLoadError, load_data
from src.filters import apply_filters, render_sidebar_filters
from src.ui import filter_chips, footer, inject_css
from src.views import (
    data_quality, drivers, environment, financial, geography, overview, temporal, vehicles,
)

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/car_crash:",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

try:
    df = load_data()
except DataLoadError as exc:
    st.error(f"Impossible de charger les données : {exc}")
    st.stop()

with st.sidebar:
    st.markdown(f"#### {APP_TITLE}")
    st.caption(APP_SUBTITLE)

filters = render_sidebar_filters(df)
fdf = apply_filters(df, filters)


def _page(module, title: str, icon: str, url: str, default: bool = False) -> st.Page:
    return st.Page(partial(module.render, df, fdf), title=title, icon=icon, url_path=url,
                   default=default)


pages = {
    "Synthèse": [
        _page(overview, "Vue d'ensemble", ":material/dashboard:", "overview", default=True),
    ],
    "Analyses": [
        _page(geography, "Géographie", ":material/public:", "geographie"),
        _page(temporal, "Évolution temporelle", ":material/calendar_month:", "temporel"),
        _page(environment, "Environnement", ":material/partly_cloudy_day:", "environnement"),
        _page(drivers, "Conducteurs", ":material/person:", "conducteurs"),
        _page(vehicles, "Véhicules", ":material/directions_car:", "vehicules"),
        _page(financial, "Impact financier", ":material/payments:", "finances"),
    ],
    "Méthodologie": [
        _page(data_quality, "Qualité des données", ":material/fact_check:", "qualite"),
    ],
}
nav = st.navigation(pages)

st.session_state["_filter_summary"] = (filters.active(df), len(fdf), len(df))
if fdf.empty:
    filter_chips(*st.session_state["_filter_summary"])
    st.warning("Aucun accident ne correspond aux filtres sélectionnés. Élargissez la sélection.",
               icon=":material/filter_alt_off:")
    st.stop()

nav.run()
footer()
