import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart
from ..components.filters import render_filters

def create_age_gender_pyramid(df, metric='Number of Fatalities'):
    """Création de la pyramide des âges par genre"""
    driver_age_order = ['<18', '18-25', '26-40', '41-60', '61+']
    df['Driver Age Group'] = pd.Categorical(df['Driver Age Group'], categories=driver_age_order, ordered=True)
    age_gender_data = df.groupby(['Driver Age Group', 'Driver Gender']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()
    
    # Inverser les valeurs pour un genre pour créer la pyramide
    age_gender_data.loc[age_gender_data['Driver Gender'] == 'Male', metric] *= -1

    # Définir la palette en fonction du metric actuel
    palette = px.colors.sequential.Reds if metric == 'Number of Fatalities' else px.colors.sequential.Blues
    
    fig = go.Figure()
    for gender in ['Female', 'Male']:
        data = age_gender_data[age_gender_data['Driver Gender'] == gender]
        color = palette[2] if gender == 'Male' else palette[6] 
        fig.add_trace(go.Bar(
            name=gender,
            y=data['Driver Age Group'],
            x=data[metric],
            orientation='h',
            marker=dict(color=color)
        ))
    
    fig.update_layout(
        barmode='overlay',
        bargap=0.1
    )
    
    return style_chart(fig)

def create_alcohol_age_box(df):
    """Création du box plot alcoolémie par groupe d'âge"""
    fig = px.box(
        df,
        x='Driver Age Group',
        y='Driver Alcohol Level',
        color='Driver Age Group'
    )
    return style_chart(fig)

def create_fatigue_stack(df, metric='Number of Fatalities'):
    """Création du graphique en barres empilées de la fatigue"""
    driver_age_order = ['<18', '18-25', '26-40', '41-60', '61+']
    df['Driver Age Group'] = pd.Categorical(df['Driver Age Group'], categories=driver_age_order, ordered=True)
    fatigue_data = df.groupby(['Driver Age Group', 'Driver Gender', 'Driver Fatigue']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum'
    }).reset_index()

    # Attribution des couleurs : nuance claire pour Female, plus foncée pour Male
    palette = px.colors.sequential.Reds if metric == 'Number of Fatalities' else px.colors.sequential.Blues
    color_discrete_map = {
        'Male': palette[2],  # Nuance claire
        'Female': palette[6]      # Nuance plus foncée
    }
    
    fig = px.bar(
        fatigue_data,
        x='Driver Age Group',
        y=metric,
        color='Driver Gender',
        facet_col='Driver Fatigue',
        color_discrete_map=color_discrete_map
    )
    return style_chart(fig)

def create_driver_treemap(df, metric='Number of Fatalities'):
    """Création du treemap des facteurs conducteurs"""
    treemap_data = df.groupby([
        'Driver Age Group', 'Driver Gender', 'Driver Fatigue'
    ]).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum',
        'Driver Alcohol Level': 'mean'
    }).reset_index()
    
    fig = px.treemap(
        treemap_data,
        path=['Driver Age Group', 'Driver Gender', 'Driver Fatigue'],
        values=metric,
        color='Driver Alcohol Level',
        color_continuous_scale='Reds' if metric == "Number of Fatalities" else 'Blues'
    )
    return style_chart(fig)

def render_driver_page():
    """
    Affiche la page d'analyse des facteurs liés aux conducteurs avec une interface améliorée
    """
    # En-tête avec contexte
    st.title("👥 Analyse des Facteurs liés aux Conducteurs")
    st.markdown("""
        Explorez le profil des conducteurs impliqués dans les accidents et analysez 
        l'impact des facteurs humains : âge, genre, fatigue, alcool...
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

    # Conteneur pour les métriques clés sur les conducteurs
    with st.container():
        cols = st.columns(4)
        
        with cols[0]:
            avg_age = filtered_df['Driver Age Group'].mode()[0]
            st.metric(
                "Groupe d'âge moyen",
                f"{str(avg_age)}",
                help="Groupe d'âge moyen des conducteurs impliqués"
            )
        
        with cols[1]:
            pct_male = (filtered_df['Driver Gender'] == 'Male').sum() / len(filtered_df) * 100
            st.metric(
                "Conducteurs hommes",
                f"{pct_male:.1f}%",
                help="Pourcentage de conducteurs masculins"
            )
        
        with cols[2]:
            pct_alcohol = filtered_df['Driver Alcohol Level'].mean()
            st.metric(
                "Alcoolémie moyenne",
                f"{pct_alcohol:.1f}",
                help="Alcoolémie moyenne des conducteurs (0 - 0.5)"
            )
        
        with cols[3]:
            pct_fatigue = (filtered_df['Driver Fatigue'] == 1).sum() / len(filtered_df) * 100
            st.metric(
                "Conducteurs fatigués",
                f"{pct_fatigue:.1f}%",
                help="Pourcentage de conducteurs fatigués"
            )

    # Sélection de métrique avec description
    st.subheader("📊 Analyse des profils conducteurs", anchor=False)
    metric = st.radio(
        "Choisissez une métrique à visualiser :",
        options=["Number of Fatalities", "Number of Injuries"],
        format_func=lambda x: "Nombre de décès" if x == "Number of Fatalities" else "Nombre de blessés",
        horizontal=True,
        help="Sélectionnez la métrique à afficher sur les graphiques"
    )

    # Organisation en onglets thématiques
    tab1, tab2 = st.tabs(["📊 Démographie", "🚗 Facteurs de risque"])
    
    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            # Pyramide des âges avec contexte
            st.markdown("#### 👥 Distribution par âge et genre")
            age_gender = create_age_gender_pyramid(filtered_df, metric)
            st.plotly_chart(age_gender, use_container_width=True)
            
        with col2:
            # Treemap avec facteurs multiples
            st.markdown("#### 🎯 Vue d'ensemble des facteurs conducteur")
            driver_tree = create_driver_treemap(filtered_df, metric)
            st.plotly_chart(driver_tree, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot alcoolémie avec contexte
            st.markdown("#### 🍷 Alcoolémie par groupe d'âge")
            alcohol_box = create_alcohol_age_box(filtered_df)
            st.plotly_chart(alcohol_box, use_container_width=True)
            
        with col2:
            # Graphique fatigue avec contexte
            st.markdown("#### 😴 Impact de la fatigue")
            fatigue_stack = create_fatigue_stack(filtered_df, metric)
            st.plotly_chart(fatigue_stack, use_container_width=True)

    # Statistiques détaillées
    with st.expander("📈 Statistiques détaillées conducteurs", expanded=False):
        # Création d'un tableau croisé avancé
        driver_stats = pd.pivot_table(
            filtered_df,
            values=[metric, 'Driver Alcohol Level', 'Driver Fatigue'],
            index=['Driver Age Group', 'Driver Gender'],
            aggfunc={
                metric: 'sum',
                'Driver Alcohol Level': 'mean',
                'Driver Fatigue': 'mean'
            }
        ).round(2)
        
        # Réinitialiser l'index pour transformer les colonnes d'index en colonnes normales
        driver_stats = driver_stats.reset_index()
        
        # Affichage avec formatage
        st.dataframe(
            driver_stats,
            use_container_width=True,
            hide_index=False,
        )
        
        # Bouton de téléchargement
        csv = driver_stats.to_csv()
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="statistiques_conducteurs.csv",
            mime="text/csv",
        )
