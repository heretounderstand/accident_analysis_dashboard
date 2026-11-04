import pandas as pd
import streamlit as st
from statsmodels.tsa.seasonal import STL

from .. import charts
from ..config import METRICS
from ..stats import Z_95, pct_change
from ..ui import pct, callout, chart_card, fmt_int, metric_picker, page_header
from .common import deviation_card, factor_card


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Évolution temporelle",
        "Tendance de long terme, saisonnalité et rythmes hebdomadaires. La dernière année de la "
        "sélection est comparée à la précédente.",
    )

    last_year = int(fdf["Year"].max())
    prev_year = last_year - 1
    cur = fdf[fdf["Year"] == last_year]
    prev = fdf[fdf["Year"] == prev_year]

    def delta(a: float, b: float) -> str | None:
        v = pct_change(a, b)
        return None if v is None else f"{pct(v, sign=True)} vs {prev_year}"

    c = st.columns(4)
    c[0].metric(f"Accidents {last_year}", fmt_int(len(cur)), delta(len(cur), len(prev)),
                delta_color="inverse", border=True)
    c[1].metric(f"Décès {last_year}", fmt_int(cur["Number of Fatalities"].sum()),
                delta(cur["Number of Fatalities"].sum(), prev["Number of Fatalities"].sum()),
                delta_color="inverse", border=True)
    c[2].metric(f"Blessés {last_year}", fmt_int(cur["Number of Injuries"].sum()),
                delta(cur["Number of Injuries"].sum(), prev["Number of Injuries"].sum()),
                delta_color="inverse", border=True)
    rt_cur, rt_prev = cur["Emergency Response Time"].mean(), prev["Emergency Response Time"].mean()
    c[3].metric(f"Délai d'intervention {last_year}", f"{rt_cur:.1f} min".replace(".", ","),
                delta(rt_cur, rt_prev), delta_color="inverse", border=True)
    if prev.empty:
        st.caption(f"Pas de données pour {prev_year} dans la sélection : variations non calculées.")

    metric = metric_picker("time_metric")
    meta = METRICS[metric]

    yearly = fdf.groupby("Year")[metric].agg(["mean", "std", "count"]).reset_index()
    yearly["ci"] = Z_95 * yearly["std"] / yearly["count"] ** 0.5
    yearly["low"], yearly["high"] = yearly["mean"] - yearly["ci"], yearly["mean"] + yearly["ci"]
    chart_card(
        f"{meta['label']} par année",
        charts.line_chart(yearly, "Year", "mean", meta["short"], fmt=meta["fmt"],
                          band=("low", "high")),
        subtitle="Bande = intervalle de confiance à 95 %. Une courbe plate dans la bande = pas de tendance.",
        table=yearly.rename(columns={"Year": "Année", "mean": meta["short"], "count": "Accidents"})
        [["Année", meta["short"], "Accidents"]].round(4),
    )

    # Décomposition STL sur le nombre mensuel d'accidents
    monthly = fdf.groupby("Date").size().asfreq("MS", fill_value=0)
    st.markdown("### Tendance et saisonnalité")
    if len(monthly) >= 36:
        res = STL(monthly.astype(float), period=12, robust=True).fit()
        seasonal_amp = res.seasonal.max() - res.seasonal.min()
        strength = max(0.0, 1 - res.resid.var() / (res.seasonal + res.resid).var())
        callout(
            f"Amplitude saisonnière : <b>{seasonal_amp:.0f} accidents</b> par mois, pour une "
            f"moyenne de {monthly.mean():.0f}. Force de la saisonnalité "
            f"(Wang et al.) : <b>{strength:.2f}</b> sur 1 "
            f"({'marquée' if strength > 0.4 else 'faible' if strength > 0.15 else 'quasi nulle'}).",
        )
        chart_card(
            "Décomposition STL du nombre mensuel d'accidents",
            charts.decomposition_chart(monthly.index, monthly, res.trend, res.seasonal, res.resid),
            subtitle="Série = tendance + saisonnalité + résidus. Décomposition robuste aux valeurs extrêmes.",
        )
    else:
        st.info("Il faut au moins 3 années de données pour estimer la saisonnalité. Élargissez la période.")

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Month", metric, key="time_month")
    with right:
        factor_card(fdf, "Day of Week", metric, key="time_dow")
        factor_card(fdf, "Time of Day", metric, key="time_tod")

    deviation_card(fdf, "Day of Week", "Time of Day", metric,
                   title=f"Jour × moment de la journée : écart à la moyenne ({meta['short']})",
                   key="time_heat")
