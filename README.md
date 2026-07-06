# 🌊 Système de Prévision Hydrologique - Barrage de Mbakaou

Application desktop professionnelle Python pour la prévision hydrologique basée sur l'analyse saisonnière (saison sèche et saison des pluies).

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

---

## 📑 Navigation Rapide

- 🎯 **[COMMENCEZ ICI - START_HERE.md](START_HERE.md)** ⭐ - Point de départ recommandé
- 🚀 **[Démarrage Rapide (5 min)](QUICKSTART.md)** - Commencer immédiatement
- 📖 **[Guide Utilisateur Complet](GUIDE_UTILISATEUR.md)** - Manuel détaillé
- 🔧 **[Installation](INSTALLATION.md)** - Guide d'installation
- 📋 **[Index Documentation](INDEX.md)** - Toute la documentation
- ✨ **[Fonctionnalités](FEATURES.md)** - Liste complète
- 🏗️ **[Architecture](PROJECT_STRUCTURE.md)** - Structure technique
- 📊 **[Synthèse](SYNTHESE.md)** - Vue d'ensemble du projet
- 🎁 **[Présentation](PRESENTATION.md)** - Présentation visuelle
- 📦 **[Livraison](LIVRAISON.md)** - Bon de livraison complet

---

## 📋 Fonctionnalités

### 🔄 Transformation des Données
- Conversion automatique en années hydrologiques saisonnières
- **Saison sèche**: 1er décembre (année n) au 31 mai (année n+1)
- **Saison des pluies**: 1er juin au 30 novembre
- Bases de données distinctes consultables en Excel

### 📊 Module 1: Analyse Hydrologique
- Analyse temporelle (tendance, variabilité, anomalies)
- Analyse mensuelle (moyennes, min/max, percentiles)
- Analyse dynamique (autocorrélation, lag features)

### 🤖 Module 2: Modélisation des Débits
Modèles disponibles:
- Random Forest
- Régression Linéaire
- SARIMA
- AdaBoost
- XGBoost

Métriques de performance:
- RMSE (Root Mean Square Error)
- MAE (Mean Absolute Error)
- R² (Coefficient de détermination)

### 🌧️ Module 3: Modélisation Climatique
- Analyse des corrélations (Débits vs Pluie, ETP, Température)
- Calcul de l'amplitude thermique (Tmax - Tmin)
- Calcul du bilan hydrique (Pluie - ETP)
- Prédiction des variables climatiques

### 📈 Visualisation
- Graphiques interactifs (Matplotlib, Plotly)
- Comparaison réel vs prédit
- Heatmaps de corrélation
- Importance des variables

### 📤 Export
- Export Excel (données, prédictions, métriques)
- Rapports PDF professionnels avec graphiques

## 🛠️ Installation

### Prérequis
- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation des dépendances

```bash
pip install -r requirements.txt
```

## 🚀 Utilisation

### Lancer l'application

```bash
python main.py
```

### Workflow typique

1. **Charger les données**
   - Cliquer sur "📁 Charger Données Excel"
   - Sélectionner votre fichier Excel contenant les colonnes:
     - Date
     - Débits
     - Pluie
     - Température max
     - Température min
     - ETP (Évapotranspiration)

2. **Sélectionner la saison**
   - Choisir "Saison Sèche" ou "Saison des Pluies"
   - Sélectionner l'année hydrologique

3. **Analyser**
   - Cliquer sur "🔍 Analyser"
   - Consulter les résultats dans l'onglet "📈 Analyse"

4. **Prédire**
   - Sélectionner un modèle (Random Forest, XGBoost, etc.)
   - Cliquer sur "🎯 Prédire"
   - Visualiser les résultats dans l'onglet "🤖 Prédiction"

5. **Analyser le climat**
   - Consulter l'onglet "🌧️ Climat" pour les corrélations
   - Voir les prédictions climatiques basées sur les débits

6. **Exporter**
   - Onglet "📤 Export"
   - Choisir Excel ou PDF
   - Télécharger le rapport complet

## 📁 Structure du Projet

```
mbakaou_hydro/
├── backend/                    # Backend (logique métier)
│   ├── core/                   # Contrôleur principal
│   │   └── application_controller.py
│   ├── data_processing/        # Traitement des données
│   │   └── seasonal_transformer.py
│   ├── analysis/               # Analyses hydrologiques
│   │   └── flow_analyzer.py
│   ├── models/                 # Modèles de prédiction
│   │   ├── flow_predictor.py
│   │   └── climate_analyzer.py
│   └── export/                 # Export Excel/PDF
│       └── report_generator.py
├── frontend/                   # Frontend (interface)
│   └── ui/
│       ├── main_window.py      # Fenêtre principale
│       └── visualization.py    # Visualisations
├── config/                     # Configuration
│   └── settings.py
├── image/                      # Images (fond d'écran)
│   └── mbaka.png
├── exports/                    # Dossier des exports
├── main.py                     # Point d'entrée
├── requirements.txt            # Dépendances
└── README.md                   # Documentation
```

## 🔧 Configuration

Modifier `config/settings.py` pour personnaliser:
- Chemins des dossiers
- Paramètres des modèles
- Seuils d'analyse
- Couleurs et styles de visualisation

## 📊 Format des Données d'Entrée

Le fichier Excel doit contenir les colonnes suivantes:

| Date       | Débits | Pluie | Tmax | Tmin | ETP  |
|------------|--------|-------|------|------|------|
| 2020-01-01 | 150.5  | 0.0   | 35.2 | 18.5 | 5.2  |
| 2020-01-02 | 148.3  | 2.5   | 34.8 | 19.0 | 5.0  |
| ...        | ...    | ...   | ...  | ...  | ...  |

## 🎯 Cas d'Usage

### Exemple 1: Prédiction Saison Sèche
```
1. Charger données historiques
2. Sélectionner "Saison Sèche" + année "2023-2024"
3. Choisir modèle "Random Forest"
4. Analyser puis Prédire
5. Exporter rapport PDF
```

### Exemple 2: Analyse Climatique
```
1. Charger données
2. Sélectionner saison
3. Analyser
4. Consulter onglet Climat
5. Voir corrélations Débits-Pluie-ETP
```

## 📈 Métriques de Performance

- **RMSE**: Plus faible = meilleure précision
- **MAE**: Erreur moyenne absolue
- **R²**: Proche de 1 = excellent modèle

## 🐛 Dépannage

### Erreur de chargement Excel
- Vérifier que le fichier contient bien une colonne "Date"
- S'assurer que les dates sont au format reconnu

### Erreur de prédiction
- Vérifier qu'il y a suffisamment de données (minimum 30 jours)
- Essayer un autre modèle

### Graphiques ne s'affichent pas
- Vérifier l'installation de matplotlib et PyQt5
- Réinstaller: `pip install --upgrade matplotlib PyQt5`

## 👥 Support

Pour toute question ou problème:
- Consulter la documentation dans le code
- Vérifier les logs d'erreur dans la console

## 📝 Licence

Application développée pour le Bureau d'Études Hydrologiques - Barrage de Mbakaou

## 🔄 Mises à Jour

### Version 1.0.0
- Transformation saisonnière automatique
- 5 modèles de prédiction
- Analyse climatique complète
- Export Excel et PDF
- Interface professionnelle avec fond personnalisé

## 🎓 Niveau Technique

Application de niveau ingénieur avec:
- Architecture MVC
- Code modulaire et documenté
- Gestion robuste des erreurs
- Performance optimisée
- Interface professionnelle

---

**Développé avec ❤️ pour l'hydrologie du Cameroun**
