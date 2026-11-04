import pandas as pd
import streamlit as st

from .. import charts
from ..config import COUNTRY_ISO3, METRICS
from ..stats import group_summary
from ..ui import fr, pct, callout, chart_card, fmt_int, fmt_money, metric_picker, page_header
from .common import deviation_card, factor_card


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Géographie",
        "Comparaison des pays et des milieux urbain et rural. Les indicateurs sont rapportés "
        "au nombre d'accidents : comparer des totaux reviendrait à comparer la taille des échantillons.",
    )
    callout(
        "Le champ « Region » de la source est incohérent avec le pays (un même pays apparaît sur "
        "les cinq continents). Le continent est donc <b>recalculé à partir du pays</b>. "
        "Détails dans la page Qualité des données.",
        kind="warn",
    )

    metric = metric_picker("geo_metric")
    meta = METRICS[metric]

    by_country = group_summary(fdf, "Country", metric)
    by_country["iso"] = by_country["Country"].astype(str).map(COUNTRY_ISO3)
    top = by_country.sort_values("mean", ascending=False).iloc[0]
    bottom = by_country.sort_values("mean").iloc[0]
    spread = top["mean"] / bottom["mean"] - 1 if bottom["mean"] else 0

    c = st.columns(3)
    c[0].metric("Pays représentés", str(by_country["Country"].nunique()), border=True)
    c[1].metric("Pays le plus élevé", str(top["Country"]), border=True,
                delta=f"{fr(top['mean'], meta['fmt'])} · {meta['short']}", delta_color="off",
                delta_arrow="off")
    c[2].metric("Écart max entre pays", f"{pct(spread, sign=True)}", border=True,
                help=f"Écart relatif entre {top['Country']} et {bottom['Country']}.")

    chart_card(
        f"{meta['label']} par pays",
        charts.choropleth(by_country, "iso", "mean", "Country", meta["short"], meta["fmt"]),
        subtitle="Attention : la carte étire visuellement les écarts, voir le graphique ci-dessous "
                 "pour l'incertitude.",
    )

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Country", metric, sort=True, key="geo_country")
    with right:
        factor_card(fdf, "Continent", metric, sort=True, key="geo_continent")
        factor_card(fdf, "Urban/Rural", metric, key="geo_urban")

    deviation_card(
        fdf, "Country", "Time of Day", metric,
        title=f"Pays × moment de la journée : écart à la moyenne ({meta['short']})",
        key="geo_heat",
    )

    with st.expander("Tableau récapitulatif par pays"):
        recap = fdf.groupby("Country", observed=True).agg(
            Accidents=("Year", "size"), Décès=("Number of Fatalities", "sum"),
            Blessés=("Number of Injuries", "sum"), Coût=("Total Cost", "sum"),
            Délai=("Emergency Response Time", "mean"),
        ).reset_index().rename(columns={"Country": "Pays"})
        recap["Décès / accident"] = recap["Décès"] / recap["Accidents"]
        recap["Part des décès"] = recap["Décès"] / recap["Décès"].sum()
        st.dataframe(
            recap, hide_index=True,
            column_config={
                "Coût": st.column_config.NumberColumn("Coût total ($)", format="compact"),
                "Délai": st.column_config.NumberColumn("Délai moyen (min)", format="%.1f"),
                "Décès / accident": st.column_config.NumberColumn(format="%.3f"),
                "Part des décès": st.column_config.ProgressColumn(format="percent", min_value=0,
                                                                  max_value=float(recap["Part des décès"].max())),
            },
        )
        st.download_button("Télécharger (CSV)", recap.to_csv(index=False).encode("utf-8"),
                           "recap_pays.csv", "text/csv", icon=":material/download:")
        st.caption(f"Total : {fmt_int(recap['Accidents'].sum())} accidents · "
                   f"{fmt_money(recap['Coût'].sum())}.")
