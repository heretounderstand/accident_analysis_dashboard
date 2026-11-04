import pandas as pd
import streamlit as st

from .. import charts
from ..config import LABELS, METRICS, RISK_FACTORS
from ..stats import pct_change, rank_factors
from ..ui import fr, pct, callout, chart_card, fmt_int, fmt_money, metric_picker, page_header


def filter_key() -> str:
    """Clé de cache stable représentant la sélection courante."""
    return repr(st.session_state.get("_filter_summary"))


@st.cache_data(show_spinner="Calcul des tests statistiques…")
def cached_ranking(_df: pd.DataFrame, key: str, metric: str) -> pd.DataFrame:
    return rank_factors(_df, RISK_FACTORS, metric)


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Synthèse",
        "Vue d'ensemble",
        "Les chiffres clés de la sélection, leur évolution et les facteurs qui influencent "
        "réellement la gravité des accidents, testés statistiquement.",
    )

    n = len(fdf)
    fatalities = fdf["Number of Fatalities"].sum()
    injuries = fdf["Number of Injuries"].sum()
    last_year = int(fdf["Year"].max())
    prev_year = last_year - 1
    n_last = int((fdf["Year"] == last_year).sum())
    n_prev = int((fdf["Year"] == prev_year).sum())
    yoy = pct_change(n_last, n_prev)

    yearly = fdf.groupby("Year").size()
    c = st.columns(3)
    c[0].metric(
        f"Accidents en {last_year}", fmt_int(n_last),
        delta=f"{pct(yoy, sign=True)} vs {prev_year}" if yoy is not None else None,
        delta_color="inverse", border=True,
        help=f"{fmt_int(n)} accidents sur toute la période sélectionnée.",
    )
    c[1].metric(
        "Décès", fmt_int(fatalities), border=True,
        delta=f"{fatalities / n:.2f} par accident".replace(".", ","), delta_color="off",
        delta_arrow="off",
        chart_data=fdf.groupby("Year")["Number of Fatalities"].sum().tolist(),
    )
    c[2].metric(
        "Blessés", fmt_int(injuries), border=True,
        delta=f"{injuries / n:.2f} par accident".replace(".", ","), delta_color="off",
        delta_arrow="off",
        chart_data=fdf.groupby("Year")["Number of Injuries"].sum().tolist(),
    )
    c = st.columns(3)
    c[0].metric("Accidents mortels", pct(fdf['Is Fatal'].mean()), border=True,
                help="Part des accidents ayant causé au moins un décès.")
    c[1].metric("Délai moyen d'intervention",
                f"{fdf['Emergency Response Time'].mean():.1f} min".replace(".", ","), border=True,
                help="Temps moyen entre l'accident et l'arrivée des secours.")
    c[2].metric("Coût total (médical + économique)", fmt_money(fdf["Total Cost"].sum()), border=True,
                delta=f"{fmt_money(fdf['Total Cost'].mean())} par accident", delta_color="off",
                delta_arrow="off")

    left, right = st.columns([3, 2])
    with left:
        yearly_df = yearly.rename("Accidents").reset_index()
        chart_card(
            "Nombre d'accidents par année", charts.line_chart(yearly_df, "Year", "Accidents", "Accidents"),
            subtitle="Axe partant de zéro pour ne pas exagérer les variations.",
            table=yearly_df.rename(columns={"Year": "Année"}),
        )
    with right:
        sev = fdf["Accident Severity"].value_counts().reindex(
            fdf["Accident Severity"].cat.categories).fillna(0).rename_axis("Gravité").reset_index(name="Accidents")
        sev["Part"] = sev["Accidents"] / sev["Accidents"].sum()
        fig = charts.bar_chart(sev, "Gravité", "Part", "Part des accidents", fmt=".0%", horizontal=True)
        fig.update_layout(height=charts.CHART_HEIGHT)
        chart_card("Répartition par gravité déclarée", fig, subtitle="Part des accidents de la sélection.",
                   table=sev.assign(Part=sev["Part"].map("{:.1%}".format)))

    st.markdown("### Quels facteurs influencent la gravité ?")
    st.markdown(
        "Pour chaque facteur, on teste si l'indicateur choisi diffère entre ses modalités "
        "(Kruskal-Wallis, ou Khi² pour la part d'accidents mortels), avec une correction de "
        "Bonferroni pour les tests multiples. La **taille d'effet** indique si la différence "
        "compte vraiment : avec 100 000 observations, un écart minuscule peut être "
        "« significatif » sans avoir d'intérêt pratique."
    )
    metric = metric_picker("overview_metric")
    ranking = cached_ranking(fdf, filter_key(), metric)
    if ranking.empty:
        st.info("Pas assez de données pour tester les facteurs.")
        return

    n_sig = int(ranking["significant"].sum())
    n_meaningful = int((ranking["magnitude"] != "négligeable").sum())
    top = ranking.iloc[0]
    if n_meaningful == 0:
        sig_txt = ("aucun ne présente de différence statistiquement significative"
                   if n_sig == 0 else
                   f"{n_sig} présente{'nt' if n_sig > 1 else ''} une différence statistiquement "
                   "significative, mais")
        callout(
            f"Sur {len(ranking)} facteurs testés, <b>{sig_txt}</b> et <b>aucun</b> n'a d'effet "
            f"au-delà du seuil "
            f"« négligeable » sur <b>{METRICS[metric]['label'].lower()}</b>. Le facteur le plus "
            f"associé ({LABELS.get(top['factor'], top['factor'])}) a une taille d'effet "
            f"{top['effect_name']} = {fr(top['effect'], '.5f')}. Dans ces données, la gravité d'un accident "
            "ne s'explique par aucune des variables disponibles.",
            title="Résultat clé", kind="warn",
        )
    else:
        callout(
            f"{n_meaningful} facteur(s) ont un effet non négligeable sur "
            f"<b>{METRICS[metric]['label'].lower()}</b>, le plus important étant "
            f"<b>{LABELS.get(top['factor'], top['factor'])}</b> ({top['effect_name']} = {fr(top['effect'], '.3f')}).",
            title="Résultat clé",
        )

    table = ranking.assign(
        Facteur=ranking["factor"].map(lambda f: LABELS.get(f, f)),
        Test=ranking["test"],
        **{"Taille d'effet": ranking["effect"].round(5),
           "p ajustée": ranking["p_adj"].map(lambda p: f"{p:.3g}"),
           "Significatif": ranking["significant"].map({True: "Oui", False: "Non"}),
           "Effet": ranking["magnitude"]},
    )[["Facteur", "Test", "Taille d'effet", "p ajustée", "Significatif", "Effet"]]
    chart_card(
        f"Taille d'effet de chaque facteur sur : {METRICS[metric]['label'].lower()}",
        charts.effect_size_chart(ranking, LABELS),
        subtitle="Bleu : significatif après correction de Bonferroni · gris : non significatif. "
                 "Des barres quasi invisibles signifient un effet quasi nul.",
        table=table,
    )
