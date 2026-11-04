"""Chargement, nettoyage et enrichissement du jeu de données."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from .config import (
    ALCOHOL_BINS, ALCOHOL_LABELS, CATEGORY_ORDERS, COUNTRY_TO_CONTINENT, DATA_PATH,
    NUMERIC_COLUMNS, QUINTILE_LABELS, SPEED_BINS, SPEED_LABELS, TRANSLATIONS,
)

MONTH_NUMBER = {name: i for i, name in enumerate(CATEGORY_ORDERS["Month"], start=1)}


class DataLoadError(RuntimeError):
    """Erreur explicite levée quand le fichier source est absent ou invalide."""


def _to_category(series: pd.Series, column: str) -> pd.Series:
    order = CATEGORY_ORDERS.get(column)
    if order is None:
        order = sorted(series.dropna().unique())
    return pd.Categorical(series, categories=order, ordered=column in CATEGORY_ORDERS)


def prepare_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Nettoie et enrichit le DataFrame brut (fonction pure, testable)."""
    missing = set(NUMERIC_COLUMNS) - set(raw.columns)
    if missing:
        raise DataLoadError(f"Colonnes manquantes dans le fichier : {sorted(missing)}")

    df = raw.copy()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Traduction des modalités
    for col, mapping in TRANSLATIONS.items():
        df[col] = df[col].map(mapping).fillna(df[col])

    # Date (1er du mois : la source ne fournit pas le jour)
    df["Date"] = pd.to_datetime(
        dict(year=df["Year"], month=df["Month"].map(MONTH_NUMBER), day=1), errors="coerce"
    )

    # Variables dérivées
    df["Continent"] = df["Country"].map(COUNTRY_TO_CONTINENT)
    df["Victims"] = df["Number of Injuries"] + df["Number of Fatalities"]
    df["Is Fatal"] = (df["Number of Fatalities"] > 0).astype(float)
    df["Total Cost"] = df["Medical Cost"] + df["Economic Loss"]
    df["Fatigue"] = df["Driver Fatigue"].map({1: "Oui", 0: "Non"})
    df["Alcohol Band"] = pd.cut(
        df["Driver Alcohol Level"], bins=ALCOHOL_BINS, labels=ALCOHOL_LABELS, right=False
    )
    df["Speed Band"] = pd.cut(df["Speed Limit"], bins=SPEED_BINS, labels=SPEED_LABELS)
    df["Visibility Band"] = pd.qcut(df["Visibility Level"], 5, labels=QUINTILE_LABELS)
    df["Traffic Band"] = pd.qcut(df["Traffic Volume"], 5, labels=QUINTILE_LABELS)
    df["Density Band"] = pd.qcut(df["Population Density"], 5, labels=QUINTILE_LABELS)

    categorical = [
        "Country", "Continent", "Region", "Month", "Day of Week", "Time of Day",
        "Urban/Rural", "Road Type", "Weather Conditions", "Driver Age Group",
        "Driver Gender", "Vehicle Condition", "Accident Severity", "Road Condition",
        "Accident Cause", "Fatigue",
    ]
    for col in categorical:
        df[col] = _to_category(df[col], col)

    return df


@st.cache_data(show_spinner="Chargement des données…")
def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Charge le CSV source (mis en cache pour toute la session)."""
    if not Path(path).exists():
        raise DataLoadError(f"Fichier introuvable : {path}")
    return prepare_data(pd.read_csv(path))
