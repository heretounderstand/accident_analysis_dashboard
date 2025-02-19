import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart, create_time_series
from ..components.filters import render_filters
from statsmodels.tsa.seasonal import seasonal_decompose
from ..config import THEME_CONFIG

def create_timeline(df, metric='Number of Fatalities'):
    """Création de la ligne temporelle interactive"""
    time_data = df.groupby(['Year', 'Month']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()

    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
        
    time_data.index = pd.to_datetime(time_data['Year'].astype(str) + '-' + time_data['Month'].map(month_map).astype(str) + '-01')
    time_data = time_data.sort_index()
    
    fig = create_time_series(
        time_data,
        x_col=time_data.index,
        y_col=metric,
        color= THEME_CONFIG['secondary'] if metric == "Number of Injuries" else THEME_CONFIG['primary']
    )
    return fig

def create_weekly_hourly_heatmap(df, metric='Number of Fatalities'):
    """Création de la heatmap jour/heure"""
    time_order = ["Morning", "Afternoon", "Evening", "Night"]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    df["Day of Week"] = pd.Categorical(df["Day of Week"], categories=day_order, ordered=True)
    df["Time of Day"] = pd.Categorical(df["Time of Day"], categories=time_order, ordered=True)
    heatmap_data = df.pivot_table(
        index='Day of Week',
        columns='Time of Day',
        values= metric,
        aggfunc='sum'
    ).fillna(0)
    
    fig = px.imshow(
        heatmap_data,
        color_continuous_scale='Reds' if metric == "Number of Fatalities" else 'Blues'
    )
    return style_chart(fig)

def create_monthly_distribution(df):
    """Création du graphique en barres cyclique mensuel"""
    month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    monthly_data = df.groupby('Month').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Number of Injuries'],
        name='Blessés',
        marker_color=THEME_CONFIG['secondary']
    ))

    fig.add_trace(go.Bar(
        x=monthly_data['Month'],
        y=monthly_data['Number of Fatalities'],
        name='Décès',
        marker_color=THEME_CONFIG['primary']
    ))

    # Mise en page pour empiler les barres
    fig.update_layout(
        barmode='stack',  # Mode empilé
        xaxis_title="Mois",
        yaxis_title="Nombre de cas",
        legend_title="Type d'accident"
    )
    return style_chart(fig)

def create_temporal_decomposition(df):
    """Création de la décomposition temporelle"""
    # Préparation des données temporelles
    time_series = df.groupby(['Year', 'Month']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
        
    time_series.index = pd.to_datetime(time_series['Year'].astype(str) + '-' + time_series['Month'].map(month_map).astype(str) + '-01')
    time_series = time_series.sort_index()


    # Décomposition
    decomposition = seasonal_decompose(
        time_series["Number of Fatalities"] + time_series["Number of Injuries"],
        period=12
    )
    
    # Création du graphique
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_series.index,
        y=decomposition.seasonal,
        name='Saisonnalité'
    ))
    fig.add_trace(go.Scatter(
        x=time_series.index,
        y=decomposition.resid,
        name='Résidus'
    ))
    fig.add_trace(go.Scatter(
        x=time_series.index,
        y=decomposition.trend,
        name='Tendance'
    ))
    
    fig.update_layout(xaxis_title='Date',
                      yaxis_title='Nombre de cas')
    return style_chart(fig)

