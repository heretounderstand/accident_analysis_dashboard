import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart
from ..components.filters import render_filters

def create_speed_histogram(df):
    """Création de l'histogramme des limitations de vitesse"""
    fig = px.histogram(
        df,
        x='Speed Limit',
        nbins=20
    )
    fig.update_layout(
        xaxis_title="Limitation de vitesse (km/h)",
        yaxis_title="Nombre d'accidents",
        bargap=0.1
    )
    return style_chart(fig)

def create_vehicle_condition_pie(df, metric='Number of Fatalities'):
    """Création du diagramme en secteurs des conditions des véhicules"""
    condition_data = df.groupby('Vehicle Condition').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    fig = px.pie(
        condition_data,
        values=metric,
        names='Vehicle Condition'
    )
    return style_chart(fig)

def create_speed_condition_combined(df, metric='Number of Fatalities'):
    """Création du graphique combiné vitesse/condition"""
    fig = px.box(
        df,
        x='Vehicle Condition',
        y='Speed Limit',
        color='Vehicle Condition'
    )
    
    # Ajout de la moyenne des accidents
    avg_accidents = df.groupby('Vehicle Condition')[metric].mean()
    
    fig.add_trace(
        go.Scatter(
            x=avg_accidents.index,
            y=avg_accidents.values,
            mode='lines+markers',
            name='Moyenne des accidents',
            yaxis='y2'
        )
    )
    
    fig.update_layout(
        yaxis2=dict(
            overlaying='y',
            side='right'
        )
    )
    
    return style_chart(fig)

def render_vehicle_page():
    """
    Affiche la page d'analyse des facteurs liés aux véhicules
    """
    st.title("🚗 Analyse des Véhicules")
    st.markdown("""
        Explorez les caractéristiques des véhicules impliqués dans les accidents : 
        état technique et limites de vitesse associées.
        Utilisez les filtres dans la barre latérale pour affiner votre analyse.
    """)

    # Chargement des données
    with st.spinner("Chargement des données..."):
        df = load_data()
        if df is None:
            st.error("❌ Erreur lors du chargement des données.")
            return

    # Application des filtres
    filters = render_filters()
    filtered_df = filter_data(df, filters)

    # Métriques clés
    with st.container():
        cols = st.columns(4)
        
        with cols[0]:
            avg_speed_limit = filtered_df['Speed Limit'].mean()
            st.metric(
                "Limite de vitesse moyenne",
                f"{avg_speed_limit:.1f} km/h",
                help="Limite de vitesse moyenne sur les zones d'accident"
            )
        
        with cols[1]:
            most_common_condition = filtered_df['Vehicle Condition'].mode()[0]
            condition_pct = (filtered_df['Vehicle Condition'] == most_common_condition).sum() / len(filtered_df) * 100
            st.metric(
                "État le plus fréquent",
                most_common_condition,
                f"{condition_pct:.1f}% du total",
                help="État des véhicules le plus fréquent",
                delta_color="inverse" if most_common_condition == "Poor" else "normal"
            )
        
        with cols[2]:
            pct_speeding = (filtered_df['Accident Cause'].str.contains('Speeding', na=False)).sum() / len(filtered_df) * 100
            st.metric(
                "Excès de vitesse",
                f"{pct_speeding:.1f}%",
                help="Pourcentage d'accidents impliquant un excès de vitesse"
            )
        
        with cols[3]:
            pct_poor_condition = (filtered_df['Accident Cause'].str.contains('Mechanical Failure', na=False)).sum() / len(filtered_df) * 100
            st.metric(
                "Déficience technique",
                f"{pct_poor_condition:.1f}%",
                help="Pourcentage d'accidents liés à un état technique déficient"
            )

    # Sélection de métrique
    st.subheader("📊 Analyse des caractéristiques", anchor=False)
    metric = st.radio(
        "Choisissez une métrique à visualiser :",
        options=["Number of Fatalities", "Number of Injuries"],
        format_func=lambda x: "Nombre de décès" if x == "Number of Fatalities" else "Nombre de blessés",
        horizontal=True,
        help="Sélectionnez la métrique à afficher sur les graphiques"
    )

    # Organisation en onglets
    tab1, tab2 = st.tabs(["🚦 Limites de vitesse", "🔧 État des véhicules"])
    
    with tab1:
        st.markdown("#### 🏁 Distribution des limites de vitesse")
        speed_hist = create_speed_histogram(filtered_df)
        st.plotly_chart(speed_hist, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🚗 État technique des véhicules")
            vehicle_condition = create_vehicle_condition_pie(filtered_df, metric)
            st.plotly_chart(vehicle_condition, use_container_width=True)
        
        with col2:
            st.markdown("#### 📊 Impact de la vitesse selon les conditions")
            speed_condition = create_speed_condition_combined(filtered_df, metric)
            st.plotly_chart(speed_condition, use_container_width=True)
        
        
    with st.expander("📈 Statistiques par état des véhicules"):
        vehicle_stats = filtered_df.groupby('Vehicle Condition').agg({
            'Number of Fatalities': ['sum', 'mean'],
            'Number of Injuries': ['sum', 'mean'],
            'Speed Limit': 'mean'
        }).round(2)
            
        vehicle_stats.columns = [
            'Décès totaux', 'Décès moyens',
            'Blessés totaux', 'Blessés moyens',
            'Limite de vitesse moyenne'
        ]
            
        st.dataframe(vehicle_stats)
            
        csv = vehicle_stats.to_csv()
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="statistiques_vehicules.csv",
            mime="text/csv",
        )
