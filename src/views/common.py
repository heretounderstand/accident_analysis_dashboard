"""Blocs d'analyse réutilisés par plusieurs pages."""
import numpy as np
import pandas as pd

from .. import charts
from ..config import LABELS, METRICS
from ..stats import association, group_summary
from ..ui import chart_card, summary_table


def factor_card(df: pd.DataFrame, factor: str, metric: str, title: str | None = None,
                subtitle: str | None = None, sort: bool = False, key: str | None = None) -> None:
    """Moyenne par modalité + IC 95 % + test statistique + tableau."""
    meta = METRICS[metric]
    summary = group_summary(df, factor, metric)
    fig = charts.mean_ci_plot(
        summary, factor, meta["short"], fmt=meta["fmt"], reference=df[metric].mean(), sort=sort,
    )
    chart_card(
        title or f"{meta['label']} selon : {LABELS.get(factor, factor).lower()}",
        fig,
        subtitle=subtitle or "Point = moyenne · segment = intervalle de confiance à 95 %.",
        test=association(df, factor, metric),
        table=summary_table(summary, factor, metric),
        key=key,
    )


def deviation_card(df: pd.DataFrame, rows: str, cols: str, metric: str, title: str,
                   subtitle: str | None = None, key: str | None = None) -> None:
    """Heatmap de l'écart relatif à la moyenne globale pour un croisement de deux facteurs."""
    meta = METRICS[metric]
    overall = df[metric].mean()
    pivot = df.pivot_table(index=rows, columns=cols, values=metric, aggfunc="mean", observed=True)
    counts = df.pivot_table(index=rows, columns=cols, values=metric, aggfunc="count", observed=True)
    deviation = pivot / overall - 1 if overall else pivot * np.nan
    fig = charts.deviation_heatmap(
        deviation, meta["short"], LABELS.get(cols, cols), LABELS.get(rows, rows), counts=counts,
    )
    table = pivot.copy()
    table.index = table.index.astype(str)
    table.columns = table.columns.astype(str)
    table = table.round(3).reset_index().rename(columns={rows: LABELS.get(rows, rows)})
    chart_card(
        title, fig,
        subtitle=subtitle or (
            "Écart de chaque combinaison à la moyenne globale. Gris = dans la moyenne, "
            "rouge = au-dessus, bleu = en dessous. Échelle d'au moins ±10 % pour ne pas amplifier le bruit."
        ),
        table=table, key=key,
    )
