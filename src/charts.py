"""Thème Plotly commun et fonctions de construction des graphiques.

Règles appliquées partout :
- une seule couleur pour une seule série, palette catégorielle dans un ordre fixe ;
- séquentiel = une teinte (bleu) du clair au foncé ; écart à la moyenne = palette divergente
  bleu ↔ rouge avec un gris neutre au centre ;
- jamais de double axe ; moyennes toujours accompagnées de leur IC à 95 %.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

# --------------------------------------------------------------------------- #
# Palette (validée daltonisme pour les 3 premiers créneaux en toutes paires)
# --------------------------------------------------------------------------- #
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
BLUE = SERIES[0]
ORANGE = SERIES[1]
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
ORDINAL_BLUE = ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]
DIVERGING = [
    [0.0, "#184f95"], [0.25, "#6da7ec"], [0.5, "#f0efec"], [0.75, "#ec8a7f"], [1.0, "#b8322f"],
]

INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
SURFACE = "#fcfcfb"
FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif'

CHART_HEIGHT = 380
PLOTLY_CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]}

_template = go.layout.Template()
_template.layout = go.Layout(
    font=dict(family=FONT, size=13, color=INK_2),
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    colorway=SERIES,
    height=CHART_HEIGHT,
    margin=dict(l=8, r=16, t=16, b=8),
    hoverlabel=dict(bgcolor="white", bordercolor=AXIS, font=dict(family=FONT, size=12, color=INK)),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text="",
                font=dict(color=INK_2)),
    xaxis=dict(showgrid=False, linecolor=AXIS, ticks="", tickfont=dict(color=MUTED),
               title=dict(font=dict(color=INK_2)), zeroline=False, automargin=True),
    yaxis=dict(gridcolor=GRID, gridwidth=1, linecolor=AXIS, showline=False,
               tickfont=dict(color=MUTED), title=dict(font=dict(color=INK_2)),
               zeroline=False, automargin=True),
    bargap=0.35,
    coloraxis=dict(colorbar=dict(thickness=10, outlinewidth=0, tickfont=dict(color=MUTED))),
)
pio.templates["accidents"] = _template
TEMPLATE = "plotly_white+accidents"
pio.templates.default = TEMPLATE


def _fmt_hover(fmt: str) -> str:
    return "%{x:" + fmt + "}"


# --------------------------------------------------------------------------- #
# Comparaison de moyennes : « dot plot » avec IC à 95 %
# --------------------------------------------------------------------------- #
def mean_ci_plot(
    summary: pd.DataFrame,
    category: str,
    value_label: str,
    fmt: str = ".2f",
    reference: float | None = None,
    sort: bool = False,
    height: int | None = None,
) -> go.Figure:
    """Moyenne par groupe (point) + IC 95 % (segment), ligne de référence = moyenne globale.

    Plus honnête qu'un histogramme de sommes : la taille des groupes n'influence
    pas la lecture et l'incertitude est visible.
    """
    data = summary.copy()
    data[category] = data[category].astype(str)
    if sort:
        data = data.sort_values("mean")
    else:
        data = data.iloc[::-1]  # premier groupe en haut

    is_pct = fmt.endswith("%")
    tick = ".0%" if is_pct else None

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["mean"], y=data[category], mode="markers",
        marker=dict(size=11, color=BLUE, line=dict(color=SURFACE, width=2)),
        error_x=dict(type="data", symmetric=False, array=data["high"] - data["mean"],
                     arrayminus=data["mean"] - data["low"], color=BLUE, thickness=2, width=0),
        customdata=np.stack([data["low"], data["high"], data["n"]], axis=-1),
        hovertemplate=(
            "<b>%{y}</b><br>" + value_label + " : " + _fmt_hover(fmt)
            + "<br>IC 95 % : [%{customdata[0]:" + fmt + "} ; %{customdata[1]:" + fmt + "}]"
            + "<br>Accidents : %{customdata[2]:,.0f}<extra></extra>"
        ),
        showlegend=False,
    ))
    if reference is not None:
        fig.add_vline(x=reference, line=dict(color=MUTED, width=1))
        fig.add_annotation(
            x=reference, y=1, yref="paper", yanchor="bottom", showarrow=False,
            text="moyenne globale", font=dict(size=11, color=MUTED),
        )
    n_rows = len(data)
    fig.update_layout(
        height=height or max(220, 46 * n_rows + 90),
        xaxis=dict(title=value_label, tickformat=tick, showgrid=True, gridcolor=GRID),
        yaxis=dict(title=None, showgrid=False, type="category"),
        margin=dict(t=28),
    )
    return fig


# --------------------------------------------------------------------------- #
# Barres simples (effectifs)
# --------------------------------------------------------------------------- #
def bar_chart(
    data: pd.DataFrame, x: str, y: str, y_label: str, fmt: str = ",.0f",
    horizontal: bool = False, color: str = BLUE, height: int | None = None,
) -> go.Figure:
    d = data.copy()
    d[x] = d[x].astype(str)
    if horizontal:
        d = d.iloc[::-1]
        trace = go.Bar(y=d[x], x=d[y], orientation="h", marker=dict(color=color, cornerradius=4),
                       hovertemplate="<b>%{y}</b><br>" + y_label + " : %{x:" + fmt + "}<extra></extra>")
    else:
        trace = go.Bar(x=d[x], y=d[y], marker=dict(color=color, cornerradius=4),
                       hovertemplate="<b>%{x}</b><br>" + y_label + " : %{y:" + fmt + "}<extra></extra>")
    fig = go.Figure(trace)
    axis = dict(title=y_label, tickformat=fmt.replace(",.0f", "~s") if fmt == ",.0f" else fmt)
    if horizontal:
        fig.update_layout(xaxis=axis | dict(showgrid=True, gridcolor=GRID),
                          yaxis=dict(title=None, showgrid=False))
    else:
        fig.update_layout(yaxis=axis, xaxis=dict(title=None, type="category"))
    if height:
        fig.update_layout(height=height)
    return fig


# --------------------------------------------------------------------------- #
# Séries temporelles
# --------------------------------------------------------------------------- #
def line_chart(
    data: pd.DataFrame, x: str, y: str, y_label: str, fmt: str = ",.0f",
    band: tuple[str, str] | None = None, rolling: str | None = None,
    y_from_zero: bool = True, height: int | None = None,
) -> go.Figure:
    """Courbe principale (2 px), bande d'IC optionnelle, moyenne mobile optionnelle."""
    fig = go.Figure()
    if band is not None:
        lo, hi = band
        fig.add_trace(go.Scatter(
            x=pd.concat([data[x], data[x][::-1]]), y=pd.concat([data[hi], data[lo][::-1]]),
            fill="toself", fillcolor="rgba(42,120,214,0.14)", line=dict(width=0),
            hoverinfo="skip", showlegend=False,
        ))
    fig.add_trace(go.Scatter(
        x=data[x], y=data[y], mode="lines+markers" if len(data) <= 40 else "lines",
        line=dict(color=BLUE, width=2), marker=dict(size=6, color=BLUE),
        name=y_label, showlegend=rolling is not None,
        hovertemplate="%{x}<br>" + y_label + " : %{y:" + fmt + "}<extra></extra>",
    ))
    if rolling is not None:
        fig.add_trace(go.Scatter(
            x=data[x], y=data[rolling], mode="lines", line=dict(color=ORANGE, width=2),
            name="Moyenne mobile 12 mois",
            hovertemplate="%{x}<br>Moyenne mobile : %{y:" + fmt + "}<extra></extra>",
        ))
    tick = ".0%" if fmt.endswith("%") else None
    yaxis = dict(title=y_label, tickformat=tick)
    if y_from_zero:
        yaxis["rangemode"] = "tozero"
    fig.update_layout(yaxis=yaxis, xaxis=dict(title=None), hovermode="x unified")
    if height:
        fig.update_layout(height=height)
    return fig


