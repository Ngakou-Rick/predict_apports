# Guide de Test de l'Interface Utilisateur

**Date:** 20 Avril 2026  
**Objectif:** Tester les 5 phases de la formule via l'interface graphique PyQt5

---

## 🚀 Lancement de l'Application

### Option 1: Via le script principal
```bash
python main.py
```

### Option 2: Via le script batch (Windows)
```bash
run.bat
```

### Option 3: Directement Phase 2
```bash
python phase2_prediction.py
```

---

## 📋 Procédure de Test Complète

### Étape 1: Lancer l'Application

1. Exécutez `python main.py`
2. Sélectionnez **"PHASE 2: Analyse et Prédiction"**
3. La fenêtre de prédiction s'ouvre

### Étape 2: Charger les Données

1. Cliquez sur **"📁 Charger Fichier Saisonnier"**
2. Sélectionnez le fichier `saison_pluies.xlsx`
3. Attendez le message de confirmation
4. Vérifiez que les données sont chargées (2,142 lignes, 14 années)

### Étape 3: Ouvrir le Menu des Phases

1. Cliquez sur **"🔮 Générer Prédictions (Formule)"**
2. Un dialogue s'ouvre avec 5 boutons colorés
3. Chaque bouton a un **"?"** pour l'aide contextuelle

---

## 🧪 Test Phase 1: Formule Maîtresse

### Actions
1. Cliquez sur **"Phase 1: Formule Maîtresse"**
2. Un dialogue s'ouvre avec la formule complète

### Vérifications
- [ ] Formule Q(t,A) = P(t) × k(A) × Cm × [1 ± ε] affichée
- [ ] Polynôme P(t) d'ordre 6 affiché avec tous les coefficients
- [ ] Coefficients mensuels (Cm) affichés pour les 5 mois
- [ ] Exemples de calcul pour 5 jours clés affichés
- [ ] Formulaire de saisie k(A) et ε présent
- [ ] Bouton "🧮 Calculer" fonctionnel

### Test de Calcul
1. Saisissez k(A) = 1.0
2. Saisissez ε = 0.05
3. Cliquez sur "🧮 Calculer"
4. Vérifiez les résultats affichés

**Résultats Attendus:**
- Exemples pour t=1, 31, 77, 123, 153
- Valeurs de P(t), Q centrale, Q min, Q max
- Mois déduits automatiquement

---

## 🧪 Test Phase 2: Coefficients

### Actions
1. Retournez au dialogue de sélection
2. Cliquez sur **"Phase 2: Coefficients"**
3. Un dialogue s'ouvre avec 3 onglets

### Vérifications

#### Onglet "Tableau A - Annuel"
- [ ] 14 années affichées (2011-2024)
- [ ] Colonnes: Année, k(A), Q moy, Humidité relative, Rang, Statut
- [ ] Tri par rang d'humidité (du plus humide au plus sec)
- [ ] 2019 en tête (k(A)=1.229, Très humide)
- [ ] 2014 en dernier (k(A)=0.778, Très sec)

#### Onglet "Tableau B - Mensuel"
- [ ] 5 mois affichés (Juillet-Novembre)
- [ ] Colonnes: Mois, Cm, Q moy, Intervalle P10-P90, Tendance %/j
- [ ] Coefficients mensuels corrects:
  - Juillet: 0.697
  - Août: 1.011
  - Septembre: 1.300
  - Octobre: 1.333
  - Novembre: 0.658

#### Onglet "Tableau C - Polynôme"
- [ ] 7 termes + R² affichés
- [ ] R² = 0.988 affiché
- [ ] Coefficients du polynôme corrects

#### Bouton Export
- [ ] Bouton "📊 Exporter en Excel" présent
- [ ] Clic génère un fichier dans exports/
- [ ] Fichier contient les 3 tableaux

---

## 🧪 Test Phase 3: Calculateur

### Actions
1. Retournez au dialogue de sélection
2. Cliquez sur **"Phase 3: Calculateur"**
3. Un formulaire s'ouvre

