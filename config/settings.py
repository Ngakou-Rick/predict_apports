"""
Configuration de l'application
"""
import os

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
EXPORT_DIR = os.path.join(BASE_DIR, 'exports')
IMAGE_DIR = os.path.join(BASE_DIR, 'image')

# Créer les dossiers s'ils n'existent pas
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

# Paramètres de l'application
APP_NAME = "Prévision Hydrologique Mbakaou"
APP_VERSION = "1.0.0"

# Paramètres des modèles
DEFAULT_MODEL = "Random Forest"
TEST_SIZE = 0.2
LAG_DAYS = 7

# Paramètres d'analyse
ANOMALY_THRESHOLD = 3.0  # Écarts-types pour détection d'anomalies
PERCENTILES = [5, 25, 50, 75, 95]

# Paramètres de visualisation
PLOT_DPI = 300
PLOT_STYLE = 'seaborn-v0_8-darkgrid'
COLOR_PALETTE = {
    'primary': '#1f4788',
    'secondary': '#3498db',
    'success': '#28a745',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#17a2b8'
}

# Paramètres d'export
EXCEL_ENGINE = 'openpyxl'
PDF_PAGESIZE = 'A4'

# Messages
MESSAGES = {
    'load_success': 'Données chargées avec succès',
    'load_error': 'Erreur lors du chargement des données',
    'analysis_success': 'Analyse terminée avec succès',
    'analysis_error': 'Erreur lors de l\'analyse',
    'prediction_success': 'Prédiction terminée avec succès',
    'prediction_error': 'Erreur lors de la prédiction',
    'export_success': 'Export réussi',
    'export_error': 'Erreur lors de l\'export'
}