def decomposition_chart(index: pd.DatetimeIndex, observed, trend, seasonal, resid) -> go.Figure:
    """Décomposition STL en petits multiples (un axe par composante, pas de double axe)."""
    fig = make_subplots(
        rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.06,
        subplot_titles=("Série observée", "Tendance", "Saisonnalité", "Résidus"),
    )
    parts = [(observed, BLUE), (trend, BLUE), (seasonal, BLUE), (resid, MUTED)]
    for i, (series, color) in enumerate(parts, start=1):
        fig.add_trace(go.Scatter(
            x=index, y=series, mode="lines", line=dict(color=color, width=1.6 if i != 2 else 2),
            showlegend=False, hovertemplate="%{x|%b %Y} : %{y:,.1f}<extra></extra>",
        ), row=i, col=1)
    fig.update_layout(height=640, margin=dict(t=36))
    fig.update_annotations(font=dict(size=12, color=INK_2), x=0, xanchor="left")
    fig.update_yaxes(gridcolor=GRID)
    return fig


# --------------------------------------------------------------------------- #
# Heatmaps
# --------------------------------------------------------------------------- #
def deviation_heatmap(
    pivot: pd.DataFrame, value_label: str, x_label: str, y_label: str,
    counts: pd.DataFrame | None = None, height: int | None = None,
) -> go.Figure:
    """Écart relatif (%) de chaque cellule à la moyenne globale, palette divergente centrée."""
    z = pivot.to_numpy(dtype=float)
    bound = float(np.nanmax(np.abs(z))) if np.isfinite(z).any() else 0.01
    # Échelle d'au moins ±10 % : sinon un bruit de ±2 % saturerait les couleurs et
    # suggérerait des écarts importants qui n'existent pas.
    bound = max(bound, 0.10)
    custom = counts.reindex(index=pivot.index, columns=pivot.columns).to_numpy() if counts is not None else None
    fig = go.Figure(go.Heatmap(
        z=z, x=[str(c) for c in pivot.columns], y=[str(i) for i in pivot.index],
        colorscale=DIVERGING, zmin=-bound, zmax=bound, zmid=0, xgap=2, ygap=2,
        customdata=custom,
        text=[[f"{v:+.1%}" if np.isfinite(v) else "" for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=11, color=INK),
        colorbar=dict(title=dict(text="Écart", side="right"), tickformat="+.0%", thickness=10,
                      outlinewidth=0),
        hovertemplate=(
            f"{y_label} : %{{y}}<br>{x_label} : %{{x}}<br>Écart à la moyenne ({value_label}) : %{{z:+.1%}}"
            + ("<br>Accidents : %{customdata:,.0f}" if custom is not None else "")
            + "<extra></extra>"
        ),
    ))
    fig.update_layout(
        xaxis=dict(title=x_label, side="bottom", showgrid=False, type="category"),
        yaxis=dict(title=y_label, showgrid=False, autorange="reversed", type="category"),
        height=height or max(300, 44 * len(pivot.index) + 120),
    )
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    labels = list(corr.columns)
    z = corr.to_numpy(dtype=float).copy()
    np.fill_diagonal(z, np.nan)  # la diagonale (r = 1) écraserait visuellement le reste
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels, colorscale=DIVERGING, zmin=-1, zmax=1, zmid=0,
        xgap=1, ygap=1,
        colorbar=dict(title=dict(text="r", side="right"), thickness=10, outlinewidth=0),
        hovertemplate="%{y} × %{x}<br>r = %{z:.3f}<extra></extra>",
    ))
    fig.update_layout(
        height=620, xaxis=dict(showgrid=False, tickangle=-45),
        yaxis=dict(showgrid=False, autorange="reversed"),
    )
    return fig


