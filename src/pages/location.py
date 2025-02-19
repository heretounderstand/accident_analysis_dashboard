import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart
from ..components.filters import render_filters
from ..config import THEME_CONFIG

def create_choropleth(df, metric='Number of Fatalities'):
    """Création de la carte choroplèthe"""
    region_data = df.groupby('Country').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()

    # Création de la colonne "ISO3" en mappant directement les valeurs
    region_data["ISO3"] = region_data["Country"].replace({
        "USA": "USA",
        "UK": "GBR",
        "Canada": "CAN",
        "India": "IND",
        "China": "CHN",
        "Japan": "JPN",
        "Russia": "RUS",
        "Brazil": "BRA",
        "Germany": "DEU",
        "Australia": "AUS"
    })
    
    fig = px.choropleth(
        region_data,
        locations='ISO3',
        color=metric,  # Mise à jour dynamique
        hover_data=['Number of Fatalities', 'Number of Injuries'],
        color_continuous_scale='Reds' if metric == "Number of Fatalities" else 'Blues',
    )
    return style_chart(fig)

def create_urban_rural_comparison(df):
    """Création du diagramme en barres urbain vs rural"""
    urban_rural_data = df.groupby('Urban/Rural').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Décès',
        x=urban_rural_data['Urban/Rural'],
        y=urban_rural_data['Number of Fatalities'],
        marker_color= THEME_CONFIG['primary']
    ))
    fig.add_trace(go.Bar(
        name='Blessés',
        x=urban_rural_data['Urban/Rural'],
        y=urban_rural_data['Number of Injuries'],
        marker_color= THEME_CONFIG['secondary']
    ))
    
    fig.update_layout(
        barmode='group'
    )
    return style_chart(fig)

def create_density_heatmap(df, metric='Number of Fatalities'):
    """Création de la carte de chaleur de densité"""
    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    df["Time of Day"] = pd.Categorical(df["Time of Day"], categories=time_order, ordered=True)
    density_data = df.pivot_table(
        index='Region',
        columns='Time of Day',
        values= metric,
        aggfunc='sum'
    ).fillna(0)
    
    fig = px.imshow(
        density_data,
        color_continuous_scale='Reds' if metric == "Number of Fatalities" else 'Blues'
    )
    return style_chart(fig)

def render_location_page():
    """
    Affiche la page d'analyse géographique des accidents avec une interface améliorée
    """
    # En-tête avec contexte
    st.title("🗺️ Analyse Géographique des Accidents")
    st.markdown("""
        Visualisez la distribution géographique des accidents et analysez les tendances par région.
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
    
    # Conteneur pour les métriques globales
    with st.container():
        cols = st.columns(4)
        with cols[0]:
            st.metric(
                "Total accidents",
                f"{len(filtered_df):,}",
                help="Nombre total d'accidents après application des filtres"
            )
        with cols[1]:
            st.metric(
                "Décès",
                f"{filtered_df['Number of Fatalities'].sum():,}",
                help="Nombre total de décès"
            )
        with cols[2]:
            st.metric(
                "Blessés",
                f"{filtered_df['Number of Injuries'].sum():,}",
                help="Nombre total de blessés"
            )
        with cols[3]:
            st.metric(
                "Perte économique",
                f"{filtered_df['Economic Loss'].sum():,.0f} €",
                help="Impact économique total estimé"
            )

    # Sélection de métrique avec description
    st.subheader("📊 Visualisation des données", anchor=False)
    metric = st.radio(
        "Choisissez une métrique à visualiser :",
        options=["Number of Fatalities", "Number of Injuries"],
        format_func=lambda x: "Nombre de décès" if x == "Number of Fatalities" else "Nombre de blessés",
        horizontal=True,
        help="Sélectionnez la métrique à afficher sur les cartes"
    )
    
    # Disposition des visualisations en onglets
    tab1, tab2 = st.tabs(["🗺️ Vue d'ensemble", "📍 Analyse territoriale"])
    
    with tab1:
        # Carte principale avec titre explicatif
        st.markdown("#### 📍 Distribution géographique")
        choropleth = create_choropleth(filtered_df, metric)
        st.plotly_chart(choropleth, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔥 Zones de concentration")
            density_map = create_density_heatmap(filtered_df, metric)
            st.plotly_chart(density_map, use_container_width=True)
        
        with col2:
            st.markdown("#### 🏘️ Comparaison Urbain/Rural")
            urban_rural = create_urban_rural_comparison(filtered_df)
            st.plotly_chart(urban_rural, use_container_width=True)

    # Statistiques régionales dans un conteneur déroulant
    with st.expander("📈 Statistiques détaillées par région", expanded=False):
        # Calcul des statistiques avec pourcentages
        region_stats = filtered_df.groupby('Region').agg({
            'Number of Fatalities': 'sum',
            'Number of Injuries': 'sum',
            'Economic Loss': 'sum'
        }).round(2)
        
        # Ajout des pourcentages
        region_stats['% Décès'] = (region_stats['Number of Fatalities'] / region_stats['Number of Fatalities'].sum() * 100).round(1)
        region_stats['% Blessés'] = (region_stats['Number of Injuries'] / region_stats['Number of Injuries'].sum() * 100).round(1)
        
        # Renommage des colonnes pour l'affichage
        region_stats.columns = ['Décès', 'Blessés', 'Perte économique (€)', '% Décès', '% Blessés']
        
        # Formatage des valeurs monétaires
        region_stats['Perte économique (€)'] = region_stats['Perte économique (€)'].apply(lambda x: f"{x:,.0f}")
        
        # Affichage du tableau avec style
        st.dataframe(
            region_stats,
            use_container_width=True,
            hide_index=False,
            column_config={
                "Décès": st.column_config.NumberColumn(help="Nombre total de décès par région"),
                "Blessés": st.column_config.NumberColumn(help="Nombre total de blessés par région"),
                "% Décès": st.column_config.NumberColumn(help="Pourcentage des décès totaux", format="%.1f%%"),
                "% Blessés": st.column_config.NumberColumn(help="Pourcentage des blessés totaux", format="%.1f%%"),
            }
        )

        # Téléchargement des données
        csv = region_stats.to_csv(index=True)
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="statistiques_regionales.csv",
            mime="text/csv",
        )