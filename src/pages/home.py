import streamlit as st
from ..data_loader import load_data

def set_page_config():
    st.set_page_config(
        page_title="Analyse des Accidents de la Route",
        page_icon="🏠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def apply_custom_css():
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E3D59;
            padding-bottom: 1rem;
            border-bottom: 2px solid #E8E8E8;
            margin-bottom: 2rem;
        }
        .section-header {
            color: #2E5077;
            font-size: 1.8rem;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        .stat-card {
            background-color: #F5F7F9;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .description-text {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #444444;
        }
        .highlight-box {
            background-color: #E8F4F9;
            padding: 1.5rem;
            border-left: 4px solid #2E5077;
            border-radius: 0 5px 5px 0;
            margin: 1rem 0;
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    st.markdown('<h1 class="main-header">Analyse des Accidents de la Route</h1>', unsafe_allow_html=True)

def render_description():
    st.markdown("""
        <div class="description-text">
            <p>Cette application propose une analyse approfondie des accidents de la route dans le monde, 
            permettant d'identifier les tendances clés et les facteurs de risque pour améliorer la sécurité routière.</p>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("En savoir plus sur cette étude"):
        st.markdown("""
            <div class="highlight-box">
                <h4>Notre analyse couvre les aspects suivants :</h4>
                <ul>
                    <li>🌍 Localisation et géographie des accidents</li>
                    <li>⏰ Caractéristiques temporelles</li>
                    <li>🛣️ Conditions routières et environnementales</li>
                    <li>👤 Facteurs liés aux conducteurs</li>
                    <li>🚗 Caractéristiques des véhicules</li>
                    <li>💶 Impact financier</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

def render_metrics(df):
    st.markdown('<h2 class="section-header">Indicateurs Clés</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    metrics = [
        {
            "title": "Total des accidents",
            "value": f"{len(df):,}",
            "delta": f"+{len(df[df['Year'] == df['Year'].max()])} en {df['Year'].max()}",
            "column": col1
        },
        {
            "title": "Période d'analyse",
            "value": f"{df['Year'].min()} - {df['Year'].max()}",
            "delta": f"{df['Year'].max() - df['Year'].min() + 1} années",
            "column": col2
        },
        {
            "title": "Régions couvertes",
            "value": f"{df['Region'].nunique()}",
            "delta": f"{df['Country'].nunique()} pays",
            "column": col3
        }
    ]
    
    for metric in metrics:
        with metric["column"]:
            st.markdown(f"""
                <div class="stat-card">
                    <h3>{metric['title']}</h3>
                    <h2>{metric['value']}</h2>
                    <p>{metric['delta']}</p>
                </div>
            """, unsafe_allow_html=True)

def render_data_preview(df):
    st.markdown('<h2 class="section-header">Aperçu des Données</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Aperçu", "📥 Téléchargement"])
    
    with tab1:
        st.dataframe(
            df.head(10),
            use_container_width=True,
            hide_index=True
        )
    
    with tab2:
        st.markdown("""
            <div class="highlight-box">
                <h4>Téléchargement du jeu de données</h4>
                <p>Les données sont disponibles au format CSV et incluent l'ensemble des accidents recensés.</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.download_button(
            label="📥 Télécharger le dataset complet (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='accidents_data.csv',
            mime='text/csv',
            key='download-csv'
        )

def render_home_page():
    set_page_config()
    apply_custom_css()
    
    render_header()
    render_description()
    
    df = load_data()
    if df is not None:
        render_metrics(df)
        render_data_preview(df)
    else:
        st.error("⚠️ Erreur lors du chargement des données. Veuillez réessayer ultérieurement.")