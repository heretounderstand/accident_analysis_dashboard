import pandas as pd
import streamlit as st

from ..config import METRICS
from ..ui import pct, metric_picker, page_header
from .common import deviation_card, factor_card


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Environnement",
        "Effet de la météo, de l'état de la chaussée, du type de route, de la visibilité et du "
        "trafic sur la gravité des accidents.",
    )
    n = len(fdf)
    c = st.columns(4)
    c[0].metric("Météo défavorable",
                pct(fdf['Weather Conditions'].isin(['Pluie', 'Neige', 'Brouillard']).mean()),
                border=True, help="Part des accidents par pluie, neige ou brouillard.")
    c[1].metric("Chaussée dégradée",
                pct(fdf['Road Condition'].isin(['Mouillée', 'Verglacée', 'Enneigée']).mean()),
                border=True, help="Part des accidents sur chaussée mouillée, verglacée ou enneigée.")
    c[2].metric("Visibilité < 100 m", pct((fdf['Visibility Level'] < 100).mean()), border=True)
    c[3].metric("Visibilité médiane", f"{fdf['Visibility Level'].median():.0f} m", border=True,
                help=f"Sur {n:,} accidents.".replace(",", " "))

    metric = metric_picker("env_metric")
    meta = METRICS[metric]

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Weather Conditions", metric, key="env_weather")
        factor_card(fdf, "Road Type", metric, key="env_roadtype")
    with right:
        factor_card(fdf, "Road Condition", metric, key="env_roadcond")
        factor_card(fdf, "Visibility Band", metric,
                    subtitle="Visibilité découpée en quintiles (5 groupes de même effectif).",
                    key="env_visibility")

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Traffic Band", metric,
                    subtitle="Volume de trafic découpé en quintiles.", key="env_traffic")
    with right:
        deviation_card(fdf, "Weather Conditions", "Road Condition", metric,
                       title=f"Météo × chaussée : écart à la moyenne ({meta['short']})",
                       key="env_heat")