### Vérifications du Formulaire
- [ ] Champ "t" (jour de saison 1-153)
- [ ] Champ "k(A)" (coefficient annuel)
- [ ] Champ "ε" (taux d'erreur 0.01-0.08)
- [ ] Bouton "🧮 Calculer"
- [ ] Infobulles explicatives sur chaque champ

### Tests de Calcul

#### Test 1: Début de saison
1. Saisissez t = 1
2. Saisissez k(A) = 1.0
3. Saisissez ε = 0.05
4. Cliquez "🧮 Calculer"

**Résultats Attendus:**
- Date: 01/07/2024
- Mois: Juillet
- Cm: 0.697
- P(t): 385.49 m³/s
- Q centrale: 268.69 m³/s
- Q min: 247.19 m³/s
- Q max: 290.18 m³/s
- Statut: ℹ️ Bas

#### Test 2: Milieu de saison
1. Saisissez t = 77
2. Saisissez k(A) = 1.2 (année humide)
3. Saisissez ε = 0.05
4. Cliquez "🧮 Calculer"

**Résultats Attendus:**
- Date: 15/09/2024
- Mois: Septembre
- Cm: 1.300
- Q centrale: ~1,502 m³/s
- Statut: 🚨 Dangereux

#### Test 3: Validation des erreurs
1. Saisissez t = 200 (invalide)
2. Cliquez "🧮 Calculer"
3. **Attendu:** Message d'erreur "Jour de saison doit être entre 1 et 153"

4. Saisissez t = 50, k(A) = -1 (invalide)
5. Cliquez "🧮 Calculer"
6. **Attendu:** Message d'erreur "Coefficient annuel doit être strictement positif"

7. Saisissez t = 50, k(A) = 1.0, ε = 0.15 (invalide)
8. Cliquez "🧮 Calculer"
9. **Attendu:** Message d'erreur "Taux d'erreur doit être entre 1% et 8%"

---

## 🧪 Test Phase 4: Tableau Complet

### Actions
1. Retournez au dialogue de sélection
2. Cliquez sur **"Phase 4: Tableau Complet"**
3. Un formulaire s'ouvre

### Vérifications du Formulaire
- [ ] Champ "k(A)"
- [ ] Champ "ε"
- [ ] Champ "Année"
- [ ] Bouton "🔄 Générer"
- [ ] Boutons "📊 Exporter Excel" et "📄 Exporter PDF"

### Test de Génération

1. Saisissez k(A) = 1.0
2. Saisissez ε = 0.05
3. Saisissez Année = 2025
4. Cliquez "🔄 Générer"

**Vérifications:**
- [ ] Tableau de 153 lignes affiché
- [ ] 10 colonnes présentes:
  - t, Date, Mois, P(t), Q centrale, Q min, Q max, Q réelle, Écart %, Statut
- [ ] Dates correctes (01/07/2025 → 30/11/2025)
- [ ] Statuts affichés avec emojis (🚨, 🔔, ✅, 🌤️, ℹ️)
- [ ] Génération rapide (<1 seconde)

### Test d'Export Excel

1. Cliquez sur "📊 Exporter Excel"
2. Vérifiez le message de confirmation
3. Ouvrez le fichier dans exports/

**Vérifications du fichier Excel:**
- [ ] Fichier nommé: predictions_formule_YYYYMMDD_HHMMSS.xlsx
- [ ] Feuille "Prédictions" avec 153 lignes
- [ ] Feuille "Métadonnées" avec k(A), ε, date génération
- [ ] Formatage correct (en-têtes colorés)
- [ ] Toutes les colonnes visibles

### Test d'Export PDF

1. Cliquez sur "📄 Exporter PDF"
2. Vérifiez le message de confirmation
3. Ouvrez le fichier PDF dans exports/

**Vérifications du fichier PDF:**
- [ ] Graphique des prédictions affiché
- [ ] Courbe Q centrale visible
- [ ] Zone d'intervalle ±8% visible
- [ ] Lignes de seuil (400, 600, 900, 1200) affichées
- [ ] Titre avec k(A) et ε
- [ ] Dates sur l'axe X
- [ ] Débits sur l'axe Y

---

## 🧪 Test Phase 5: Analyse Comparative

### Actions
1. Retournez au dialogue de sélection
2. Cliquez sur **"Phase 5: Analyse Comparative"**
3. Un dialogue s'ouvre avec 2 onglets

### Vérifications

#### Onglet "Classement Annuel"
- [ ] 14 années affichées (2011-2024)
- [ ] Colonnes: Rang, Année, k(A), Q moy, Qualif., vs Moyenne
- [ ] Tri par k(A) décroissant
- [ ] Rang 1: 2019 (Très humide, +22.9%)
- [ ] Rang 14: 2014 (Très sec, -22.2%)
- [ ] Qualifications correctes:
  - Très humide: k(A) > 1.2
  - Humide: 1.1 < k(A) ≤ 1.2
  - Normal: 0.9 ≤ k(A) ≤ 1.1
  - Sec: 0.8 ≤ k(A) < 0.9
  - Très sec: k(A) < 0.8

#### Onglet "Classement Mensuel"
- [ ] 5 mois affichés (Juillet-Novembre)
- [ ] Colonnes: Rang, Mois, Q moy, Cm, Tendance %/j, Variabilité CV, Statut
- [ ] Tri par Q moy décroissant
- [ ] Rang 1: Octobre (985.09 m³/s)
- [ ] Rang 5: Novembre (486.26 m³/s)

#### Bouton Export
- [ ] Bouton "📊 Exporter en Excel" présent
- [ ] Clic génère un fichier dans exports/
- [ ] Fichier contient les 2 classements

---

## 🧪 Test Navigation Entre Phases

### Vérifications
- [ ] Bouton "Retour" présent dans chaque phase
- [ ] Clic sur "Retour" revient au dialogue de sélection
- [ ] Données saisies (k(A), ε) préservées entre phases
- [ ] Possibilité de naviguer librement entre les 5 phases

---

## 🧪 Test Aide Contextuelle

### Dans le Dialogue de Sélection
1. Cliquez sur le **"?"** à côté de "Phase 1"
2. Vérifiez qu'une fenêtre d'aide s'ouvre
3. Vérifiez le contenu en français
4. Répétez pour les 5 phases

**Vérifications:**
- [ ] Aide Phase 1: Explication de la formule maîtresse
- [ ] Aide Phase 2: Explication des 3 tableaux
- [ ] Aide Phase 3: Explication du calculateur
- [ ] Aide Phase 4: Explication du tableau complet
- [ ] Aide Phase 5: Explication des classements

### Dans les Formulaires
- [ ] Infobulles sur les champs de saisie
- [ ] Exemples de valeurs typiques affichés
- [ ] Messages d'erreur clairs en français

---

## 📊 Résumé des Tests

### Checklist Globale

#### Fonctionnalités de Base
- [ ] Application se lance sans erreur
- [ ] Chargement des données réussi
- [ ] Dialogue de sélection des phases s'ouvre
- [ ] Navigation entre phases fluide

#### Phase 1: Formule Maîtresse
- [ ] Formule affichée correctement
- [ ] Calculs corrects
- [ ] Validation des entrées fonctionnelle

#### Phase 2: Coefficients
- [ ] 3 tableaux affichés
- [ ] Détection dynamique des années (2011-2024)
- [ ] Export Excel fonctionnel

#### Phase 3: Calculateur
- [ ] Calcul jour unique correct
- [ ] Déduction automatique du mois
- [ ] Messages d'erreur appropriés

#### Phase 4: Tableau Complet
- [ ] Génération 153 lignes réussie
- [ ] Export Excel fonctionnel
- [ ] Export PDF fonctionnel
- [ ] Statuts affichés correctement

#### Phase 5: Analyse Comparative
- [ ] Classement annuel correct
- [ ] Classement mensuel correct
- [ ] Export Excel fonctionnel

#### Aide et Documentation
- [ ] Aide contextuelle accessible
- [ ] Infobulles présentes
- [ ] Messages en français

#### Performance
- [ ] Génération 153 jours < 1s
- [ ] Export Excel < 3s
- [ ] Interface réactive

---

## 🐛 Problèmes Connus et Solutions

### Problème: "Veuillez d'abord charger un fichier"
**Solution:** Chargez le fichier `saison_pluies.xlsx` avant d'utiliser la formule

### Problème: "Colonnes manquantes"
**Solution:** Vérifiez que le fichier contient les colonnes `saison_annee` et `debit` (ou `debits`)

### Problème: Export échoue
**Solution:** 
- Vérifiez que le dossier `exports/` existe
- Fermez le fichier Excel s'il est déjà ouvert
- Vérifiez les permissions d'écriture

### Problème: Graphique ne s'affiche pas
**Solution:** Vérifiez que matplotlib est installé: `pip install matplotlib`

---

## 📝 Rapport de Test

Après avoir effectué tous les tests, remplissez ce rapport:

**Date du test:** _______________  
**Testeur:** _______________  
**Version:** 1.0

### Résultats

| Phase | Statut | Commentaires |
|-------|--------|--------------|
| Phase 1 | ☐ OK ☐ KO | |
| Phase 2 | ☐ OK ☐ KO | |
| Phase 3 | ☐ OK ☐ KO | |
| Phase 4 | ☐ OK ☐ KO | |
| Phase 5 | ☐ OK ☐ KO | |
| Navigation | ☐ OK ☐ KO | |
| Aide | ☐ OK ☐ KO | |
| Exports | ☐ OK ☐ KO | |

### Bugs Trouvés
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

### Suggestions d'Amélioration
1. _______________________________________________
2. _______________________________________________
3. _______________________________________________

---

**Bonne chance pour vos tests !** 🚀

