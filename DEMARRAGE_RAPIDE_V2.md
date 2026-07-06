# ⚡ Démarrage Rapide - Version 2

## 🎯 Nouvelle Structure Simplifiée

L'application est maintenant en **2 PHASES SÉPARÉES**:

---

## 🚀 Lancement

```bash
python main.py
```

Un menu apparaît avec 2 choix:
- **Phase 1**: Transformation Saisonnière
- **Phase 2**: Analyse et Prédiction

---

## 📂 PHASE 1: Transformation (2 minutes)

### Objectif
Convertir votre fichier brut en fichiers saisonniers.

### Étapes
1. Cliquer sur **"Phase 1"** dans le menu
2. Cliquer sur **"Charger Fichier Brut"**
3. Sélectionner votre fichier (ex: "modele test.xlsx")
4. Cliquer sur **"Exporter Saison Sèche"** → Enregistrer `saison_seche.xlsx`
5. Cliquer sur **"Exporter Saison Pluies"** → Enregistrer `saison_pluies.xlsx`

### Résultat
Vous avez maintenant 2 fichiers:
- `saison_seche.xlsx` (1er déc → 31 mai)
- `saison_pluies.xlsx` (1er juin → 30 nov)

---

## 🎯 PHASE 2: Analyse et Prédiction (5 minutes)

### Objectif
Analyser et prédire l'année suivante.

### Étapes

#### 1. Lancement
- Fermer Phase 1
- Relancer `python main.py`
- Cliquer sur **"Phase 2"**

#### 2. Chargement
- Cliquer sur **"Charger Fichier Saisonnier"**
- Sélectionner `saison_seche.xlsx` (ou `saison_pluies.xlsx`)

#### 3. Configuration
L'application propose une configuration par défaut (80% train, 20% test).

Vous pouvez ajuster:
- **Période d'entraînement**: De l'année X à l'année Y
- **Période de test**: De l'année Z à l'année W

Exemple:
```
Fichier contient: Années 1 à 20 (2001-2002 à 2020-2021)

Configuration:
- Entraînement: Années 1 à 16
- Test: Années 17 à 20
```

#### 4. Sélection du Modèle
Choisir parmi:
- Random Forest (recommandé)
- XGBoost
- Régression Linéaire
- SARIMA
- AdaBoost

#### 5. Analyse
- Cliquer sur **"Analyser"**
- Consulter l'onglet **"Analyse"**
- Voir les statistiques sur toutes les années

#### 6. Prédiction
- Cliquer sur **"Prédire Année Suivante"**
- Consulter l'onglet **"Prédiction"**
- Voir les métriques (RMSE, MAE, R²)

#### 7. Export
- Cliquer sur **"Exporter"**
- Enregistrer les résultats

---

## 📊 Exemple Complet

### Scénario
Vous avez des données de 2001 à 2022.

### Phase 1
```bash
python main.py → Phase 1
Charger: modele_test.xlsx
Exporter: saison_seche.xlsx
```

**Résultat**: `saison_seche.xlsx` contient 2001-2002 à 2021-2022

### Phase 2
```bash
python main.py → Phase 2
Charger: saison_seche.xlsx

Configuration:
- Train: Années 1-15 (2001-2002 à 2015-2016)
- Test: Années 16-21 (2016-2017 à 2021-2022)

Modèle: Random Forest

Analyser → Voir statistiques globales
Prédire → Prédiction de 2022-2023 (année suivante!)
```

---

## 🎯 Points Clés

### Phase 1
✅ Fichier brut → Fichiers saisonniers
✅ Simple et rapide
✅ À faire une seule fois

### Phase 2
✅ Fichier saisonnier → Prédiction année n+1
✅ Contrôle total sur train/test
✅ Analyse sur toutes les années
✅ Prédiction de l'année future

---

## 💡 Conseils

### Répartition Train/Test
- **80/20**: Standard (80% train, 20% test)
- **70/30**: Plus de données de test
- **90/10**: Plus de données d'entraînement

### Choix du Modèle
- **Random Forest**: Bon compromis, robuste
- **XGBoost**: Très performant, rapide
- **SARIMA**: Spécialisé séries temporelles
- **Régression Linéaire**: Simple, rapide

### Interprétation R²
- **R² > 0.8**: Excellent modèle
- **R² > 0.6**: Bon modèle
- **R² > 0.4**: Acceptable
- **R² < 0.4**: À améliorer

---

## 🆘 Problèmes Courants

### "Colonne saison_annee non trouvée"
→ Utilisez un fichier exporté de Phase 1

### "Pas assez de données"
→ Ajustez les périodes train/test

### "R² négatif"
→ Essayez un autre modèle ou ajustez les périodes

---

## 📞 Aide

Consultez:
- `NOUVELLE_STRUCTURE.md` - Structure détaillée
- `README.md` - Documentation complète
- `GUIDE_UTILISATEUR.md` - Manuel utilisateur

---

**Prêt à commencer? Lancez `python main.py`!** 🚀
