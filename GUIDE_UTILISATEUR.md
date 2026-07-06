# 📖 Guide Utilisateur - Prévision Hydrologique Mbakaou

## Table des Matières
1. [Introduction](#introduction)
2. [Démarrage Rapide](#démarrage-rapide)
3. [Interface Utilisateur](#interface-utilisateur)
4. [Workflow Complet](#workflow-complet)
5. [Interprétation des Résultats](#interprétation-des-résultats)
6. [Export des Rapports](#export-des-rapports)
7. [FAQ](#faq)

## Introduction

Cette application permet de:
- Analyser les débits du barrage de Mbakaou
- Prédire les débits futurs avec différents modèles
- Étudier les relations climat-débits
- Générer des rapports professionnels

## Démarrage Rapide

### Lancement
```bash
python main.py
```

### Premier Workflow (5 minutes)

1. Cliquez sur "📁 Charger Données Excel"
2. Sélectionnez votre fichier (ex: modele test.xlsx)
3. Choisissez "Saison Sèche" et une année
4. Cliquez sur "🔍 Analyser"
5. Cliquez sur "🎯 Prédire"
6. Consultez les résultats dans les onglets

## Interface Utilisateur

### En-tête
- Titre de l'application
- Logo du barrage (fond semi-transparent)

### Panneau de Contrôle
- **Charger Données**: Importer votre fichier Excel
- **Saison**: Choisir Sèche ou Pluies
- **Année**: Sélectionner l'année hydrologique
- **Modèle**: Choisir l'algorithme de prédiction
- **Analyser**: Lancer l'analyse hydrologique
- **Prédire**: Lancer la prédiction

### Onglets

#### 📊 Données
- Informations sur les données chargées
- Aperçu des données (tableau)
- Export des bases saisonnières

#### 📈 Analyse
- Analyse temporelle des débits
- Statistiques descriptives
- Tendances et anomalies
- Autocorrélation

#### 🤖 Prédiction
- Résultats du modèle
- Métriques de performance (RMSE, MAE, R²)
- Importance des variables
- Bouton de téléchargement

#### 🌧️ Climat
- Corrélations débits-climat
- Distribution des pluies
- Variables disponibles
- Prédictions climatiques

#### 📤 Export
- Export Excel complet
- Rapport PDF professionnel

## Workflow Complet

### Étape 1: Préparation des Données

Votre fichier Excel doit contenir:
- **Date**: Format date (JJ/MM/AAAA)
- **Débits**: Valeurs numériques (m³/s)
- **Pluie**: Précipitations (mm)
- **Tmax**: Température maximale (°C)
- **Tmin**: Température minimale (°C)
- **ETP**: Évapotranspiration (mm)

### Étape 2: Chargement

1. Cliquez sur "📁 Charger Données Excel"
2. Naviguez vers votre fichier
3. Attendez le message de confirmation
4. Vérifiez les informations dans l'onglet "Données"

### Étape 3: Sélection de la Saison

**Saison Sèche**: 1er décembre → 31 mai
- Débits généralement plus faibles
- Moins de pluies
- Gestion de la ressource critique

**Saison des Pluies**: 1er juin → 30 novembre
- Débits plus élevés
- Pluies abondantes
- Risque de crues

### Étape 4: Analyse

Cliquez sur "🔍 Analyser" pour obtenir:

**Analyse Temporelle**:
- Moyenne, médiane, écart-type
- Minimum et maximum
- Coefficient de variation

**Tendance**:
- Type (croissante/décroissante)
- Pente de la tendance
- Significativité (R², p-value)

**Anomalies**:
- Nombre de valeurs aberrantes
- Indices et valeurs

**Autocorrélation**:
- Dépendances temporelles
- Lag 1 à 7 jours

### Étape 5: Choix du Modèle

**Random Forest** (Recommandé)
- Très performant
- Robuste aux outliers
- Importance des variables

**Régression Linéaire**
- Simple et rapide
- Interprétable
- Bon pour tendances linéaires

**SARIMA**
- Spécialisé séries temporelles
- Capture la saisonnalité
- Plus lent

**XGBoost**
- Très précis
- Rapide
- Bon pour données complexes

**AdaBoost**
- Ensemble learning
- Bon compromis

### Étape 6: Prédiction

1. Sélectionnez le modèle
2. Cliquez sur "🎯 Prédire"
3. Attendez le calcul (10-30 secondes)
4. Consultez les résultats

### Étape 7: Analyse Climatique

L'onglet "🌧️ Climat" affiche automatiquement:
- Corrélations entre débits et variables climatiques
- Distribution des pluies
- Statistiques mensuelles

### Étape 8: Export

**Excel**:
- Données brutes
- Prédictions
- Métriques
- Analyses mensuelles

**PDF**:
- Rapport professionnel
- Graphiques
- Interprétations
- Métriques

## Interprétation des Résultats

### Métriques de Performance

**RMSE (Root Mean Square Error)**
- Erreur quadratique moyenne
- Plus faible = meilleur
- Unité: m³/s
- Exemple: RMSE = 10 → erreur moyenne de 10 m³/s

**MAE (Mean Absolute Error)**
- Erreur absolue moyenne
- Plus faible = meilleur
- Plus robuste que RMSE
- Exemple: MAE = 8 → erreur typique de 8 m³/s

**R² (Coefficient de Détermination)**
- Qualité de l'ajustement
- Entre 0 et 1
- Plus proche de 1 = meilleur
- Interprétation:
  - R² > 0.9: Excellent
  - R² > 0.7: Bon
  - R² > 0.5: Acceptable
  - R² < 0.5: À améliorer

### Corrélations Climat-Débits

**Corrélation Positive** (r > 0)
- Les deux variables augmentent ensemble
- Exemple: Pluie ↑ → Débits ↑

**Corrélation Négative** (r < 0)
- Une variable augmente, l'autre diminue
- Exemple: ETP ↑ → Débits ↓

**Force de la Corrélation**
- |r| > 0.7: Forte
- |r| > 0.4: Modérée
- |r| < 0.4: Faible

**P-value**
- < 0.05: Corrélation significative
- > 0.05: Non significative

### Importance des Variables

Le graphique montre quelles variables influencent le plus les prédictions:
- Plus la barre est longue, plus la variable est importante
- Lag features (débits passés) souvent les plus importants
- Variables climatiques apportent information complémentaire

## Export des Rapports

### Export Excel

Contient plusieurs feuilles:
1. **Données**: Données brutes de la saison
2. **Prédictions**: Valeurs réelles vs prédites
3. **Métriques**: RMSE, MAE, R²
4. **Analyse Mensuelle**: Statistiques par mois
5. **Corrélations Climat**: Relations climat-débits

### Rapport PDF

Structure professionnelle:
1. **Page de garde**: Titre, date, saison
2. **Informations générales**: Saison, année, modèle
3. **Métriques**: Tableau des performances
4. **Graphiques**: Comparaisons visuelles
5. **Corrélations**: Heatmap climat-débits

## FAQ

### Q: Combien de données minimum sont nécessaires?
R: Au moins 30 jours pour une analyse, 90 jours recommandés pour une prédiction fiable.

### Q: Quel modèle choisir?
R: Random Forest pour débuter. XGBoost si vous avez beaucoup de données. SARIMA pour capturer la saisonnalité.

### Q: Que faire si R² est faible?
R: 
- Vérifier la qualité des données
- Essayer un autre modèle
- Ajouter plus de données historiques
- Vérifier les valeurs aberrantes

### Q: Comment interpréter une corrélation de 0.6?
R: Corrélation modérée positive. La variable explique environ 36% (0.6²) de la variance des débits.

### Q: Les prédictions sont-elles fiables?
R: Fiabilité dépend du R². R² > 0.8 = prédictions fiables. Toujours vérifier avec expertise terrain.

### Q: Puis-je utiliser des données incomplètes?
R: Oui, mais les lignes avec valeurs manquantes seront ignorées. Complétez si possible.

### Q: Comment exporter juste les prédictions?
R: Onglet Prédiction → Bouton "📥 Télécharger Prédictions" → Choisir Excel.

### Q: L'analyse climatique est-elle automatique?
R: Oui, elle se lance automatiquement après l'analyse des débits.

### Q: Puis-je comparer plusieurs modèles?
R: Oui, lancez plusieurs prédictions avec différents modèles et comparez les R².

### Q: Que signifie "Saison 2020-2021"?
R: Saison sèche du 1er décembre 2020 au 31 mai 2021.

## Conseils d'Expert

1. **Toujours vérifier les données** avant l'analyse
2. **Comparer plusieurs modèles** pour choisir le meilleur
3. **Analyser les résidus** pour détecter les biais
4. **Considérer le contexte** hydrologique local
5. **Valider avec expertise** terrain
6. **Documenter les hypothèses** dans vos rapports
7. **Archiver les résultats** pour suivi temporel

## Support Technique

Pour toute question:
- Consultez d'abord ce guide
- Vérifiez les messages d'erreur
- Consultez README.md pour installation
- Vérifiez INSTALLATION.md pour dépendances

---

**Bonne analyse! 🌊**
