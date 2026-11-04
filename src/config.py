"""Configuration centrale : chemins, libellés, ordres des catégories, palette."""
from pathlib import Path

# --------------------------------------------------------------------------- #
# Application
# --------------------------------------------------------------------------- #
APP_TITLE = "Accidents de la route"
APP_SUBTITLE = "Tableau de bord d'analyse des accidents routiers (2000 – 2024)"

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_DIR / "data" / "accidents.csv"

CURRENCY = "$"  # Devise non précisée par la source : convention unique dans tout le dashboard

# --------------------------------------------------------------------------- #
# Schéma attendu du fichier source
# --------------------------------------------------------------------------- #
NUMERIC_COLUMNS = [
    "Year", "Visibility Level", "Number of Vehicles Involved", "Speed Limit",
    "Driver Alcohol Level", "Driver Fatigue", "Pedestrians Involved",
    "Cyclists Involved", "Number of Injuries", "Number of Fatalities",
    "Emergency Response Time", "Traffic Volume", "Insurance Claims",
    "Medical Cost", "Economic Loss", "Population Density",
]

# Plages de valeurs plausibles (contrôle qualité)
VALID_RANGES = {
    "Year": (1990, 2030),
    "Visibility Level": (0, 10_000),
    "Number of Vehicles Involved": (1, 50),
    "Speed Limit": (5, 150),
    "Driver Alcohol Level": (0, 0.5),
    "Number of Injuries": (0, 500),
    "Number of Fatalities": (0, 500),
    "Emergency Response Time": (0, 600),
    "Medical Cost": (0, None),
    "Economic Loss": (0, None),
}

# --------------------------------------------------------------------------- #
# Traductions des modalités (affichage en français)
# --------------------------------------------------------------------------- #
TRANSLATIONS = {
    "Country": {
        "USA": "États-Unis", "UK": "Royaume-Uni", "Canada": "Canada", "India": "Inde",
        "China": "Chine", "Japan": "Japon", "Russia": "Russie", "Brazil": "Brésil",
        "Germany": "Allemagne", "Australia": "Australie",
    },
    "Month": {
        "January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril",
        "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août",
        "September": "Septembre", "October": "Octobre", "November": "Novembre",
        "December": "Décembre",
    },
    "Day of Week": {
        "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi",
        "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche",
    },
    "Time of Day": {
        "Morning": "Matin", "Afternoon": "Après-midi", "Evening": "Soir", "Night": "Nuit",
    },
    "Urban/Rural": {"Urban": "Urbain", "Rural": "Rural"},
    "Road Type": {"Street": "Rue", "Main Road": "Route principale", "Highway": "Autoroute"},
    "Weather Conditions": {
        "Clear": "Dégagé", "Rainy": "Pluie", "Snowy": "Neige", "Foggy": "Brouillard",
        "Windy": "Vent",
    },
    "Driver Gender": {"Male": "Homme", "Female": "Femme"},
    "Vehicle Condition": {"Good": "Bon", "Moderate": "Moyen", "Poor": "Mauvais"},
    "Accident Severity": {"Minor": "Mineure", "Moderate": "Modérée", "Severe": "Grave"},
    "Road Condition": {"Dry": "Sèche", "Wet": "Mouillée", "Icy": "Verglacée", "Snow-covered": "Enneigée"},
    "Accident Cause": {
        "Speeding": "Excès de vitesse", "Distracted Driving": "Distraction",
        "Drunk Driving": "Alcool au volant", "Mechanical Failure": "Défaillance mécanique",
        "Weather": "Météo",
    },
    "Region": {
        "Europe": "Europe", "Asia": "Asie", "North America": "Amérique du Nord",
        "South America": "Amérique du Sud", "Australia": "Océanie",
    },
}

# Ordre logique des modalités (ordinales ou conventionnelles)
CATEGORY_ORDERS = {
    "Month": list(TRANSLATIONS["Month"].values()),
    "Day of Week": list(TRANSLATIONS["Day of Week"].values()),
    "Time of Day": ["Matin", "Après-midi", "Soir", "Nuit"],
    "Driver Age Group": ["<18", "18-25", "26-40", "41-60", "61+"],
    "Accident Severity": ["Mineure", "Modérée", "Grave"],
    "Vehicle Condition": ["Bon", "Moyen", "Mauvais"],
    "Road Condition": ["Sèche", "Mouillée", "Enneigée", "Verglacée"],
    "Weather Conditions": ["Dégagé", "Vent", "Pluie", "Brouillard", "Neige"],
    "Road Type": ["Rue", "Route principale", "Autoroute"],
    "Urban/Rural": ["Urbain", "Rural"],
    "Driver Gender": ["Femme", "Homme"],
}

