import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .. import charts
from ..config import LABELS, NUMERIC_COLUMNS, VALID_RANGES
from ..stats import chi2_test, uniformity_test
from ..ui import callout, chart_card, fmt_int, page_header

CATEGORICAL = [
    "Country", "Region", "Month", "Day of Week", "Time of Day", "Urban/Rural", "Road Type",
    "Weather Conditions", "Driver Age Group", "Driver Gender", "Vehicle Condition",
    "Accident Severity", "Road Condition", "Accident Cause",
]


@st.cache_data(show_spinner="Audit des données…")
def audit(_df: pd.DataFrame, n_rows: int) -> dict:
    df = _df
    checks = []
    n_missing = int(df[NUMERIC_COLUMNS + CATEGORICAL].isna().sum().sum())
    checks.append(("Valeurs manquantes", fmt_int(n_missing), n_missing == 0))
    n_dup = int(df.duplicated(subset=NUMERIC_COLUMNS + CATEGORICAL).sum())
    checks.append(("Lignes dupliquées", fmt_int(n_dup), n_dup == 0))
    out_of_range = 0
    for col, (lo, hi) in VALID_RANGES.items():
        s = df[col]
        out_of_range += int(((s < lo) | ((s > hi) if hi is not None else False)).sum())
    checks.append(("Valeurs hors plage plausible", fmt_int(out_of_range), out_of_range == 0))

    # Incohérences logiques
    region = chi2_test(df, "Country", "Region")
    sev_zero = df.groupby("Accident Severity", observed=True)["Number of Fatalities"].apply(
        lambda s: (s == 0).mean())
    severe_no_victim = int(((df["Accident Severity"] == "Grave") & (df["Victims"] == 0)).sum())
    minor_4_deaths = int(((df["Accident Severity"] == "Mineure") & (df["Number of Fatalities"] >= 4)).sum())
    checks.append(("Pays ↔ région (V de Cramér)", f"{region.effect:.3f}", region.effect > 0.9))
    checks.append(("Accidents « mineurs » avec ≥ 4 décès", fmt_int(minor_4_deaths), minor_4_deaths == 0))
    checks.append(("Accidents « graves » sans aucune victime", fmt_int(severe_no_victim), severe_no_victim == 0))

    # Uniformité des distributions
    uni = []
    for col in CATEGORICAL:
        chi2, p = uniformity_test(df[col])
        counts = df[col].value_counts()
        uni.append({"Variable": LABELS.get(col, col), "Modalités": len(counts),
                    "Écart max à l'uniforme": counts.max() / counts.mean() - 1,
                    "p (Khi² d'uniformité)": p})
    uni = pd.DataFrame(uni)

    num = df[NUMERIC_COLUMNS].drop(columns=["Year"])
    corr = num.corr()
    corr.index = corr.columns = [LABELS.get(c, c) for c in corr.columns]
    off_diag = corr.where(~np.eye(len(corr), dtype=bool)).abs()

    crosstab = pd.crosstab(df["Country"], df["Region"], normalize="index")
    return dict(checks=checks, region=region, sev_zero=sev_zero, uni=uni, corr=corr,
                max_corr=float(off_diag.max().max()), crosstab=crosstab)


