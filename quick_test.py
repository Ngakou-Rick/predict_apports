"""
Test rapide de l'application
"""
import sys
import os

print("="*60)
print("🧪 TEST RAPIDE DE L'APPLICATION")
print("="*60)

# Test 1: Imports
print("\n1. Test des imports...")
try:
    from backend.data_processing.seasonal_transformer import SeasonalTransformer
    from backend.analysis.flow_analyzer import FlowAnalyzer
    from backend.models.flow_predictor import FlowPredictor
    from backend.models.climate_analyzer import ClimateAnalyzer
    from backend.export.report_generator import ReportGenerator
    from backend.core.application_controller import ApplicationController
    print("   ✅ Tous les imports backend OK")
except Exception as e:
    print(f"   ❌ Erreur imports backend: {e}")
    sys.exit(1)

try:
    from frontend.ui.main_window import MainWindow
    from frontend.ui.visualization import VisualizationWidget
    print("   ✅ Tous les imports frontend OK")
except Exception as e:
    print(f"   ❌ Erreur imports frontend: {e}")
    sys.exit(1)

# Test 2: Dépendances
print("\n2. Test des dépendances...")
try:
    import pandas as pd
    import numpy as np
    import sklearn
    import xgboost
    import statsmodels
    import matplotlib
    import seaborn
    import plotly
    from PyQt5 import QtWidgets
    import openpyxl
    import reportlab
    import scipy
    print("   ✅ Toutes les dépendances OK")
except Exception as e:
    print(f"   ❌ Erreur dépendances: {e}")
    sys.exit(1)

# Test 3: Création d'objets
print("\n3. Test de création d'objets...")
try:
    transformer = SeasonalTransformer()
    controller = ApplicationController()
    generator = ReportGenerator()
    print("   ✅ Création d'objets OK")
except Exception as e:
    print(f"   ❌ Erreur création objets: {e}")
    sys.exit(1)

# Test 4: Fichiers de configuration
print("\n4. Test des fichiers...")
try:
    assert os.path.exists("requirements.txt"), "requirements.txt manquant"
    assert os.path.exists("main.py"), "main.py manquant"
    assert os.path.exists("README.md"), "README.md manquant"
    assert os.path.exists("backend"), "Dossier backend manquant"
    assert os.path.exists("frontend"), "Dossier frontend manquant"
    assert os.path.exists("config"), "Dossier config manquant"
    print("   ✅ Tous les fichiers essentiels présents")
except AssertionError as e:
    print(f"   ❌ {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ TOUS LES TESTS SONT PASSÉS!")
print("="*60)
print("\n💡 L'application est prête à être utilisée:")
print("   python main.py")
print("\n📚 Consultez START_HERE.md pour commencer")
