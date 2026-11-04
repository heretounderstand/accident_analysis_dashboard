import pandas as pd
import streamlit as st

from .. import charts
from ..config import METRICS
from ..ui import pct, chart_card, metric_picker, page_header
from .common import deviation_card, factor_card


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Véhicules",
        "État technique des véhicules, nombre de véhicules impliqués et limitation de vitesse "
        "sur le lieu de l'accident.",
    )

    c = st.columns(4)
    c[0].metric("Limitation moyenne", f"{fdf['Speed Limit'].mean():.0f} km/h", border=True)
    c[1].metric("Véhicules en mauvais état", pct((fdf['Vehicle Condition'] == 'Mauvais').mean()),
                border=True)
    c[2].metric("Cause : excès de vitesse", pct((fdf['Accident Cause'] == 'Excès de vitesse').mean()),
                border=True)
    c[3].metric("Cause : défaillance mécanique",
                pct((fdf['Accident Cause'] == 'Défaillance mécanique').mean()), border=True)

    metric = metric_picker("veh_metric")
    meta = METRICS[metric]

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Vehicle Condition", metric, key="veh_cond")
        factor_card(fdf, "Number of Vehicles Involved", metric, key="veh_n")
    with right:
        factor_card(fdf, "Speed Band", metric, key="veh_speed")
        factor_card(fdf, "Accident Cause", metric, sort=True, key="veh_cause")

    left, right = st.columns(2)
    with left:
        chart_card(
            "Distribution des limitations de vitesse",
            charts.histogram(fdf["Speed Limit"], "Limitation de vitesse (km/h)", nbins=30),
            subtitle="Nombre d'accidents par tranche de limitation.",
        )
    with right:
        deviation_card(fdf, "Vehicle Condition", "Speed Band", metric,
                       title=f"État du véhicule × vitesse : écart à la moyenne ({meta['short']})",
                       key="veh_heat")