def render(df: pd.DataFrame, fdf: pd.DataFrame) -> None:
    page_header(
        "Méthodologie",
        "Qualité des données",
        "Audit du jeu de données complet (indépendamment des filtres) : complétude, cohérence "
        "logique et plausibilité des distributions. Cette étape conditionne la portée de toutes "
        "les analyses du tableau de bord.",
    )
    a = audit(df, len(df))

    callout(
        "Le fichier est <b>propre sur la forme</b> (aucune valeur manquante ni doublon), mais "
        "<b>peu plausible sur le fond</b> : toutes les variables suivent des lois quasi uniformes, "
        f"aucune paire de variables numériques n'est corrélée (|r| max = {a['max_corr']:.3f}), le pays "
        "ne détermine pas la région et la gravité déclarée n'a aucun lien avec le nombre de décès. "
        "Ce sont les signes d'un <b>jeu de données synthétique</b>, généré variable par variable. "
        "Le tableau de bord reste utile comme démonstration de méthode, mais ses résultats ne "
        "doivent pas être lus comme des constats sur la sécurité routière réelle.",
        title="Verdict", kind="warn",
    )

    st.markdown("### Contrôles")
    checks = pd.DataFrame(a["checks"], columns=["Contrôle", "Résultat", "OK"])
    checks["Statut"] = checks["OK"].map({True: "✅ Conforme", False: "⚠️ Anomalie"})
    st.dataframe(checks[["Contrôle", "Résultat", "Statut"]], hide_index=True)

    left, right = st.columns(2)
    with left:
        ct = a["crosstab"]
        fig = go.Figure(go.Heatmap(
            z=ct.to_numpy(), x=[str(c) for c in ct.columns], y=[str(i) for i in ct.index],
            colorscale=[[i / (len(charts.SEQ_BLUE) - 1), c] for i, c in enumerate(charts.SEQ_BLUE)],
            zmin=0, zmax=1, xgap=2, ygap=2, texttemplate="%{z:.0%}", textfont=dict(size=10),
            colorbar=dict(tickformat=".0%", thickness=10, outlinewidth=0),
            hovertemplate="%{y} → %{x} : %{z:.1%}<extra></extra>",
        ))
        fig.update_layout(height=440, yaxis=dict(autorange="reversed", showgrid=False),
                          xaxis=dict(showgrid=False, title="Région (source)"))
        chart_card(
            "Pays × région déclarée",
            fig,
            subtitle="Chaque pays devrait appartenir à 100 % à une seule région. Ici, chaque pays "
                     "est réparti à ~20 % sur toutes les régions.",
        )
    with right:
        sz = a["sev_zero"].rename("share").rename_axis("Gravité").reset_index()
        fig = charts.bar_chart(sz, "Gravité", "share", "Part sans aucun décès", fmt=".0%")
        fig.update_layout(height=440, yaxis=dict(range=[0, 1]))
        chart_card(
            "Part des accidents sans décès, par gravité déclarée",
            fig,
            subtitle="Attendu : forte pour « Mineure », faible pour « Grave ». Observé : identique.",
        )

    chart_card(
        "Corrélations entre variables numériques (Pearson)",
        charts.correlation_heatmap(a["corr"]),
        subtitle="Dans des données réelles, on attendrait par ex. un lien entre décès et coût "
                 "médical, ou entre vitesse et gravité. Ici toutes les corrélations sont ≈ 0.",
    )

    st.markdown("### Uniformité des distributions")
    st.markdown(
        "Le test du Khi² vérifie si les modalités sont équiprobables. Des données réelles sont "
        "rarement uniformes (il y a plus d'accidents de jour que de nuit, plus en ville, etc.)."
    )
    uni = a["uni"]
    st.dataframe(uni, hide_index=True, column_config={
        "Écart max à l'uniforme": st.column_config.NumberColumn(format="percent"),
        "p (Khi² d'uniformité)": st.column_config.NumberColumn(format="%.3f"),
    })

    st.markdown("### Méthodologie du tableau de bord")
    st.markdown(
        """
- **Indicateurs rapportés à l'accident.** Les groupes n'ont pas tous la même taille : on compare
  des moyennes (décès par accident, part d'accidents mortels, coût moyen), jamais des totaux bruts.
- **Incertitude visible.** Chaque moyenne est accompagnée de son intervalle de confiance à 95 %
  (approximation normale, justifiée par la taille des groupes).
- **Tests adaptés.** Kruskal-Wallis (non paramétrique, sans hypothèse de normalité) pour les
  indicateurs numériques, Khi² d'indépendance pour les proportions, avec une correction de
  Bonferroni lorsque plusieurs facteurs sont testés en même temps.
- **Taille d'effet avant significativité.** Avec plus de 100 000 lignes, des écarts infimes
  deviennent « significatifs ». On rapporte donc ε² (Kruskal-Wallis) ou le V de Cramér (Khi²),
  avec les seuils usuels : négligeable < 0,01 / 0,10.
- **Variables continues découpées en quintiles** (visibilité, trafic, densité) pour obtenir
  des groupes de même effectif. L'alcoolémie est découpée selon les seuils légaux (0,05 et 0,08 g/dL).
- **Données corrigées.** Le continent est recalculé à partir du pays, car le champ « Region »
  de la source est incohérent. Les modalités sont traduites en français et ordonnées logiquement.
- **Saisonnalité** estimée par une décomposition STL robuste sur le nombre mensuel d'accidents.
        """
    )

    st.markdown("### Exporter la sélection")
    st.caption(f"{fmt_int(len(fdf))} accidents correspondent aux filtres actuels.")
    export_cols = [c for c in df.columns if c not in {"Date"}]
    st.download_button(
        "Télécharger les données filtrées (CSV)",
        lambda: fdf[export_cols].to_csv(index=False).encode("utf-8"),  # généré au clic seulement
        "accidents_filtres.csv", "text/csv", icon=":material/download:",
    )
