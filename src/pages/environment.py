import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart
from ..components.filters import render_filters

def create_road_weather_bar(df, metric='Number of Fatalities'):
    """Création du graphique en barres groupées routes vs météo"""
    road_weather_data = df.groupby(['Road Type', 'Weather Conditions']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = px.bar(
        road_weather_data,
        x='Road Type',
        y=metric,
        color='Weather Conditions',
        barmode='group'
    )
    return style_chart(fig)

def create_visibility_traffic_heatmap(df, metric='Number of Fatalities'):
    """Création du heatmap plot visibilité vs trafic"""
    df['Visibility Level'] = pd.qcut(df['Visibility Level'], q=5, labels=['Très faible', 'Faible', 'Moyenne', 'Bonne', 'Très bonne'])
    df['Traffic Volume'] = pd.qcut(df['Traffic Volume'], q=5, labels=['Très faible', 'Faible', 'Moyen', 'Forte', 'Très forte'])
    visibility_order = ['Très bonne', 'Bonne', 'Moyenne', 'Faible', 'Très faible']
    df['Visibility Level'] = pd.Categorical(df['Visibility Level'], categories=visibility_order, ordered=True)
    
    heatmap_data = df.pivot_table(
        index='Visibility Level',
        columns='Traffic Volume',
        values= metric,
        aggfunc='sum'
    ).fillna(0)
    
    fig = px.imshow(
        heatmap_data,
        color_continuous_scale='Reds' if metric == "Number of Fatalities" else 'Blues'
    )
    return style_chart(fig)

def create_road_conditions_pie(df, metric='Number of Fatalities'):
    """Création du diagramme en secteurs des conditions routières"""
    road_conditions = df.groupby('Road Condition').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = px.pie(
        road_conditions,
        values=metric,
        names='Road Condition'
    )
    return style_chart(fig)

def create_weather_road_radar(df, metric='Number of Fatalities'):
    """Création du graphique radar conditions météo et routières"""
    radar_data = df.groupby(['Weather Conditions', 'Road Condition']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    
    for weather in radar_data['Weather Conditions'].unique():
        weather_data = radar_data[radar_data['Weather Conditions'] == weather]
        fig.add_trace(go.Scatterpolar(
            r=weather_data[metric],
            theta=weather_data['Road Condition'],
            name=weather,
            fill='toself'
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, radar_data[metric].max()]))
    )
    return style_chart(fig)

def render_environment_page():
    """
    Affiche la page d'analyse environnementale des accidents avec une interface améliorée
    """
    # En-tête avec contexte
    st.title("🌤️ Analyse Environnementale des Accidents")
    st.markdown("""
        Explorez l'impact des conditions environnementales sur les accidents : météo, état des routes, 
        visibilité et conditions de circulation.
        Utilisez les filtres dans la barre latérale pour affiner votre analyse.
    """)

    # Chargement des données avec indicateur de progression
    with st.spinner("Chargement des données..."):
        df = load_data()
        if df is None:
            st.error("❌ Erreur lors du chargement des données.")
            return

    # Application des filtres
    filters = render_filters()
    filtered_df = filter_data(df, filters)

    # Conteneur pour les métriques environnementales clés
    with st.container():
        cols = st.columns(4)
        
        with cols[0]:
            pct_bad_weather = (filtered_df['Weather Conditions'].isin(['Rainy', 'Snowy', 'Foggy']).sum() / len(filtered_df) * 100)
            st.metric(
                "Mauvais temps",
                f"{pct_bad_weather:.1f}%",
                help="Pourcentage d'accidents par mauvais temps (pluie, neige, brouillard)"
            )
        
        with cols[1]:
            pct_poor_visibility = (filtered_df['Visibility Level'] < 100).sum() / len(filtered_df) * 100
            st.metric(
                "Visibilité réduite",
                f"{pct_poor_visibility:.1f}%",
                help="Pourcentage d'accidents avec visibilité réduite (<100m)"
            )
        
        with cols[2]:
            pct_bad_road = (filtered_df['Road Condition'].isin(['Wet', 'Icy', 'Snow-covered']).sum() / len(filtered_df) * 100)
            st.metric(
                "Routes dégradées",
                f"{pct_bad_road:.1f}%",
                help="Pourcentage d'accidents sur routes dégradées"
            )
        
        with cols[3]:
            avg_traffic = filtered_df['Traffic Volume'].mean()
            st.metric(
                "Volume trafic moyen",
                f"{avg_traffic:.1f}",
                help="Volume moyen du trafic lors des accidents"
            )

    # Sélection de métrique avec description
    st.subheader("📊 Analyse des facteurs environnementaux", anchor=False)
    metric = st.radio(
        "Choisissez une métrique à visualiser :",
        options=["Number of Fatalities", "Number of Injuries"],
        format_func=lambda x: "Nombre de décès" if x == "Number of Fatalities" else "Nombre de blessés",
        horizontal=True,
        help="Sélectionnez la métrique à afficher sur les graphiques"
    )

    # Disposition des visualisations en onglets
    tab1, tab2 = st.tabs(["🌍 Conditions générales", "🔍 Analyse détaillée"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Graphique routes vs météo avec titre explicatif
            st.markdown("#### 🌧️ Impact météo et état des routes")
            road_weather = create_road_weather_bar(filtered_df, metric)
            st.plotly_chart(road_weather, use_container_width=True)
        
        with col2:
            # Heatmap visibilité vs trafic avec contexte
            st.markdown("#### 👁️ Visibilité et densité du trafic")
            visibility_traffic = create_visibility_traffic_heatmap(filtered_df, metric)
            st.plotly_chart(visibility_traffic, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Diagramme conditions routières avec contexte
            st.markdown("#### 🛣️ Répartition des conditions routières")
            road_conditions = create_road_conditions_pie(filtered_df, metric)
            st.plotly_chart(road_conditions, use_container_width=True)
        
        with col2:
            # Graphique radar avec explications
            st.markdown("#### 📊 Vue d'ensemble des facteurs")
            weather_road_radar = create_weather_road_radar(filtered_df, metric)
            st.plotly_chart(weather_road_radar, use_container_width=True)

    # Statistiques détaillées dans un expander
    with st.expander("📈 Statistiques environnementales détaillées", expanded=False):
        # Création d'un tableau croisé
        env_stats = pd.crosstab(
            filtered_df['Weather Conditions'],
            filtered_df['Road Condition'],
            values=filtered_df[metric],
            aggfunc='sum'
        ).round(2)
        
        # Affichage avec formatage
        st.dataframe(
            env_stats,
            use_container_width=True,
            hide_index=False,
        )
        
        # Bouton de téléchargement
        csv = env_stats.to_csv()
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="statistiques_environnementales.csv",
            mime="text/csv",
        )