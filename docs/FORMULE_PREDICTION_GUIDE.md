# Guide Utilisateur - Formule de Prédiction à 5 Phases

## 📋 Table des Matières

1. [Introduction](#introduction)
2. [Accès à la Formule](#accès-à-la-formule)
3. [Phase 1: Formule Maîtresse](#phase-1-formule-maîtresse)
4. [Phase 2: Coefficients](#phase-2-coefficients)
5. [Phase 3: Calculateur](#phase-3-calculateur)
6. [Phase 4: Tableau Complet](#phase-4-tableau-complet)
7. [Phase 5: Analyse Comparative](#phase-5-analyse-comparative)
8. [Paramètres Clés](#paramètres-clés)
9. [Interprétation des Résultats](#interprétation-des-résultats)
10. [FAQ et Dépannage](#faq-et-dépannage)

---

## Introduction

La **Formule de Prédiction à 5 Phases** est un outil avancé pour prédire les débits de la rivière Tadang pendant la saison des pluies (1er juillet au 30 novembre, 153 jours).

### Formule Maîtresse

```
Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]
```

Où:
- **P(t)**: Polynôme d'ordre 6 (R²=0.988)
- **k(A)**: Coefficient annuel (Q̄_année / 739)
- **Cm**: Coefficient mensuel
- **ε**: Taux d'erreur (1% à 8%)

---

## Accès à la Formule

### Étape 1: Charger les Données
1. Lancez l'application Phase 2
2. Cliquez sur **"📁 Charger Fichier Saisonnier"**
3. Sélectionnez votre fichier Excel avec les données historiques

### Étape 2: Ouvrir le Menu des Phases
1. Cliquez sur le bouton **"🔮 Générer Prédictions (Formule)"**
2. Un dialogue s'ouvre avec 5 phases disponibles
3. Chaque phase a un bouton **"?"** pour afficher l'aide

---

## Phase 1: Formule Maîtresse

### Description
Visualisez la formule complète et calculez des exemples de débits.

### Utilisation
1. Sélectionnez **"Phase 1: Formule Maîtresse"**
2. Saisissez les paramètres:
   - **k(A)**: Coefficient annuel (ex: 1.0 pour année normale)
   - **ε**: Taux d'erreur (recommandé: 5%)
3. Cliquez sur **"🧮 Calculer"**

### Résultats Affichés
- Formule complète avec tous les coefficients
- Polynôme P(t) d'ordre 6
- Coefficients mensuels (Cm)
- Exemples de calcul pour 5 jours clés

### Exemple
```
Paramètres:
- k(A) = 1.15 (année humide)
- ε = 0.05 (5%)

Résultat pour t=77 (milieu de saison):
- P(77) = 850.23 m³/s
- Q centrale = 1,127.55 m³/s
- Q min = 1,037.35 m³/s
- Q max = 1,217.75 m³/s
```

---

## Phase 2: Coefficients

### Description
Consultez les 3 tableaux de coefficients utilisés dans la formule.

### Tableaux Disponibles

#### Tableau A: Coefficients Annuels
Affiche k(A) pour chaque année de vos données historiques.

**Colonnes:**
- Année
- k(A)
- Humidité relative (%)
- Q moyen (m³/s)
- Rang humidité
- Statut (Très humide, Humide, Normal, Sec, Très sec)

#### Tableau B: Coefficients Mensuels
Statistiques pour chaque mois de la saison des pluies.

**Colonnes:**
- Mois
- Cm (coefficient mensuel)
- Q moyen (m³/s)
- Intervalle P10-P90
- Tendance %/jour
- Succession max ↑/↓

#### Tableau C: Coefficients du Polynôme
Détails du polynôme P(t) d'ordre 6.

**Colonnes:**
- Terme (t⁶, t⁵, etc.)
- Coefficient
- Exposant de t
- Contribution
- R² = 0.988

### Export
Cliquez sur **"📊 Exporter en Excel"** pour sauvegarder les 3 tableaux.

---

## Phase 3: Calculateur

### Description
Calculez rapidement le débit pour un jour spécifique.

### Utilisation
1. Sélectionnez **"Phase 3: Calculateur"**
2. Saisissez:
   - **t**: Jour de saison (1-153)
   - **k(A)**: Coefficient annuel
   - **ε**: Taux d'erreur
3. Cliquez sur **"🧮 Calculer"**

### Correspondance Jour → Date
- t = 1 → 1er juillet
- t = 31 → 31 juillet
- t = 32 → 1er août
- t = 153 → 30 novembre

### Résultats
- Date calendaire
- Mois déduit automatiquement
- Cm appliqué
- P(t) calculé
- Q centrale, Q min, Q max
- Statut du débit

### Exemple
```
Entrées:
- t = 100 (9 octobre)
- k(A) = 1.0
- ε = 0.05

Résultats:
- Date: 09/10/2024
- Mois: Octobre
- Cm: 1.333
- P(t): 725.45 m³/s
- Q centrale: 967.02 m³/s
- Q min: 889.66 m³/s
- Q max: 1,044.38 m³/s
- Statut: ✅ Normal
```

---

## Phase 4: Tableau Complet

### Description
Générez le tableau complet de 153 jours avec export Excel/PDF.

### Utilisation
1. Sélectionnez **"Phase 4: Tableau Complet"**
2. Saisissez:
   - **k(A)**: Coefficient annuel
   - **ε**: Taux d'erreur
   - **Année**: Année de prédiction
3. Cliquez sur **"🔄 Générer"**

### Colonnes du Tableau
| Colonne | Description |
|---------|-------------|
| t | Jour de saison (1-153) |
| Date | Date calendaire |
| Mois | Nom du mois |
| P(t) | Valeur du polynôme (m³/s) |
| Q centrale | Débit prédit central (m³/s) |
| Q min (-8%) | Borne inférieure (m³/s) |
| Q max (+8%) | Borne supérieure (m³/s) |
| Q réelle | Débit observé (à remplir) |
| Écart % | Écart entre prédit et observé |
| Statut | 🚨 🔔 ✅ 🌤️ ℹ️ |

### Export
- **📊 Exporter Excel**: Format .xlsx pour analyse
- **📄 Exporter PDF**: Format PDF avec graphique

Les fichiers sont sauvegardés dans `exports/` avec le format:
```
predictions_formule_YYYYMMDD_HHMMSS.xlsx
```

### Métadonnées Incluses
- k(A) utilisé
- ε utilisé
- Date et heure de génération
- Année de prédiction

---

## Phase 5: Analyse Comparative

### Description
Comparez les années et les mois pour identifier les périodes humides/sèches.

### Classement Annuel
Classe toutes les années par ordre d'humidité décroissante.

**Colonnes:**
- Rang (1 = plus humide)
- Année
- k(A)
- Q moyen (m³/s)
- Qualification
- vs Moyenne (%)

**Qualifications:**
- **Très humide**: k(A) > 1.2
- **Humide**: 1.1 < k(A) ≤ 1.2
- **Normal**: 0.9 ≤ k(A) ≤ 1.1
- **Sec**: 0.8 ≤ k(A) < 0.9
- **Très sec**: k(A) < 0.8

### Classement Mensuel
Classe les 5 mois de la saison des pluies.

**Colonnes:**
- Rang (1 = plus humide)
- Mois
- Q moyen (m³/s)
- Cm
- Tendance %/jour
- Variabilité CV
- Statut

### Export
Cliquez sur **"📊 Exporter en Excel"** pour sauvegarder les 2 classements.

---

## Paramètres Clés

### Coefficient Annuel k(A)

**Définition:** k(A) = Q̄_année / Q̄_historique (739 m³/s)

**Signification:**
- Représente l'humidité relative de l'année
- k(A) = 1.0 → Année normale
- k(A) > 1.0 → Année humide
- k(A) < 1.0 → Année sèche

**Valeurs Typiques:**
| k(A) | Qualification | Exemple Q̄ |
|------|---------------|-----------|
| 1.30 | Très humide | 960 m³/s |
| 1.15 | Humide | 850 m³/s |
| 1.00 | Normal | 739 m³/s |
| 0.85 | Sec | 628 m³/s |
| 0.70 | Très sec | 517 m³/s |

**Comment Choisir k(A):**
1. Consultez Phase 2 ou Phase 5 pour voir les k(A) historiques
2. Pour prédire une année similaire à 2020, utilisez k(A) de 2020
3. Pour une année "moyenne", utilisez k(A) = 1.0
4. Pour un scénario pessimiste, utilisez k(A) = 0.8
5. Pour un scénario optimiste, utilisez k(A) = 1.2

### Taux d'Erreur ε

**Définition:** Marge d'erreur appliquée à toute la saison

**Plage Valide:** 1% à 8% (0.01 à 0.08)

**Valeur Recommandée:** 5% (0.05)

**Utilisation:**
- Calcule les bornes Q_min et Q_max
- Q_min = Q centrale × (1 - 0.08) = Q centrale × 0.92
- Q_max = Q centrale × (1 + 0.08) = Q centrale × 1.08

**Comment Choisir ε:**
- **ε = 0.03 (3%)**: Prédiction très confiante
- **ε = 0.05 (5%)**: Recommandé (équilibre confiance/prudence)
- **ε = 0.08 (8%)**: Prédiction prudente avec large marge

### Coefficients Mensuels Cm

**Valeurs Fixes:**
| Mois | Cm | Signification |
|------|-----|---------------|
| Juillet | 0.697 | Début de saison (débits modérés) |
| Août | 1.011 | Montée des eaux |
| Septembre | 1.300 | Pic de la saison |
| Octobre | 1.333 | Maximum de la saison |
| Novembre | 0.658 | Fin de saison (décrue) |

**Interprétation:**
- Cm > 1.0 → Mois humide (septembre, octobre)
- Cm ≈ 1.0 → Mois normal (août)
- Cm < 1.0 → Mois sec (juillet, novembre)

---

## Interprétation des Résultats

### Statuts de Débit

| Statut | Icône | Plage Q (m³/s) | Signification |
|--------|-------|----------------|---------------|
| Dangereux | 🚨 | > 1200 | Risque d'inondation élevé |
| Élevé | 🔔 | 900-1200 | Surveillance accrue recommandée |
| Normal | ✅ | 600-900 | Conditions normales |
| Modéré | 🌤️ | 400-600 | Débit modéré |
| Bas | ℹ️ | < 400 | Débit faible |

### Analyse des Prédictions

**Débit Moyen de la Saison:**
```
Q̄_saison = Somme(Q centrale) / 153
```

**Comparaison avec l'Historique:**
```
Écart = (Q̄_saison - 739) / 739 × 100%
```

**Exemple:**
- Q̄_saison = 850 m³/s
- Écart = (850 - 739) / 739 × 100% = +15%
- Interprétation: Saison 15% plus humide que la moyenne

### Validation des Prédictions

**Après la Saison:**
1. Remplissez la colonne "Q réelle" dans Phase 4
2. La colonne "Écart %" se calcule automatiquement
3. Analysez les écarts pour évaluer la précision

**Métriques de Performance:**
- **Écart moyen < 10%**: Excellente prédiction
- **Écart moyen 10-20%**: Bonne prédiction
- **Écart moyen > 20%**: Prédiction à améliorer

---

## FAQ et Dépannage

### Questions Fréquentes

**Q1: Quelle est la différence entre "Formule" et "ML" ?**
- **Formule**: Utilise le polynôme mathématique (Phase 1-5)
- **ML**: Utilise un modèle d'apprentissage automatique (nécessite entraînement)

**Q2: Puis-je utiliser la formule sans données historiques ?**
- Non, vous devez charger un fichier avec au moins une année de données
- Les coefficients k(A) sont calculés à partir de vos données

**Q3: Comment choisir k(A) pour une année future ?**
- Consultez Phase 5 pour voir les k(A) historiques
- Utilisez k(A) d'une année similaire
- Ou utilisez k(A) = 1.0 pour une année "moyenne"

**Q4: Pourquoi 153 jours exactement ?**
- Saison des pluies: 1er juillet au 30 novembre
- Juillet: 31 jours
- Août: 31 jours
- Septembre: 30 jours
- Octobre: 31 jours
- Novembre: 30 jours
- **Total: 153 jours**

**Q5: Puis-je modifier les coefficients mensuels Cm ?**
- Non, les Cm sont fixes et basés sur l'analyse historique
- Ils représentent la saisonnalité typique de la rivière

**Q6: Que signifie R² = 0.988 ?**
- Le polynôme explique 98.8% de la variance des débits
- Excellente précision du modèle mathématique

### Dépannage

**Problème: "Erreur: Jour de saison doit être entre 1 et 153"**
- **Solution**: Vérifiez que t est entre 1 et 153

**Problème: "Erreur: Coefficient annuel doit être strictement positif"**
- **Solution**: k(A) doit être > 0 (typiquement entre 0.5 et 1.5)

**Problème: "Erreur: Taux d'erreur doit être entre 1% et 8%"**
- **Solution**: ε doit être entre 0.01 et 0.08

**Problème: "Veuillez d'abord charger un fichier"**
- **Solution**: Cliquez sur "📁 Charger Fichier Saisonnier" avant d'utiliser la formule

**Problème: "Export échoué"**
- **Solution**: Vérifiez que le dossier `exports/` existe
- Vérifiez les permissions d'écriture
- Fermez le fichier Excel s'il est déjà ouvert

**Problème: "Tableau vide ou incomplet"**
- **Solution**: Vérifiez que vos données contiennent la colonne `saison_annee`
- Vérifiez que les débits sont dans la colonne `debits`

### Support

Pour toute question ou problème:
1. Consultez l'aide contextuelle (bouton "?" dans chaque phase)
2. Vérifiez les logs dans `logs/formula_predictions_YYYYMMDD.log`
3. Contactez l'équipe de support technique

---

## Annexes

### Formule Complète

```
P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴
       − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2

Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]

Q_inf = P(t) × k(A) × Cm × 0.92
Q_sup = P(t) × k(A) × Cm × 1.08
```

### Performances

| Opération | Temps | Objectif |
|-----------|-------|----------|
| Calcul P(t) | < 10ms | ✅ |
| Génération 153 jours | < 500ms | ✅ |
| Affichage tableaux | < 2s | ✅ |
| Export Excel | < 3s | ✅ |
| Export PDF | < 5s | ✅ |

### Références

- **R² du polynôme**: 0.988
- **RMSE**: 25.3 m³/s
- **Q̄ historique**: 739 m³/s
- **Période**: 1er juillet - 30 novembre (153 jours)
- **Rivière**: Tadang

---

**Version:** 1.0  
**Date:** Avril 2026  
**Auteur:** Système de Prédiction Hydrologique
