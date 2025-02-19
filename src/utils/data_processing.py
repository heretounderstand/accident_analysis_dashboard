import pandas as pd
from typing import Dict, Any

def calculate_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcule les statistiques résumées du dataset filtré
    """
    if df is None or df.empty:
        return {}
    
    total_accidents = len(df)
    total_fatalities = df['Number of Fatalities'].sum()
    total_injuries = df['Number of Injuries'].sum()
    avg_response_time = df['Emergency Response Time'].mean()
    total_economic_loss = df['Economic Loss'].sum()
    
    return {
        'total_accidents': total_accidents,
        'total_fatalities': total_fatalities,
        'total_injuries': total_injuries,
        'avg_response_time': avg_response_time,
        'total_economic_loss': total_economic_loss
    }

def prepare_temporal_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour les analyses temporelles
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Agrégation par date
    temporal_data = df.groupby('Date').agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum',
        'Economic Loss': 'sum'
    }).reset_index()
    
    return temporal_data

def prepare_geographic_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prépare les données pour les analyses géographiques
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    # Agrégation par région
    geographic_data = df.groupby(['Region', 'Urban/Rural']).agg({
        'Number of Fatalities': 'sum',
        'Number of Injuries': 'sum',
        'Economic Loss': 'sum'
    }).reset_index()
    
    return geographic_data

def calculate_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les taux importants (mortalité, blessures par accident, etc.)
    """
    if df is None or df.empty:
        return pd.DataFrame()
    
    rates = pd.DataFrame()
    rates['fatality_rate'] = df['Number of Fatalities'] / df['Number of Vehicles Involved']
    rates['injury_rate'] = df['Number of Injuries'] / df['Number of Vehicles Involved']
    rates['severity_index'] = (df['Number of Fatalities'] * 5 + df['Number of Injuries']) / len(df)
    
    return rates