import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from ..config import THEME_CONFIG, CHART_HEIGHT, CHART_WIDTH

def create_base_figure(title: str = None) -> go.Figure:
    """
    Crée une figure de base avec le thème personnalisé
    """
    fig = go.Figure()
    fig.update_layout(
        template='plotly_white',
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        title=title,
        title_x=0.5,
        font=dict(color=THEME_CONFIG['text']),
        paper_bgcolor=THEME_CONFIG['background'],
        plot_bgcolor='white'
    )
    return fig

def style_chart(fig: go.Figure) -> go.Figure:
    """
    Applique le style commun aux graphiques
    """
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#E1E5EA')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#E1E5EA')
    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Arial"
        )
    )
    return fig

def create_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    color: str = None
) -> go.Figure:
    """
    Crée un graphique temporel
    """
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        height=CHART_HEIGHT,
        width=CHART_WIDTH
    )
    
    if color is None:
        color = THEME_CONFIG['primary']
    
    fig.update_layout(xaxis_title="Date")
    fig.update_traces(line_color=color)
    return style_chart(fig)

def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color: str = None
) -> go.Figure:
    """
    Crée un graphique en barres
    """
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH
    )
    
    if color is None:
        color = THEME_CONFIG['primary']
    
    fig.update_traces(marker_color=color)
    return style_chart(fig)

def create_scatter_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    size_col: str = None,
    color_col: str = None,
    title: str = ""
) -> go.Figure:
    """
    Crée un graphique de dispersion
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH
    )
    return style_chart(fig)

def create_heatmap(
    df: pd.DataFrame,
    title: str = ""
) -> go.Figure:
    """
    Crée une carte de chaleur
    """
    fig = px.imshow(
        df,
        title=title,
        height=CHART_HEIGHT,
        width=CHART_WIDTH,
        color_continuous_scale=px.colors.sequential.Reds
    )
    return style_chart(fig)