import streamlit as st
import sys
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
sys.path.append(str(Path(__file__).parent))

from src.config import APP_TITLE, APP_SUBTITLE
from src.components.filters import render_filters, display_active_filters
from src.data_loader import load_data, filter_data
from src.utils.data_processing import calculate_summary_stats

# Configuration de la page
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
        .main * {
            font-family: 'Roboto', sans-serif !important;
        }
        .stApp {
            background-color: #F0F2F6;
        }
        .stSidebar {
            background-color: white;
        }
        .stButton>button {
            background-color: #FF4B4B;
            color: white;
        }
        .stButton>button:hover {
            background-color: #FF6B6B;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

def main():

    # Titre avec style personnalisé
    st.markdown(f"""
        <h1 style='text-align: center;'>{APP_TITLE}</h1>
        <p style='text-align: center; font-style: italic;'>{APP_SUBTITLE}</p>
    """, unsafe_allow_html=True)

    # Chargement des données avec spinner
    with st.spinner("Chargement des données en cours..."):
        df = load_data()

    if df is None:
        st.error("🚫 Erreur lors du chargement des données. Veuillez vérifier le fichier de données.")
        return

    # Conteneur pour les filtres avec style
    with st.expander("🔍 Filtres de recherche", expanded=True):
        filters = render_filters()

    # Application des filtres
    filtered_df = filter_data(df, filters)

    # Affichage des filtres actifs dans un conteneur stylisé
    st.markdown("### 📋 Filtres actifs")
    display_active_filters()

    # Calcul des statistiques
    stats = calculate_summary_stats(filtered_df)
    
    

    # Métriques principales avec icônes et couleurs
    st.markdown("### 📊 Statistiques principales")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚗 Total des accidents",
            value=f"{stats['total_accidents']:,}",
            delta=f"{((stats['total_accidents'] / len(df)) * 100):.1f}% du total",
            delta_color="inverse"
        )

    with col2:
        st.metric(
            label="⚠️ Décès",
            value=f"{stats['total_fatalities']:,}",
            delta=f"{(stats['total_fatalities'] / stats['total_accidents']):.1f} par accident",
            delta_color="inverse"
        )

    with col3:
        st.metric(
            label="🏥 Blessés",
            value=f"{stats['total_injuries']:,}",
            delta=f"{(stats['total_injuries'] / stats['total_accidents']):.1f} par accident",
            delta_color="inverse"
        )

    with col4:
        st.metric(
            label="⏱️ Temps de réponse moyen",
            value=f"{stats['avg_response_time']:.1f} min",
            delta=f"{stats['avg_response_time'] - df['Emergency Response Time'].mean():.1f} min",
            delta_color="inverse"
        )

    # Séparateur stylisé
    st.markdown("<hr style='border: 2px solid #f0f2f6; margin: 2em 0;'>", unsafe_allow_html=True)

    # Pertes économiques avec formatage monétaire
    st.metric(
        label="💶 Pertes économiques totales",
        value=f"{stats['total_economic_loss']:,.2f} $",
        delta=f"{((stats['total_economic_loss'] / df['Economic Loss'].sum()) * 100):.1f}% du total",
        delta_color="inverse"
    )

    # Ajout d'informations contextuelles
    with st.expander("ℹ️ Informations sur les métriques"):
        st.markdown("""
        - Le pourcentage est calculé par rapport au total des accidents
        - Le temps de réponse moyen est comparé à la moyenne globale
        - Les pertes économiques sont exprimées en $
        """)

if __name__ == "__main__":
    main()