def render_temporal_page():
    """
    Affiche la page d'analyse temporelle des accidents avec une interface améliorée
    """
    # En-tête avec contexte
    st.title("⏳ Analyse Temporelle des Accidents")
    st.markdown("""
        Explorez l'évolution des accidents dans le temps et identifiez les tendances et motifs temporels.
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
    
    # Conteneur pour les métriques temporelles clés
    with st.container():
        cols = st.columns(4)
        
        # Calcul des variations sur la période
        current_year = filtered_df['Date'].max()
        previous_year = current_year - pd.DateOffset(years=1)
        current_data = filtered_df[filtered_df['Date'].dt.year == current_year.year]
        previous_data = filtered_df[filtered_df['Date'].dt.year == previous_year.year]
        
        with cols[0]:
            variation_accidents = ((len(current_data) - len(previous_data)) / len(previous_data) * 100
                                 if len(previous_data) > 0 else 0)
            st.metric(
                "Accidents 2024",
                f"{len(current_data):,}",
                f"{variation_accidents:+.1f}%",
                help="Nombre d'accidents de 2024 et variation par rapport à 2023",
                delta_color='inverse'
            )
        
        with cols[1]:
            current_fatalities = current_data['Number of Fatalities'].sum()
            previous_fatalities = previous_data['Number of Fatalities'].sum()
            variation_fatalities = ((current_fatalities - previous_fatalities) / previous_fatalities * 100
                                  if previous_fatalities > 0 else 0)
            st.metric(
                "Décès 2024",
                f"{current_fatalities:,}",
                f"{variation_fatalities:+.1f}%",
                help="Nombre de décès de 2024 et variation par rapport à 2023",
                delta_color='inverse'
            )
        
        with cols[2]:
            current_injuries = current_data['Number of Injuries'].sum()
            previous_injuries = previous_data['Number of Injuries'].sum()
            variation_injuries = ((current_injuries - previous_injuries) / previous_injuries * 100
                                if previous_injuries > 0 else 0)
            st.metric(
                "Blessés 2024",
                f"{current_injuries:,}",
                f"{variation_injuries:+.1f}%",
                help="Nombre de blessés de 2024 et variation par rapport à 2023",
                delta_color='inverse'
            )
        
        with cols[3]:
            avg_response_time = filtered_df['Emergency Response Time'].mean()
            st.metric(
                "Temps de réponse moyen",
                f"{avg_response_time:.1f} min",
                help="Temps moyen d'intervention des secours"
            )

        
    # Sélection de métrique avec description
    st.subheader("📊 Visualisation des tendances", anchor=False)
    
    metric = st.radio(
        "Choisissez une métrique à visualiser :",
        options=["Number of Fatalities", "Number of Injuries"],
        format_func=lambda x: "Nombre de décès" if x == "Number of Fatalities" else "Nombre de blessés",
        horizontal=True,
        help="Sélectionnez la métrique à afficher sur les graphiques"
    )
    
    # Disposition des visualisations en onglets
    tab1, tab2 = st.tabs(["📊 Tendances globales", "⏰ Patterns temporels"])
    
    with tab1:
        # Ligne temporelle principale
        st.markdown("#### 📈 Évolution temporelle")
        timeline = create_timeline(filtered_df, metric)
        st.plotly_chart(timeline, use_container_width=True)
        
        # Décomposition temporelle
        st.markdown("#### 🔍 Décomposition temporelle détaillée")    
        st.markdown("""
            Cette visualisation décompose la série temporelle en ses composantes :
            - **Tendance** : évolution à long terme
            - **Saisonnalité** : motifs cycliques
            - **Résidus** : variations inexpliquées
        """)
        decomposition = create_temporal_decomposition(filtered_df)
        st.plotly_chart(decomposition, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Distribution mensuelle")
            monthly_dist = create_monthly_distribution(filtered_df)
            st.plotly_chart(monthly_dist, use_container_width=True)
        
        with col2:
            st.markdown("#### 🕒 Heatmap jour/heure")
            heatmap = create_weekly_hourly_heatmap(filtered_df, metric)
            st.plotly_chart(heatmap, use_container_width=True)

    # Statistiques temporelles additionnelles
    with st.expander("📈 Statistiques temporelles", expanded=False):

        # Calcul des statistiques par période
        time_stats = filtered_df.groupby(pd.Grouper(key='Date', freq='M')).agg({
            'Number of Fatalities': ['sum', 'mean'],
            'Number of Injuries': ['sum', 'mean'],
            'Emergency Response Time': 'mean'
        }).round(2)
        
        # Formatage du tableau
        time_stats.columns = ['Décès (total)', 'Décès (moy/jour)', 
                            'Blessés (total)', 'Blessés (moy/jour)',
                            'Temps réponse moyen (min)']
        
        # Affichage du tableau
        st.dataframe(
            time_stats,
            use_container_width=True,
            column_config={
                "Temps réponse moyen (min)": st.column_config.NumberColumn(format="%.1f")
            }
        )

        # Bouton de téléchargement
        csv = time_stats.to_csv()
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="statistiques_temporelles.csv",
            mime="text/csv",
        )