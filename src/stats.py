"""Fonctions statistiques : moyennes avec IC, tests d'association, tailles d'effet."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats as sps

from .config import SIGNIFICANCE_LEVEL

Z_95 = 1.959964


def group_summary(df: pd.DataFrame, by: str, value: str) -> pd.DataFrame:
    """Moyenne par groupe avec intervalle de confiance à 95 % (approximation normale)."""
    g = df.groupby(by, observed=True)[value]
    out = g.agg(mean="mean", std="std", n="count").reset_index()
    out["se"] = out["std"] / np.sqrt(out["n"])
    out["ci"] = Z_95 * out["se"].fillna(0)
    out["low"] = out["mean"] - out["ci"]
    out["high"] = out["mean"] + out["ci"]
    out["share"] = out["n"] / out["n"].sum()
    return out


def pct_change(current: float, previous: float) -> float | None:
    """Variation relative ; None si la base est nulle (évite la division par zéro)."""
    if previous is None or previous == 0 or pd.isna(previous):
        return None
    return (current - previous) / previous


@dataclass
class AssociationResult:
    factor: str
    test: str
    statistic: float
    p_value: float
    effect: float
    effect_name: str
    n: int
    k: int

    @property
    def significant(self) -> bool:
        return self.p_value < SIGNIFICANCE_LEVEL

    @property
    def magnitude(self) -> str:
        e = self.effect
        if self.effect_name == "ε²":
            cuts = (0.01, 0.06, 0.14)
        else:  # V de Cramér
            cuts = (0.10, 0.30, 0.50)
        if e < cuts[0]:
            return "négligeable"
        if e < cuts[1]:
            return "faible"
        if e < cuts[2]:
            return "moyen"
        return "fort"


def kruskal_test(df: pd.DataFrame, factor: str, value: str) -> AssociationResult | None:
    """Kruskal-Wallis (non paramétrique) + ε² comme taille d'effet."""
    data = df[[factor, value]].dropna()
    groups = [g[value].to_numpy() for _, g in data.groupby(factor, observed=True) if len(g) > 1]
    if len(groups) < 2:
        return None
    n = sum(len(g) for g in groups)
    k = len(groups)
    try:
        h, p = sps.kruskal(*groups)
    except ValueError:  # toutes les valeurs identiques
        return None
    eps2 = max((h - k + 1) / (n - k), 0.0) if n > k else 0.0
    return AssociationResult(factor, "Kruskal-Wallis", float(h), float(p), float(eps2), "ε²", n, k)


def chi2_test(df: pd.DataFrame, factor: str, other: str) -> AssociationResult | None:
    """Khi² d'indépendance + V de Cramér corrigé du biais (Bergsma, 2013)."""
    table = pd.crosstab(df[factor], df[other])
    table = table.loc[table.sum(axis=1) > 0, table.sum(axis=0) > 0]
    if table.shape[0] < 2 or table.shape[1] < 2:
        return None
    chi2, p, _, _ = sps.chi2_contingency(table, correction=False)
    n = table.to_numpy().sum()
    r, c = table.shape
    phi2 = chi2 / n
    phi2_corr = max(0.0, phi2 - (c - 1) * (r - 1) / (n - 1))
    r_corr = r - (r - 1) ** 2 / (n - 1)
    c_corr = c - (c - 1) ** 2 / (n - 1)
    denom = min(r_corr - 1, c_corr - 1)
    v = float(np.sqrt(phi2_corr / denom)) if denom > 0 else 0.0
    return AssociationResult(factor, "Khi²", float(chi2), float(p), v, "V de Cramér", int(n), r)


def association(df: pd.DataFrame, factor: str, value: str) -> AssociationResult | None:
    """Choisit le test adapté : Khi² pour une variable binaire, Kruskal-Wallis sinon."""
    if value == "Is Fatal":
        return chi2_test(df, factor, value)
    return kruskal_test(df, factor, value)


def rank_factors(df: pd.DataFrame, factors: list[str], value: str) -> pd.DataFrame:
    """Teste chaque facteur et applique une correction de Bonferroni."""
    rows = []
    for f in factors:
        res = association(df, f, value)
        if res is None:
            continue
        rows.append({
            "factor": f, "test": res.test, "statistic": res.statistic, "p_value": res.p_value,
            "effect": res.effect, "effect_name": res.effect_name, "magnitude": res.magnitude,
        })
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    out["p_adj"] = np.minimum(out["p_value"] * len(out), 1.0)
    out["significant"] = out["p_adj"] < SIGNIFICANCE_LEVEL
    return out.sort_values("effect", ascending=False).reset_index(drop=True)


def describe_result(res: AssociationResult | None) -> str:
    """Phrase d'interprétation courte, affichée sous les graphiques."""
    if res is None:
        return "Test non calculable (pas assez de groupes ou de données)."
    p_txt = "p < 0,001" if res.p_value < 0.001 else f"p = {res.p_value:.3f}".replace(".", ",")
    verdict = "significative" if res.significant else "non significative"
    effect = f"{res.effect:.4f}".replace(".", ",")
    return (
        f"{res.test} : différence **{verdict}** ({p_txt}) · "
        f"taille d'effet {res.effect_name} = {effect} → **{res.magnitude}**"
    )


def uniformity_test(series: pd.Series) -> tuple[float, float]:
    """Khi² d'adéquation à une loi uniforme sur les modalités observées."""
    counts = series.value_counts()
    chi2, p = sps.chisquare(counts.to_numpy())
    return float(chi2), float(p)