# --------------------------------------------------------------------------- #
# Carte
# --------------------------------------------------------------------------- #
def choropleth(data: pd.DataFrame, iso_col: str, value: str, name_col: str,
               value_label: str, fmt: str) -> go.Figure:
    fig = go.Figure(go.Choropleth(
        locations=data[iso_col], z=data[value], text=data[name_col],
        colorscale=[[i / (len(SEQ_BLUE) - 1), c] for i, c in enumerate(SEQ_BLUE)],
        marker_line_color="white", marker_line_width=0.6,
        colorbar=dict(title=dict(text=value_label, side="right"), thickness=10, outlinewidth=0,
                      tickformat=".0%" if fmt.endswith("%") else None),
        customdata=data["n"],
        hovertemplate="<b>%{text}</b><br>" + value_label + " : %{z:" + fmt
                      + "}<br>Accidents : %{customdata:,.0f}<extra></extra>",
    ))
    fig.update_geos(
        showframe=False, showcoastlines=False, showland=True, landcolor="#ecebe6",
        showcountries=True, countrycolor="white", projection_type="natural earth",
        bgcolor="rgba(0,0,0,0)", lataxis_range=[-58, 85],
    )
    fig.update_layout(height=440, margin=dict(l=0, r=0, t=0, b=0))
    return fig


