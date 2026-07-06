# 📦 Guide d'Installation

## Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)
- Windows, macOS ou Linux

## Installation Étape par Étape

### 1. Vérifier Python

Ouvrez un terminal (CMD ou PowerShell sur Windows) et vérifiez que Python est installé:

```bash
python --version
```

Si Python n'est pas installé, téléchargez-le depuis [python.org](https://www.python.org/downloads/)

### 2. Créer un Environnement Virtuel (Recommandé)

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
# Sur Windows:
venv\Scripts\activate

# Sur macOS/Linux:
source venv/bin/activate
```

### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

Cette commande installera automatiquement:
- pandas (traitement de données)
- numpy (calculs numériques)
- scikit-learn (machine learning)
- xgboost (modèle de prédiction)
- statsmodels (SARIMA)
- matplotlib, seaborn, plotly (visualisations)
- PyQt5 (interface graphique)
- openpyxl (export Excel)
- reportlab (export PDF)
- scipy (analyses statistiques)

### 4. Vérifier l'Installation

```bash
python -c "import pandas, numpy, sklearn, xgboost, PyQt5; print('Installation réussie!')"
```

### 5. Lancer l'Application

```bash
python main.py
```

## Résolution des Problèmes

### Erreur: "No module named 'PyQt5'"

```bash
pip install --upgrade PyQt5
```

### Erreur: "Microsoft Visual C++ required"

Sur Windows, installez [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)

### Erreur: "Permission denied"

Sur macOS/Linux, utilisez:

```bash
pip install --user -r requirements.txt
```

### Problème avec xgboost

```bash
pip uninstall xgboost
pip install xgboost --no-cache-dir
```

## Installation Alternative (Conda)

Si vous utilisez Anaconda:

```bash
# Créer l'environnement
conda create -n mbakaou python=3.9

# Activer
conda activate mbakaou

# Installer les packages
conda install pandas numpy scikit-learn matplotlib seaborn scipy
pip install xgboost statsmodels PyQt5 openpyxl reportlab plotly
```

## Mise à Jour

Pour mettre à jour les dépendances:

```bash
pip install --upgrade -r requirements.txt
```

## Désinstallation

```bash
# Désactiver l'environnement virtuel
deactivate

# Supprimer le dossier venv
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

## Support

En cas de problème, vérifiez:
1. Version de Python (3.8+)
2. Connexion internet pour télécharger les packages
3. Droits d'administrateur si nécessaire
4. Espace disque suffisant (environ 500 MB)
