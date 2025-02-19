import streamlit as st
from typing import Dict, Any
from ..config import SEVERITY_LEVELS, ACCIDENT_CAUSES

def initialize_filters():
    """
    Initialise les filtres dans la session state si nécessaire
    """
    if 'filters' not in st.session_state:
        st.session_state.filters = {
            'severity': [],
            'vehicles_range': (1, 4),
            'pedestrians': False,
            'cyclists': False,
            'casualties_range': (0, 23),
            'response_time_range': (5, 60),
            'causes': []
        }

def render_filters() -> Dict[str, Any]:
    """
    Affiche et gère les filtres globaux avec une interface utilisateur améliorée
    """
    initialize_filters()
    
    with st.sidebar:
        st.header("🔍 Filtres d'analyse", anchor=False)
        
        # Conteneur pour tous les filtres
        with st.container():
            # Filtre de sévérité avec code couleur
            st.subheader("🚨 Niveau de sévérité", anchor=False)
            severity = st.multiselect(
                "Sélectionner la sévérité",
                options=SEVERITY_LEVELS,
                default=st.session_state.filters['severity'],
                help="Filtrer par niveau de gravité des accidents"
            )
            
            # Séparateur visuel
            st.divider()
            
            # Section participants avec mise en page améliorée
            st.subheader("👥 Participants", anchor=False)
            
            # Filtre nombre de véhicules avec plus de contexte
            vehicles_range = st.slider(
                "🚗 Véhicules impliqués",
                min_value=1,
                max_value=4,
                value=st.session_state.filters['vehicles_range'],
                help="Nombre de véhicules impliqués dans l'accident"
            )
            
            # Filtres piétons/cyclistes dans une disposition plus compacte
            cols = st.columns([1, 1])
            with cols[0]:
                pedestrians = st.toggle(
                    "🚶 Piétons",
                    value=st.session_state.filters['pedestrians'],
                    help="Inclure les accidents impliquant des piétons"
                )
            with cols[1]:
                cyclists = st.toggle(
                    "🚲 Cyclistes",
                    value=st.session_state.filters['cyclists'],
                    help="Inclure les accidents impliquant des cyclistes"
                )
            
            st.divider()
            
            # Section impact avec meilleure présentation
            st.subheader("📊 Impact", anchor=False)
            
            # Filtre blessés/décès avec statistiques
            casualties_range = st.slider(
                "🏥 Nombre de victimes",
                min_value=0,
                max_value=23,
                value=st.session_state.filters['casualties_range'],
                help="Nombre total de personnes blessées ou décédées"
            )
            
            # Temps de réponse avec des repères visuels
            response_time_range = st.slider(
                "⏱️ Temps de réponse (min)",
                min_value=5,
                max_value=60,
                value=st.session_state.filters['response_time_range'],
                help="Durée entre l'appel d'urgence et l'arrivée des secours"
            )
            
            st.divider()
            
            # Filtre causes avec catégorisation
            st.subheader("⚠️ Causes", anchor=False)
            causes = st.multiselect(
                "Sélectionner les causes",
                options=ACCIDENT_CAUSES,
                default=st.session_state.filters['causes'],
                help="Facteurs ayant contribué à l'accident"
            )
            
            st.divider()
            
            # Bouton de réinitialisation plus visible
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Réinitialiser", type="primary", use_container_width=True):
                    st.session_state.filters = {
                        'severity': [],
                        'vehicles_range': (1, 4),
                        'pedestrians': False,
                        'cyclists': False,
                        'casualties_range': (0, 23),
                        'response_time_range': (5, 60),
                        'causes': []
                    }
                    st.rerun()
    
    # Mise à jour des filtres dans la session state
    current_filters = {
        'severity': severity,
        'vehicles_range': vehicles_range,
        'pedestrians': pedestrians,
        'cyclists': cyclists,
        'casualties_range': casualties_range,
        'response_time_range': response_time_range,
        'causes': causes
    }
    
    st.session_state.filters = current_filters
    return current_filters

def get_active_filters() -> Dict[str, Any]:
    """
    Retourne les filtres actifs avec leurs valeurs
    """
    active_filters = {}
    if st.session_state.filters['severity']:
        active_filters['Sévérité'] = st.session_state.filters['severity']
    
    if st.session_state.filters['vehicles_range'] != (1, 4):
        active_filters['Véhicules'] = f"{st.session_state.filters['vehicles_range'][0]} - {st.session_state.filters['vehicles_range'][1]}"
    
    if st.session_state.filters['pedestrians']:
        active_filters['Piétons'] = "Oui"
    
    if st.session_state.filters['cyclists']:
        active_filters['Cyclistes'] = "Oui"
    
    if st.session_state.filters['casualties_range'] != (0, 23):
        active_filters['Victimes'] = f"{st.session_state.filters['casualties_range'][0]} - {st.session_state.filters['casualties_range'][1]}"
    
    if st.session_state.filters['response_time_range'] != (5, 60):
        active_filters['Temps de réponse'] = f"{st.session_state.filters['response_time_range'][0]} - {st.session_state.filters['response_time_range'][1]} min"
    
    if st.session_state.filters['causes']:
        active_filters['Causes'] = st.session_state.filters['causes']
    
    return active_filters

def display_active_filters():
    """
    Affiche un résumé des filtres actifs
    """
    active_filters = get_active_filters()
    
    if active_filters:
        st.write("---")
        st.subheader("Filtres actifs")
        
        for key, value in active_filters.items():
            if isinstance(value, list):
                value = ", ".join(value)
            st.write(f"**{key}:** {value}")