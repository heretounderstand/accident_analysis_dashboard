"""Tests de la chaîne de données et des statistiques : python -m pytest"""
import numpy as np
import pandas as pd
import pytest

from src.config import DATA_PATH, RISK_FACTORS
from src.data_loader import DataLoadError, prepare_data
from src.filters import Filters, apply_filters
from src.stats import chi2_test, group_summary, kruskal_test, pct_change, rank_factors


@pytest.fixture(scope="module")
def df():
    return prepare_data(pd.read_csv(DATA_PATH, nrows=20_000))


def test_prepare_data_derives_columns(df):
    for col in ["Date", "Continent", "Victims", "Is Fatal", "Total Cost", "Alcohol Band"]:
        assert col in df.columns
    assert df["Date"].notna().all()
    assert (df["Victims"] == df["Number of Injuries"] + df["Number of Fatalities"]).all()
    assert df["Continent"].notna().all(), "chaque pays doit avoir un continent"
    assert set(df["Accident Severity"].cat.categories) == {"Mineure", "Modérée", "Grave"}
    assert df["Month"].cat.ordered


def test_prepare_data_rejects_bad_schema():
    with pytest.raises(DataLoadError):
        prepare_data(pd.DataFrame({"Country": ["USA"]}))


def test_apply_filters(df):
    f = Filters(years=(2010, 2012), countries=("Japon",), vulnerable="Non")
    out = apply_filters(df, f)
    assert out["Year"].between(2010, 2012).all()
    assert (out["Country"] == "Japon").all()
    assert ((out["Pedestrians Involved"] + out["Cyclists Involved"]) == 0).all()
    assert len(apply_filters(df, Filters(years=(1900, 1901)))) == 0


def test_group_summary_ci(df):
    s = group_summary(df, "Accident Severity", "Number of Fatalities")
    assert s["n"].sum() == len(df)
    assert (s["low"] <= s["mean"]).all() and (s["mean"] <= s["high"]).all()


def test_pct_change_handles_zero():
    assert pct_change(10, 0) is None
    assert pct_change(12, 10) == pytest.approx(0.2)


def test_tests_detect_real_effect():
    rng = np.random.default_rng(0)
    g = np.repeat(["a", "b"], 500)
    strong = pd.DataFrame({"g": g, "v": np.r_[rng.normal(0, 1, 500), rng.normal(2, 1, 500)]})
    res = kruskal_test(strong, "g", "v")
    assert res.significant and res.magnitude in {"moyen", "fort"}
    cat = pd.DataFrame({"g": g, "y": np.r_[np.ones(450), np.zeros(50), np.zeros(450), np.ones(50)]})
    assert chi2_test(cat, "g", "y").effect > 0.5


def test_rank_factors_bonferroni(df):
    r = rank_factors(df, RISK_FACTORS[:5], "Number of Fatalities")
    assert len(r) == 5
    assert (r["p_adj"] >= r["p_value"]).all()
    assert r["effect"].is_monotonic_decreasing
