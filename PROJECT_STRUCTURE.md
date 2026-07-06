# 📁 Structure du Projet

```
mbakaou_hydro/
│
├── 📂 backend/                          # BACKEND (Logique Métier)
│   ├── __init__.py
│   │
│   ├── 📂 core/                         # Contrôleur Principal
│   │   ├── __init__.py
│   │   └── application_controller.py    # Orchestration de toute la logique
│   │
│   ├── 📂 data_processing/              # Traitement des Données
│   │   ├── __init__.py
│   │   └── seasonal_transformer.py      # Transformation en saisons hydrologiques
│   │
│   ├── 📂 analysis/                     # Analyses Hydrologiques
│   │   ├── __init__.py
│   │   └── flow_analyzer.py             # Analyse temporelle, mensuelle, lag
│   │
│   ├── 📂 models/                       # Modèles de Prédiction
│   │   ├── __init__.py
│   │   ├── flow_predictor.py            # Random Forest, XGBoost, SARIMA, etc.
│   │   └── climate_analyzer.py          # Analyse climatique et corrélations
│   │
│   └── 📂 export/                       # Export des Résultats
│       ├── __init__.py
│       └── report_generator.py          # Génération Excel et PDF
│
├── 📂 frontend/                         # FRONTEND (Interface Utilisateur)
│   ├── __init__.py
│   │
│   └── 📂 ui/                           # Interface Graphique
│       ├── __init__.py
│       ├── main_window.py               # Fenêtre principale PyQt5
│       └── visualization.py             # Graphiques interactifs
│
├── 📂 config/                           # Configuration
│   ├── __init__.py
│   └── settings.py                      # Paramètres de l'application
│
├── 📂 image/                            # Images et Assets
│   └── mbaka.png                        # Image de fond (75% transparence)
│
├── 📂 exports/                          # Dossier des Exports (créé auto)
│   ├── *.xlsx                           # Fichiers Excel exportés
│   └── *.pdf                            # Rapports PDF générés
│
├── 📂 data/                             # Données (créé auto)
│   └── *.xlsx                           # Fichiers de données
│
├── 📄 main.py                           # POINT D'ENTRÉE PRINCIPAL
├── 📄 test_app.py                       # Script de test
│
├── 📄 requirements.txt                  # Dépendances Python
├── 📄 .gitignore                        # Fichiers à ignorer par Git
│
├── 📄 README.md                         # Documentation principale
├── 📄 INSTALLATION.md                   # Guide d'installation
├── 📄 GUIDE_UTILISATEUR.md              # Guide utilisateur complet
├── 📄 QUICKSTART.md                     # Démarrage rapide
├── 📄 PROJECT_STRUCTURE.md              # Ce fichier
│
├── 📄 run.bat                           # Script de lancement Windows
└── 📄 run.sh                            # Script de lancement Linux/macOS
```

## 🎯 Description des Modules

### Backend

#### 1. **core/application_controller.py**
Contrôleur principal qui orchestre toute la logique:
- Chargement et transformation des données
- Coordination des analyses
- Gestion des prédictions
- Export des résultats

#### 2. **data_processing/seasonal_transformer.py**
Transformation des données en années hydrologiques:
- Saison sèche: 1er décembre → 31 mai
- Saison des pluies: 1er juin → 30 novembre
- Création de bases de données distinctes
- Export des bases saisonnières

#### 3. **analysis/flow_analyzer.py**
Analyse hydrologique complète:
- Analyse temporelle (moyenne, tendance, variabilité)
- Analyse mensuelle (statistiques par mois)
- Analyse dynamique (autocorrélation, lag features)
- Détection d'anomalies

#### 4. **models/flow_predictor.py**
Modélisation et prédiction des débits:
- 5 modèles: Random Forest, XGBoost, SARIMA, AdaBoost, Régression Linéaire
- Préparation des features (lag, temporelles, climatiques)
- Entraînement et validation
- Métriques de performance (RMSE, MAE, R²)
- Feature importance

