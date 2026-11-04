"""Filtres globaux (barre latérale), partagés par toutes les pages."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd
import streamlit as st

PREFIX = "flt_"


@dataclass(frozen=True)
class Filters:
    years: tuple[int, int]
    countries: tuple[str, ...] = field(default_factory=tuple)
    severity: tuple[str, ...] = field(default_factory=tuple)
    causes: tuple[str, ...] = field(default_factory=tuple)
    weather: tuple[str, ...] = field(default_factory=tuple)
    setting: tuple[str, ...] = field(default_factory=tuple)
    vulnerable: str = "Tous"

    def active(self, df: pd.DataFrame) -> dict[str, str]:
        """Résumé lisible des filtres réellement actifs."""
        out = {}
        y_min, y_max = int(df["Year"].min()), int(df["Year"].max())
        if self.years != (y_min, y_max):
            out["Période"] = f"{self.years[0]} – {self.years[1]}"
        for label, values in [
            ("Pays", self.countries), ("Gravité", self.severity), ("Cause", self.causes),
            ("Météo", self.weather), ("Milieu", self.setting),
        ]:
            if values:
                out[label] = ", ".join(values)
        if self.vulnerable != "Tous":
            out["Usagers vulnérables"] = self.vulnerable
        return out


def _options(df: pd.DataFrame, col: str) -> list[str]:
    return [str(c) for c in df[col].cat.categories]


def _reset(df: pd.DataFrame) -> None:
    for key in list(st.session_state.keys()):
        if key.startswith(PREFIX):
            del st.session_state[key]


def render_sidebar_filters(df: pd.DataFrame) -> Filters:
    """Affiche les filtres dans la barre latérale. Les clés de session garantissent
    que la sélection est conservée lors de la navigation entre les pages."""
    y_min, y_max = int(df["Year"].min()), int(df["Year"].max())

    with st.sidebar:
        st.markdown("### Filtres")
        years = st.slider("Période", y_min, y_max, (y_min, y_max), key=f"{PREFIX}years")
        countries = st.multiselect(
            "Pays", _options(df, "Country"), key=f"{PREFIX}countries", placeholder="Tous les pays"
        )
        severity = st.multiselect(
            "Gravité déclarée", _options(df, "Accident Severity"), key=f"{PREFIX}severity",
            placeholder="Toutes",
        )
        causes = st.multiselect(
            "Cause", _options(df, "Accident Cause"), key=f"{PREFIX}causes", placeholder="Toutes"
        )
        with st.expander("Plus de filtres"):
            weather = st.multiselect(
                "Météo", _options(df, "Weather Conditions"), key=f"{PREFIX}weather",
                placeholder="Toutes",
            )
            setting = st.multiselect(
                "Milieu", _options(df, "Urban/Rural"), key=f"{PREFIX}setting", placeholder="Tous"
            )
            vulnerable = st.radio(
                "Piétons ou cyclistes impliqués",
                ["Tous", "Oui", "Non"],
                horizontal=True,
                key=f"{PREFIX}vulnerable",
                help="« Oui » : au moins un piéton ou un cycliste impliqué. « Non » : aucun.",
            )
        st.button(
            "Réinitialiser les filtres", on_click=_reset, args=(df,), width="stretch",
            icon=":material/restart_alt:",
        )

    return Filters(
        years=tuple(years), countries=tuple(countries), severity=tuple(severity),
        causes=tuple(causes), weather=tuple(weather), setting=tuple(setting),
        vulnerable=vulnerable,
    )


def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    """Applique les filtres avec un unique masque booléen (pas de copies successives)."""
    mask = df["Year"].between(*f.years)
    for col, values in [
        ("Country", f.countries), ("Accident Severity", f.severity),
        ("Accident Cause", f.causes), ("Weather Conditions", f.weather),
        ("Urban/Rural", f.setting),
    ]:
        if values:
            mask &= df[col].isin(values)
    if f.vulnerable != "Tous":
        has_vulnerable = (df["Pedestrians Involved"] + df["Cyclists Involved"]) > 0
        mask &= has_vulnerable if f.vulnerable == "Oui" else ~has_vulnerable
    return df.loc[mask]
