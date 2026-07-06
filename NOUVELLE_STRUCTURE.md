# 🔄 Nouvelle Structure de l'Application

## 📋 Vue d'Ensemble

L'application est maintenant divisée en **2 PHASES DISTINCTES** pour plus de clarté et de simplicité.

---

## 🎯 PHASE 1: Transformation Saisonnière

### Objectif
Convertir un fichier de données brut en fichiers saisonniers séparés.

### Fichier
`phase1_transformation.py`

### Lancement
```bash
python phase1_transformation.py
```

### Workflow
1. **Charger** le fichier brut (ex: "modele test.xlsx")
2. **Exporter** la saison sèche → `saison_seche.xlsx`
3. **Exporter** la saison des pluies → `saison_pluies.xlsx`

### Résultat
Deux fichiers Excel contenant les données séparées par saison hydrologique:
- **Saison sèche**: 1er décembre → 31 mai
- **Saison des pluies**: 1er juin → 30 novembre

---

## 🎯 PHASE 2: Analyse et Prédiction

### Objectif
Analyser les données saisonnières et prédire l'année suivante.

### Fichier
`phase2_prediction.py`

### Lancement
```bash
python phase2_prediction.py
```

### Workflow

#### 1. Chargement
- Charger un fichier saisonnier exporté (ex: `saison_seche.xlsx`)

#### 2. Configuration
- **Période d'entraînement**: Choisir les années pour entraîner le modèle
  - Exemple: Années 1 à 15 (2001-2002 à 2015-2016)
- **Période de test**: Choisir les années pour tester le modèle
  - Exemple: Années 16 à 20 (2016-2017 à 2020-2021)

#### 3. Sélection du Modèle
- Random Forest
- XGBoost
- Régression Linéaire
- SARIMA
- AdaBoost

#### 4. Analyse
- Analyse sur **TOUTES les années** du fichier
- Statistiques globales
- Tendances
- Anomalies

#### 5. Prédiction
- Entraînement sur la période choisie
- Test sur la période choisie
- **Prédiction de l'année suivante** (n+1)

#### 6. Export
- Résultats en Excel
- Rapport PDF

---

## 🚀 Lancement Rapide

### Menu Principal
```bash
python main.py
```

Le menu vous permet de choisir:
- **Phase 1**: Transformation
- **Phase 2**: Analyse et Prédiction

---

## 📊 Exemple Complet

### Étape 1: Transformation (Phase 1)
```
Fichier brut: modele_test.xlsx (2001 à 2023)
    ↓
[Phase 1]
    ↓
saison_seche.xlsx (2001-2002 à 2022-2023)
saison_pluies.xlsx (2001 à 2022)
```

### Étape 2: Prédiction (Phase 2)
```
Charger: saison_seche.xlsx
    ↓
Configuration:
- Entraînement: Années 1-15 (2001-2002 à 2015-2016)
- Test: Années 16-22 (2016-2017 à 2022-2023)
    ↓
Analyse: Toutes les années (2001-2002 à 2022-2023)
    ↓
Prédiction: Année 2023-2024 (année suivante!)
```

---

## 📁 Fichiers Principaux

### Applications
- `main.py` - Menu principal
- `phase1_transformation.py` - Phase 1
- `phase2_prediction.py` - Phase 2

### Backend (inchangé)
- `backend/data_processing/seasonal_transformer.py`
- `backend/analysis/flow_analyzer.py`
- `backend/models/flow_predictor.py`
- `backend/models/climate_analyzer.py`
- `backend/export/report_generator.py`

### Anciens Fichiers (non utilisés)
- `frontend/ui/main_window.py` - Ancienne interface (remplacée)
- `frontend/ui/visualization.py` - Peut être réutilisé

---

## ✅ Avantages de la Nouvelle Structure

1. **Simplicité**: Deux phases clairement séparées
2. **Clarté**: Chaque phase a un objectif précis
3. **Flexibilité**: L'utilisateur choisit les périodes train/test
4. **Prédiction correcte**: Prédit l'année suivante (n+1), pas une année existante
5. **Pas de confusion**: Pas de mélange entre transformation et prédiction

---

## 🎯 Utilisation Recommandée

### Pour un nouveau projet:
1. Lancer `python main.py`
2. Choisir **Phase 1**
3. Transformer vos données
4. Fermer Phase 1
5. Lancer `python main.py`
6. Choisir **Phase 2**
7. Analyser et prédire

### Pour des données déjà transformées:
1. Lancer `python main.py`
2. Choisir **Phase 2** directement
3. Charger votre fichier saisonnier
4. Analyser et prédire

---

## 📝 Notes Importantes

- Les fichiers exportés de Phase 1 contiennent la colonne `saison_annee`
- Phase 2 nécessite cette colonne pour fonctionner
- La prédiction se fait toujours sur l'année n+1 (future)
- L'analyse se fait sur toutes les années du fichier
- L'utilisateur contrôle la répartition train/test

---

**Structure simplifiée et efficace!** ✅
