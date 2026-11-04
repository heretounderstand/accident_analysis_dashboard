"""Composants d'interface communs (en-têtes, cartes, encadrés, graphiques)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .charts import PLOTLY_CONFIG, SURFACE, TEMPLATE
from .config import DEFAULT_METRIC, LABELS, METRICS
from .stats import AssociationResult, describe_result

CSS = """
<style>
:root {
  --ink: #0b0b0b; --ink-2: #52514e; --muted: #898781;
  --surface: #fcfcfb; --plane: #f9f9f7; --hairline: rgba(11,11,11,0.10);
  --accent: #2a78d6; --accent-soft: #e8f1fc; --warn-soft: #fff6e0; --warn: #b07800;
}
.block-container { padding-top: 3.6rem; padding-bottom: 3rem; max-width: 1320px; }
h1, h2, h3, h4 { letter-spacing: -0.01em; color: var(--ink); }
[data-testid="stSidebar"] { border-right: 1px solid var(--hairline); }

.page-eyebrow { color: var(--accent); font-weight: 600; font-size: .78rem;
  text-transform: uppercase; letter-spacing: .08em; margin-bottom: .2rem; }
.page-title { font-size: 2.05rem; font-weight: 700; line-height: 1.15; margin: 0 0 .35rem 0; color: var(--ink); }
.page-lead { color: var(--ink-2); font-size: 1.02rem; max-width: 820px; margin-bottom: .6rem; }

.chip-row { display: flex; flex-wrap: wrap; gap: .4rem; margin: .2rem 0 1rem 0; }
.chip { background: var(--accent-soft); color: #184f95; border-radius: 999px;
  padding: .18rem .7rem; font-size: .8rem; }
.chip.neutral { background: #f0efec; color: var(--ink-2); }

.callout { border-radius: 10px; padding: .85rem 1rem; margin: .3rem 0 1rem 0;
  border: 1px solid var(--hairline); background: var(--surface); font-size: .93rem; color: var(--ink-2); }
.callout b, .callout strong { color: var(--ink); }
.callout.info { border-left: 3px solid var(--accent); }
.callout.warn { border-left: 3px solid #fab219; background: var(--warn-soft); }
.callout .title { font-weight: 600; color: var(--ink); margin-bottom: .2rem; }

.chart-title { font-weight: 600; font-size: 1.02rem; color: var(--ink); margin: 0; }
.chart-sub { color: var(--muted); font-size: .85rem; margin: .1rem 0 .3rem 0; }

[data-testid="stMetric"] { background: var(--surface); }
[data-testid="stMetricLabel"] p { color: var(--ink-2); font-size: .85rem; }
[data-testid="stMetricValue"] { font-weight: 650; }
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"] .chart-title) {
  background: var(--surface);
}
.stTabs [data-baseweb="tab-list"] { gap: .25rem; }
.footer { color: var(--muted); font-size: .8rem; margin-top: 2.5rem; border-top: 1px solid var(--hairline); padding-top: .8rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, lead: str) -> None:
    st.markdown(
        f'<div class="page-eyebrow">{eyebrow}</div>'
        f'<h1 class="page-title">{title}</h1>'
        f'<p class="page-lead">{lead}</p>',
        unsafe_allow_html=True,
    )
    summary = st.session_state.get("_filter_summary")
    if summary:
        filter_chips(*summary)


def filter_chips(active: dict[str, str], n_rows: int, n_total: int) -> None:
    share = n_rows / n_total if n_total else 0
    chips = [f'<span class="chip neutral">{fmt_int(n_rows)} accidents · {pct(share, 0)} du total</span>']
    if not active:
        chips.append('<span class="chip neutral">Aucun filtre actif</span>')
    chips += [f'<span class="chip">{k} : {v}</span>' for k, v in active.items()]
    st.markdown(f'<div class="chip-row">{"".join(chips)}</div>', unsafe_allow_html=True)


def callout(body: str, title: str | None = None, kind: str = "info") -> None:
    head = f'<div class="title">{title}</div>' if title else ""
    st.markdown(f'<div class="callout {kind}">{head}{body}</div>', unsafe_allow_html=True)


def metric_picker(key: str, options: list[str] | None = None) -> str:
    """Sélecteur de l'indicateur « par accident » analysé sur la page."""
    options = options or list(METRICS)
    choice = st.segmented_control(
        "Indicateur analysé", options, format_func=lambda m: METRICS[m]["label"],
        default=DEFAULT_METRIC if DEFAULT_METRIC in options else options[0],
        key=key, required=True,
    )
    return choice or options[0]


def chart_card(
    title: str, fig: go.Figure, subtitle: str | None = None,
    test: AssociationResult | None | str = "skip", table: pd.DataFrame | None = None,
    key: str | None = None,
) -> None:
    """Carte contenant titre, graphique, interprétation statistique et vue tableau."""
    with st.container(border=True):
        st.markdown(f'<p class="chart-title">{title}</p>', unsafe_allow_html=True)
        if subtitle:
            st.markdown(f'<p class="chart-sub">{subtitle}</p>', unsafe_allow_html=True)
        # Streamlit remplace le template Plotly par défaut : on l'impose explicitement.
        fig.update_layout(template=TEMPLATE, paper_bgcolor=SURFACE, plot_bgcolor=SURFACE)
        st.plotly_chart(fig, theme=None, config=PLOTLY_CONFIG, key=key)
        if test != "skip":
            st.caption(describe_result(test))
        if table is not None:
            with st.expander("Voir les données"):
                st.dataframe(table, hide_index=True)


def summary_table(summary: pd.DataFrame, category: str, metric: str) -> pd.DataFrame:
    """Met en forme un résultat de stats.group_summary pour l'affichage."""
    fmt = METRICS.get(metric, {}).get("fmt", ".2f")
    pct = fmt.endswith("%")

    def f(v: float) -> str:
        if pct:
            return f"{v:.1%}"
        if "," in fmt:
            return f"{v:,.0f}".replace(",", " ")
        return f"{v:.3f}"

    return pd.DataFrame({
        LABELS.get(category, category): summary[category].astype(str),
        "Accidents": summary["n"],
        METRICS.get(metric, {}).get("label", metric): summary["mean"].map(f),
        "IC 95 % bas": summary["low"].map(f),
        "IC 95 % haut": summary["high"].map(f),
    })


def fr(v: float, fmt: str = ".1f") -> str:
    """Formate un nombre à la française : virgule décimale, espace pour les milliers."""
    s = format(v, fmt)
    return s.replace(",", "\u202f").replace(".", ",")


def pct(v: float, digits: int = 1, sign: bool = False) -> str:
    return fr(v, f"{'+' if sign else ''}.{digits}%").replace("%", " %")


def fmt_int(v: float) -> str:
    return f"{v:,.0f}".replace(",", " ")


def fmt_money(v: float) -> str:
    """Format monétaire compact (k, M, Md)."""
    a = abs(v)
    for div, suffix in [(1e9, " Md"), (1e6, " M"), (1e3, " k")]:
        if a >= div:
            return f"{v / div:,.1f}{suffix} $".replace(".", ",")
    return f"{v:,.0f} $"


def footer() -> None:
    st.markdown(
        '<div class="footer">Source : jeu de données « Global Road Accidents » (132 000 accidents, '
        "2000 – 2024). Montants exprimés dans une devise non précisée par la source, notée $. "
        "Voir la page <b>Qualité des données</b> pour les limites d'interprétation.</div>",
        unsafe_allow_html=True,
    )
