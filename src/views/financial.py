import pandas as pd
import streamlit as st

from .. import charts
from ..stats import Z_95, pct_change
from ..ui import pct, callout, chart_card, fmt_money, page_header
from .common import factor_card

COST = "Total Cost"


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Analyses",
        "Impact financier",
        "Coûts médicaux et pertes économiques. On compare les coûts moyens par accident, car "
        "les totaux augmentent mécaniquement avec le nombre d'accidents.",
    )

    last_year = int(fdf["Year"].max())
    cur, prev = fdf[fdf["Year"] == last_year], fdf[fdf["Year"] == last_year - 1]
    yoy = pct_change(cur[COST].mean(), prev[COST].mean())

    c = st.columns(4)
    c[0].metric("Coûts médicaux", fmt_money(fdf["Medical Cost"].sum()), border=True,
                delta=f"{fmt_money(fdf['Medical Cost'].mean())} par accident", delta_color="off",
                delta_arrow="off")
    c[1].metric("Pertes économiques", fmt_money(fdf["Economic Loss"].sum()), border=True,
                delta=f"{fmt_money(fdf['Economic Loss'].mean())} par accident", delta_color="off",
                delta_arrow="off")
    c[2].metric(f"Coût moyen par accident ({last_year})", fmt_money(cur[COST].mean()) if len(cur) else "–",
                delta=f"{pct(yoy, sign=True)} vs {last_year - 1}" if yoy is not None else None,
                delta_color="inverse", border=True,
                help="Coût médical + perte économique, moyenne par accident, comparé à l'année précédente.")
    c[3].metric("Déclarations d'assurance", f"{fdf['Insurance Claims'].mean():.1f} / accident".replace(".", ","),
                border=True, help="Nombre moyen de déclarations d'assurance par accident (ce n'est pas un montant).")

    yearly = fdf.groupby("Year")[COST].agg(["mean", "std", "count"]).reset_index()
    yearly["ci"] = Z_95 * yearly["std"] / yearly["count"] ** 0.5
    yearly["low"], yearly["high"] = yearly["mean"] - yearly["ci"], yearly["mean"] + yearly["ci"]
    chart_card(
        "Coût moyen par accident, par année",
        charts.line_chart(yearly, "Year", "mean", "Coût moyen ($)", fmt=",.0f", band=("low", "high"), y_from_zero=False),
        subtitle="Bande = intervalle de confiance à 95 %.",
        table=yearly.rename(columns={"Year": "Année", "mean": "Coût moyen", "count": "Accidents"})
        [["Année", "Coût moyen", "Accidents"]].round(0),
    )

    left, right = st.columns(2)
    with left:
        factor_card(fdf, "Accident Severity", COST,
                    subtitle="On attendrait un coût nettement plus élevé pour les accidents graves.",
                    key="fin_sev")
        factor_card(fdf, "Density Band", COST,
                    subtitle="Densité de population découpée en quintiles.", key="fin_density")
    with right:
        chart_card(
            "Distribution du coût total par accident",
            charts.histogram(fdf[COST], "Coût total par accident ($)", nbins=40),
            subtitle="Forme de la distribution : symétrique, asymétrique, valeurs extrêmes ?",
        )
        claims = fdf["Insurance Claims"].value_counts().sort_index().rename_axis("Déclarations") \
            .reset_index(name="Accidents")
        chart_card(
            "Nombre de déclarations d'assurance par accident",
            charts.bar_chart(claims, "Déclarations", "Accidents", "Accidents"),
            table=claims,
        )

    sev = fdf.groupby("Accident Severity", observed=True)[COST].mean()
    if len(sev) >= 2 and sev.min() > 0 and sev.max() / sev.min() - 1 < 0.05:
        callout(
            "Le coût moyen d'un accident <b>grave</b> est pratiquement identique à celui d'un "
            "accident <b>mineur</b> (écart < 5 %). Dans la réalité, la gravité est le premier "
            "déterminant du coût : cette absence de lien confirme que les montants du jeu de "
            "données sont simulés indépendamment des autres variables.",
            title="À interpréter avec prudence", kind="warn",
        )

    with st.expander("Tableau détaillé : gravité × continent"):
        detail = (
            fdf.groupby(["Accident Severity", "Continent"], observed=True)
            .agg(Accidents=(COST, "size"),
                 **{"Coût médical moyen": ("Medical Cost", "mean"),
                    "Perte économique moyenne": ("Economic Loss", "mean"),
                    "Coût total": (COST, "sum"),
                    "Déclarations / accident": ("Insurance Claims", "mean")})
            .reset_index().rename(columns={"Accident Severity": "Gravité"})
        )
        st.dataframe(detail, hide_index=True, column_config={
            "Coût médical moyen": st.column_config.NumberColumn(format="%.0f $"),
            "Perte économique moyenne": st.column_config.NumberColumn(format="%.0f $"),
            "Coût total": st.column_config.NumberColumn(format="compact"),
            "Déclarations / accident": st.column_config.NumberColumn(format="%.2f"),
        })
        st.download_button("Télécharger (CSV)", detail.to_csv(index=False).encode("utf-8"),
                           "analyse_financiere.csv", "text/csv", icon=":material/download:")