# --------------------------------------------------------------------------- #
# Classement des facteurs (tailles d'effet)
# --------------------------------------------------------------------------- #
def effect_size_chart(ranking: pd.DataFrame, labels: dict[str, str]) -> go.Figure:
    d = ranking.iloc[::-1].copy()
    d["label"] = d["factor"].map(lambda f: labels.get(f, f))
    colors = [BLUE if s else AXIS for s in d["significant"]]
    effect_name = d["effect_name"].iloc[0] if not d.empty else ""
    fig = go.Figure(go.Bar(
        y=d["label"], x=d["effect"], orientation="h", marker=dict(color=colors, cornerradius=4),
        customdata=np.stack([d["p_adj"], d["magnitude"]], axis=-1),
        hovertemplate=(
            "<b>%{y}</b><br>" + effect_name + " = %{x:.4f}"
            "<br>p ajustée (Bonferroni) = %{customdata[0]:.3g}"
            "<br>Effet : %{customdata[1]}<extra></extra>"
        ),
    ))
    threshold = 0.01 if effect_name == "ε²" else 0.10
    fig.add_vline(x=threshold, line=dict(color=MUTED, width=1))
    fig.add_annotation(x=threshold, y=1, yref="paper", yanchor="bottom", showarrow=False,
                       text="seuil d'effet « faible »", font=dict(size=11, color=MUTED))
    fig.update_layout(
        height=max(300, 26 * len(d) + 90), bargap=0.3,
        xaxis=dict(title=f"Taille d'effet ({effect_name})", showgrid=True, gridcolor=GRID,
                   range=[0, max(threshold * 1.15, float(d["effect"].max()) * 1.1)]),
        yaxis=dict(title=None), margin=dict(t=28),
    )
    return fig


def histogram(data: pd.Series, label: str, nbins: int = 40, fmt: str = ",.0f") -> go.Figure:
    fig = go.Figure(go.Histogram(
        x=data, nbinsx=nbins, marker=dict(color=BLUE, line=dict(color=SURFACE, width=1)),
        hovertemplate=label + " : %{x}<br>Accidents : %{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(xaxis=dict(title=label, tickformat=None),
                      yaxis=dict(title="Accidents"), bargap=0.04)
    return fig


def stacked_share_bar(data: pd.DataFrame, category: str, stack: str, value: str,
                      order: list[str], colors: list[str], value_label: str) -> go.Figure:
    """Barres 100 % empilées (part de chaque modalité dans chaque groupe)."""
    fig = go.Figure()
    for i, level in enumerate(order):
        sub = data[data[stack] == level]
        fig.add_trace(go.Bar(
            y=sub[category].astype(str), x=sub[value], name=level, orientation="h",
            marker=dict(color=colors[i % len(colors)], line=dict(color=SURFACE, width=2)),
            hovertemplate="<b>%{y}</b><br>" + level + " : %{x:.1%}<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack", xaxis=dict(title=value_label, tickformat=".0%", showgrid=True,
                                    gridcolor=GRID, range=[0, 1]),
        yaxis=dict(title=None, autorange="reversed"), legend=dict(traceorder="normal"),
    )
    return fig
