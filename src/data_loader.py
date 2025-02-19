import pandas as pd
import streamlit as st
from pathlib import Path

@st.cache_data
def load_data():
    """
    Charge et prétraite le dataset des accidents
    """
    try:
        df = pd.read_csv(Path('data/accidents.csv'))
        
        # Conversion des types de données
        numeric_columns = [
            'Number of Vehicles Involved', 'Number of Injuries',
            'Number of Fatalities', 'Emergency Response Time',
            'Driver Alcohol Level', 'Traffic Volume',
            'Medical Cost', 'Economic Loss'
        ]
        
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Conversion des dates
        # Dictionnaire de conversion des mois en anglais vers leurs numéros
        month_map = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        
        df['Date'] = pd.to_datetime(df['Year'].astype(str) + '-' + df['Month'].map(month_map).astype(str) + '-01')
        
        return df
    
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

def filter_data(df, filters):
    """
    Applique les filtres globaux au dataset
    """
    if df is None:
        return None
    
    filtered_df = df.copy()
    
    # Filtre par sévérité
    if filters.get('severity'):
        filtered_df = filtered_df[filtered_df['Accident Severity'].isin(filters['severity'])]
    
    # Filtre par nombre de véhicules
    if filters.get('vehicles_range'):
        min_v, max_v = filters['vehicles_range']
        filtered_df = filtered_df[
            (filtered_df['Number of Vehicles Involved'] >= min_v) &
            (filtered_df['Number of Vehicles Involved'] <= max_v)
        ]
    
    # Filtre présence piétons/cyclistes
    if filters.get('pedestrians', False):
        filtered_df = filtered_df[filtered_df['Pedestrians Involved'] > 0]
    if filters.get('cyclists', False):
        filtered_df = filtered_df[filtered_df['Cyclists Involved'] > 0]
    
    # Filtre blessés/décès
    if filters.get('casualties_range'):
        min_c, max_c = filters['casualties_range']
        total_casualties = filtered_df['Number of Injuries'] + filtered_df['Number of Fatalities']
        filtered_df = filtered_df[
            (total_casualties >= min_c) &
            (total_casualties <= max_c)
        ]
    
    # Filtre temps de réponse
    if filters.get('response_time_range'):
        min_t, max_t = filters['response_time_range']
        filtered_df = filtered_df[
            (filtered_df['Emergency Response Time'] >= min_t) &
            (filtered_df['Emergency Response Time'] <= max_t)
        ]
    
    # Filtre causes d'accident
    if filters.get('causes'):
        filtered_df = filtered_df[filtered_df['Accident Cause'].isin(filters['causes'])]
    
    return filtered_df