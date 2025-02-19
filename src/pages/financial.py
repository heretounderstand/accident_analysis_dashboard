from matplotlib import pyplot as plt
import pandas as pd
import streamlit as st
import plotly.express as px
from ..data_loader import load_data, filter_data
from ..utils.viz_helpers import style_chart
from ..components.filters import render_filters

def create_cost_severity_box(df):
    """Création des boîtes à moustaches des coûts médicaux par sévérité"""
    fig = px.box(
        df,
        x='Accident Severity',
        y='Medical Cost',
        color='Accident Severity',
    )
    fig.update_layout(
        yaxis_title="Coût médical ($)",
        xaxis_title="Niveau de sévérité"
    )
    return style_chart(fig)

def create_economic_loss_area(df):
    """Création du graphique en aires empilées des pertes économiques"""
    time_data = df.groupby(['Year', 'Month', 'Accident Severity']).agg({
        'Economic Loss': 'sum'
    }).reset_index()
    
    fig = px.area(
        time_data,
        x='Year',
        y='Economic Loss',
        color='Accident Severity',
    )
    fig.update_layout(
        yaxis_title="Pertes économiques ($)",
        xaxis_title="Année"
    )
    return style_chart(fig)

def create_insurance_medical_treemap(df):
    """Création du treemap assurance vs coûts médicaux"""
    fig = px.treemap(
        df,
        path=['Insurance Claims', 'Accident Severity'],
        values='Medical Cost',
        color='Medical Cost',
    )
    return style_chart(fig)

def create_economic_density(df):
    """Création du heatmap pertes/densité/accidents"""
    df['Population Density'] = pd.qcut(df['Population Density'], q=5, labels=['Très faible', 'Faible', 'Moyen', 'Forte', 'Très forte'])
    heatmap_data = df.pivot_table(
        index='Population Density',
        columns='Accident Severity',
        values= 'Economic Loss',
        aggfunc='sum'
    ).fillna(0)
    
    fig = px.imshow(
        heatmap_data,
    )
    return style_chart(fig)

def render_financial_page():
    """
    Affiche la page d'analyse de l'impact financier avec une interface améliorée
    """
    # En-tête avec contexte
    st.title("💰 Analyse de l'Impact Financier")
    st.markdown("""
        Explorez l'impact financier des accidents : coûts médicaux, pertes économiques, 
        réclamations d'assurance et analyse des tendances.
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

    # Conteneur pour les KPIs financiers principaux
    st.markdown("#### 📊 Indicateurs financiers clés")
    with st.container():
        total_cost = filtered_df['Medical Cost'].sum()
        total_loss = filtered_df['Economic Loss'].sum()
        total_claims = filtered_df['Insurance Claims'].sum()
        previous_period = filtered_df['Date'].max() - pd.DateOffset(months=1)
        previous_df = filtered_df[filtered_df['Date'] <= previous_period]
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        with kpi1:
            variation = ((total_cost - previous_df['Medical Cost'].sum()) / previous_df['Medical Cost'].sum() * 100)
            st.metric(
                "Coûts médicaux totaux",
                f"${total_cost:,.0f}",
                f"{variation:+.1f}% vs mois préc.",
                help="Total des coûts médicaux et variation mensuelle",
                delta_color='inverse'
            )
        
        with kpi2:
            variation = ((total_loss - previous_df['Economic Loss'].sum()) / previous_df['Economic Loss'].sum() * 100)
            st.metric(
                "Pertes économiques",
                f"${total_loss:,.0f}",
                f"{variation:+.1f}% vs mois préc.",
                help="Total des pertes économiques et variation mensuelle",
                delta_color='inverse'
            )
        
        with kpi3:
            variation = ((total_claims - previous_df['Insurance Claims'].sum()) / previous_df['Insurance Claims'].sum() * 100)
            st.metric(
                "Réclamations assurance",
                f"${total_claims:,.0f}",
                f"{variation:+.1f}% vs mois préc.",
                help="Total des réclamations d'assurance et variation mensuelle",
                delta_color='inverse'
            )
        
        with kpi4:
            avg_cost = total_cost / len(filtered_df)
            prev_avg = previous_df['Medical Cost'].sum() / len(previous_df)
            variation = ((avg_cost - prev_avg) / prev_avg * 100)
            st.metric(
                "Coût moyen par accident",
                f"${avg_cost:,.0f}",
                f"{variation:+.1f}% vs mois préc.",
                help="Coût moyen par accident et variation mensuelle",
                delta_color='inverse'
            )

    # Organisation en onglets thématiques
    tab1, tab2 = st.tabs(["📈 Analyse des coûts", "💹 Impact économique"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Boîtes à moustaches coûts/sévérité avec contexte
            st.markdown("#### 📊 Distribution des coûts par sévérité")
            cost_severity = create_cost_severity_box(filtered_df)
            st.plotly_chart(cost_severity, use_container_width=True)
        
        with col2:
            # Treemap assurance/coûts avec contexte
            st.markdown("#### 🌳 Répartition des coûts et assurances")
            insurance_medical = create_insurance_medical_treemap(filtered_df)
            st.plotly_chart(insurance_medical, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Heatmap pertes économiques avec contexte
            st.markdown("#### 🔥 Évolution des pertes économiques")
            economic_loss = create_economic_loss_area(filtered_df)
            st.plotly_chart(economic_loss, use_container_width=True)
        
        with col2:
            # Graphique bulles économique/densité avec contexte
            st.markdown("#### 🎯 Impact vs Densité urbaine")
            economic_density = create_economic_density(filtered_df)
            st.plotly_chart(economic_density, use_container_width=True)

    # Analyses détaillées dans un expander
    with st.expander("📈 Analyses financières détaillées", expanded=False):
        # Création d'un tableau croisé avancé
        financial_analysis = pd.pivot_table(
            filtered_df,
            values=['Medical Cost', 'Economic Loss', 'Insurance Claims'],
            index=['Accident Severity', 'Region'],
            aggfunc={
                'Medical Cost': ['mean', 'sum'],
                'Economic Loss': ['mean', 'sum'],
                'Insurance Claims': ['count', 'mean', 'sum']
            }
        ).round(2)
        
        st.dataframe(financial_analysis)
        
        # Bouton de téléchargement
        csv = financial_analysis.to_csv()
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="analyse_financiere.csv",
            mime="text/csv",
        )