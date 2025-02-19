# Configuration générale
APP_TITLE = "Analyse des Accidents de la Route"
APP_SUBTITLE = "Dashboard interactif d'analyse des accidents routiers"

# Thème personnalisé
THEME_CONFIG = {
    'primary': '#FF4B4B',  # Rouge pour les accidents/danger
    'secondary': '#1F77B4',  # Bleu pour les données neutres
    'background': '#F0F2F6',
    'text': '#262730'
}

# Configuration des graphiques
CHART_HEIGHT = 400
CHART_WIDTH = 600
GRID_COLUMNS = 2

# Paramètres des filtres
SEVERITY_LEVELS = [
    'Moderate', 'Minor', 'Severe'
]

ACCIDENT_CAUSES = [
    'Weather', 'Mechanical Failure', 'Speeding', 'Distracted Driving', 'Drunk Driving'
]

# Colonnes importantes du dataset
NUMERIC_COLUMNS = [
    'Number of Vehicles Involved', 'Number of Injuries',
    'Number of Fatalities', 'Emergency Response Time',
    'Driver Alcohol Level', 'Traffic Volume',
    'Medical Cost', 'Economic Loss'
]

CATEGORICAL_COLUMNS = [
    'Accident Severity', 'Accident Cause', 'Weather Conditions',
    'Road Type', 'Urban/Rural', 'Driver Age Group', 'Driver Gender'
]

# Format des nombres
NUMBER_FORMAT = {
    'Medical Cost': '${:,.2f}',
    'Economic Loss': '${:,.2f}',
    'Emergency Response Time': '{:.1f} min',
    'Driver Alcohol Level': '{:.3f}'
}