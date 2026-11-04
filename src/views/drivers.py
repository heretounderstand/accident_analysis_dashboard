import pandas as pd
import streamlit as st

from .. import charts
from ..config import METRICS
from ..stats import chi2_test, describe_result
from ..ui import pct, callout, chart_card, metric_picker, page_header
from .common import deviation_card, factor_card


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Conducteurs",
        "Profil des conducteurs impliqués (âge, sexe, fatigue, alcoolémie) et lien avec la "
        "gravité des accidents.",
    )

    c = st.columns(4)
    c[0].metric("Tranche d'âge la plus représentée",
                str(fdf["Driver Age Group"].mode().iloc[0]), border=True,
                help="Modalité la plus fréquente (mode), et non une moyenne.")
    c[1].metric("Conducteurs hommes", pct((fdf['Driver Gender'] == 'Homme').mean()), border=True)
    c[2].metric("Conducteurs fatigués", pct(fdf['Driver Fatigue'].mean()), border=True)
    c[3].metric("Alcoolémie ≥ 0,08 g/dL", pct((fdf['Driver Alcohol Level'] >= 0.08).mean()),
                border=True,
                help=f"Alcoolémie moyenne : {fdf['Driver Alcohol Level'].mean():.3f} g/dL. "
                     "0,08 g/dL = seuil légal aux États-Unis et au Royaume-Uni.")

    metric = metric_picker("drv_metric")
    meta = METRICS[metric]

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Driver Age Group", metric, key="drv_age")
        factor_card(fdf, "Fatigue", metric, key="drv_fatigue")
    with right:
        factor_card(fdf, "Driver Gender", metric, key="drv_gender")
        factor_card(fdf, "Alcohol Band", metric,
                    subtitle="Seuils : 0,05 g/dL (Europe) et 0,08 g/dL (États-Unis, Royaume-Uni).",
                    key="drv_alcohol")

    deviation_card(fdf, "Driver Age Group", "Driver Gender", metric,
                   title=f"Âge × sexe : écart à la moyenne ({meta['short']})", key="drv_heat")

    # Contrôle de cohérence : la cause « Alcool au volant » devrait aller avec une alcoolémie élevée
    st.markdown("### Contrôle de cohérence : cause déclarée et alcoolémie")
    share = (
        fdf.groupby("Accident Cause", observed=True)["Alcohol Band"]
        .value_counts(normalize=True).rename("share").reset_index()
    )
    share["Alcohol Band"] = share["Alcohol Band"].astype(str)
    levels = [str(x) for x in fdf["Alcohol Band"].cat.categories]
    fig = charts.stacked_share_bar(share, "Accident Cause", "Alcohol Band", "share", levels,
                                   charts.ORDINAL_BLUE[:3], "Part des conducteurs")
    fig.update_layout(height=320)
    res = chi2_test(fdf, "Accident Cause", "Alcohol Band")
    drunk = share[(share["Accident Cause"] == "Alcool au volant") & (share["Alcohol Band"] == "≥ 0,08")]
    drunk_share = float(drunk["share"].iloc[0]) if not drunk.empty else float("nan")
    overall_high = float((fdf["Driver Alcohol Level"] >= 0.08).mean())
    chart_card(
        "Répartition de l'alcoolémie selon la cause de l'accident",
        fig, subtitle="Si les données étaient cohérentes, la cause « Alcool au volant » serait "
                      "dominée par les alcoolémies ≥ 0,08.",
        test=res,
    )
    if res is not None and res.magnitude == "négligeable":
        callout(
            f"<b>{pct(drunk_share, 0)}</b> des accidents attribués à l'alcool au volant impliquent "
            "un conducteur à 0,08 g/dL ou plus, <b>exactement comme pour les autres causes</b> "
            f"(y compris « Météo »). Au total, {pct(overall_high, 0)} des conducteurs dépassent "
            "0,08 g/dL, une proportion invraisemblable. "
            "La cause déclarée et l'alcoolémie mesurée sont indépendantes : c'est le signe d'un "
            "jeu de données <b>généré aléatoirement</b>, et non une découverte sur la sécurité routière.",
            title="Incohérence détectée", kind="warn",
        )
    else:
        st.caption(describe_result(res))