# Le champ « Region » de la source est incohérent avec « Country » (un même pays
# apparaît dans les 5 régions). On reconstruit le continent à partir du pays.
COUNTRY_TO_CONTINENT = {
    "États-Unis": "Amérique du Nord", "Canada": "Amérique du Nord",
    "Brésil": "Amérique du Sud", "Royaume-Uni": "Europe", "Allemagne": "Europe",
    "Russie": "Europe", "Inde": "Asie", "Chine": "Asie", "Japon": "Asie",
    "Australie": "Océanie",
}

COUNTRY_ISO3 = {
    "États-Unis": "USA", "Royaume-Uni": "GBR", "Canada": "CAN", "Inde": "IND",
    "Chine": "CHN", "Japon": "JPN", "Russie": "RUS", "Brésil": "BRA",
    "Allemagne": "DEU", "Australie": "AUS",
}

# Seuils d'alcoolémie (g/dL, convention BAC) : 0,05 = seuil européen courant,
# 0,08 = seuil légal US/UK.
ALCOHOL_BINS = [0, 0.05, 0.08, 1]
ALCOHOL_LABELS = ["< 0,05", "0,05 – 0,08", "≥ 0,08"]

SPEED_BINS = [0, 50, 70, 90, 110, 200]
SPEED_LABELS = ["≤ 50", "51–70", "71–90", "91–110", "> 110"]

QUINTILE_LABELS = ["Très faible", "Faible", "Moyen", "Élevé", "Très élevé"]

# --------------------------------------------------------------------------- #
# Libellés lisibles des colonnes
# --------------------------------------------------------------------------- #
LABELS = {
    "Country": "Pays",
    "Continent": "Continent",
    "Region": "Région (source)",
    "Year": "Année",
    "Month": "Mois",
    "Day of Week": "Jour de la semaine",
    "Time of Day": "Moment de la journée",
    "Urban/Rural": "Milieu",
    "Road Type": "Type de route",
    "Weather Conditions": "Météo",
    "Visibility Level": "Visibilité (m)",
    "Visibility Band": "Visibilité",
    "Number of Vehicles Involved": "Véhicules impliqués",
    "Speed Limit": "Limitation de vitesse (km/h)",
    "Speed Band": "Limitation de vitesse (km/h)",
    "Driver Age Group": "Âge du conducteur",
    "Driver Gender": "Sexe du conducteur",
    "Driver Alcohol Level": "Alcoolémie (g/dL)",
    "Alcohol Band": "Alcoolémie (g/dL)",
    "Driver Fatigue": "Fatigue",
    "Fatigue": "Conducteur fatigué",
    "Vehicle Condition": "État du véhicule",
    "Pedestrians Involved": "Piétons impliqués",
    "Cyclists Involved": "Cyclistes impliqués",
    "Accident Severity": "Gravité déclarée",
    "Number of Injuries": "Blessés",
    "Number of Fatalities": "Décès",
    "Victims": "Victimes",
    "Is Fatal": "Accident mortel",
    "Emergency Response Time": "Délai d'intervention (min)",
    "Traffic Volume": "Volume de trafic",
    "Traffic Band": "Volume de trafic",
    "Road Condition": "État de la chaussée",
    "Accident Cause": "Cause",
    "Insurance Claims": "Déclarations d'assurance",
    "Medical Cost": f"Coût médical ({CURRENCY})",
    "Economic Loss": f"Perte économique ({CURRENCY})",
    "Total Cost": f"Coût total ({CURRENCY})",
    "Population Density": "Densité de population",
    "Density Band": "Densité de population",
}

# --------------------------------------------------------------------------- #
# Indicateurs « par accident » proposés à l'utilisateur
# --------------------------------------------------------------------------- #
METRICS = {
    "Number of Fatalities": {"label": "Décès par accident", "short": "Décès / accident", "fmt": ".2f"},
    "Number of Injuries": {"label": "Blessés par accident", "short": "Blessés / accident", "fmt": ".2f"},
    "Is Fatal": {"label": "Part d'accidents mortels", "short": "% mortels", "fmt": ".1%"},
    "Total Cost": {"label": "Coût total par accident", "short": f"Coût / accident ({CURRENCY})", "fmt": ",.0f"},
}
DEFAULT_METRIC = "Number of Fatalities"

# Facteurs analysés dans le classement des facteurs de risque
RISK_FACTORS = [
    "Continent", "Urban/Rural", "Road Type", "Weather Conditions", "Road Condition",
    "Visibility Band", "Traffic Band", "Time of Day", "Day of Week", "Month",
    "Driver Age Group", "Driver Gender", "Fatigue", "Alcohol Band",
    "Vehicle Condition", "Speed Band", "Number of Vehicles Involved", "Accident Cause",
    "Accident Severity",
]

SIGNIFICANCE_LEVEL = 0.05