#### 5. **models/climate_analyzer.py**
Analyse des variables climatiques:
- Corrélations débits-climat (Pearson, Spearman)
- Calcul amplitude thermique (Tmax - Tmin)
- Calcul bilan hydrique (Pluie - ETP)
- Distribution des pluies
- Prédiction des variables climatiques

#### 6. **export/report_generator.py**
Génération de rapports professionnels:
- Export Excel multi-feuilles
- Rapport PDF avec graphiques
- Création de visualisations
- Heatmaps de corrélation

### Frontend

#### 1. **ui/main_window.py**
Interface principale PyQt5:
- Panneau de contrôle (chargement, sélection, actions)
- 5 onglets (Données, Analyse, Prédiction, Climat, Export)
- Gestion des événements utilisateur
- Affichage des résultats
- Intégration avec le backend

#### 2. **ui/visualization.py**
Visualisations interactives:
- Graphiques Matplotlib intégrés
- Comparaison réel vs prédit
- Analyse mensuelle
- Heatmaps de corrélation
- Importance des variables
- Graphiques Plotly interactifs

### Configuration

#### **config/settings.py**
Paramètres centralisés:
- Chemins des dossiers
- Paramètres des modèles
- Seuils d'analyse
- Couleurs et styles
- Messages

## 🔄 Flux de Données

```
1. Utilisateur charge Excel
   ↓
2. SeasonalTransformer sépare en saisons
   ↓
3. ApplicationController coordonne
   ↓
4. FlowAnalyzer analyse les débits
   ↓
5. FlowPredictor prédit les débits futurs
   ↓
6. ClimateAnalyzer analyse le climat
   ↓
7. ReportGenerator exporte les résultats
   ↓
8. MainWindow affiche à l'utilisateur
```

## 🎨 Architecture MVC

**Model** (Backend):
- data_processing/
- analysis/
- models/

**View** (Frontend):
- ui/main_window.py
- ui/visualization.py

**Controller**:
- core/application_controller.py

## 📦 Dépendances Principales

### Traitement de Données
- pandas: Manipulation de données
- numpy: Calculs numériques
- openpyxl: Lecture/écriture Excel

### Machine Learning
- scikit-learn: Random Forest, Régression, AdaBoost
- xgboost: XGBoost
- statsmodels: SARIMA

### Visualisation
- matplotlib: Graphiques statiques
- seaborn: Graphiques statistiques
- plotly: Graphiques interactifs

### Interface
- PyQt5: Interface graphique

### Export
- reportlab: Génération PDF
- openpyxl: Export Excel

### Analyse
- scipy: Statistiques avancées

## 🚀 Points d'Entrée

### Principal
```bash
python main.py
```

### Test
```bash
python test_app.py
```

### Scripts de Lancement
```bash
# Windows
run.bat

# Linux/macOS
chmod +x run.sh
./run.sh
```

## 📊 Formats de Données

### Entrée (Excel)
```
Date | Debits | Pluie | Tmax | Tmin | ETP
```

### Sortie (Excel)
```
Feuille 1: Données brutes
Feuille 2: Prédictions
Feuille 3: Métriques
Feuille 4: Analyse mensuelle
Feuille 5: Corrélations climat
```

### Sortie (PDF)
```
Page 1: Informations générales
Page 2: Métriques de performance
Page 3+: Graphiques et visualisations
```

## 🔐 Sécurité et Robustesse

- Gestion des erreurs à tous les niveaux
- Validation des données d'entrée
- Messages d'erreur explicites
- Logs pour débogage
- Sauvegarde automatique des exports

## 🎓 Niveau Technique

**Niveau Ingénieur**:
- Architecture modulaire propre
- Séparation backend/frontend
- Code documenté
- Gestion d'erreurs robuste
- Performance optimisée
- Interface professionnelle

## 📈 Évolutions Futures

Possibilités d'extension:
- Base de données SQL
- API REST
- Interface web
- Modèles deep learning
- Prévisions multi-saisons
- Analyse de sensibilité
- Optimisation de la gestion du barrage

---

**Architecture conçue pour la maintenabilité et l'extensibilité** 🏗️
