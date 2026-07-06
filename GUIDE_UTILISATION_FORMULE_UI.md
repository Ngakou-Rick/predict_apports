# 📐 Guide d'Utilisation - Onglet Formule de Prédiction

## 🎯 Accès à la fonctionnalité

Dans l'interface principale, vous trouverez maintenant un nouvel onglet :

**📐 Formule Prédiction**

Cet onglet vous permet de générer des prédictions de débits en utilisant les formules mathématiques pour les deux saisons.

---

## 🌊 Saisons disponibles

### 1. Saison Sèche (Décembre → Juin)
- **Durée** : 212 jours
- **Période** : 1er décembre → 30 juin
- **Jour 1** = 1er décembre
- **Jour 212** = 30 juin
- **R²** : 0.994
- **Mois** : Décembre, Janvier, Février, Mars, Avril, Mai, Juin

### 2. Saison Pluies (Juillet → Novembre)
- **Durée** : 153 jours
- **Période** : 1er juillet → 30 novembre
- **Jour 1** = 1er juillet
- **Jour 153** = 30 novembre
- **R²** : 0.988
- **Mois** : Juillet, Août, Septembre, Octobre, Novembre

---

## 🎛️ Paramètres à configurer

### 1. Saison
Sélectionnez la saison pour laquelle vous voulez faire la prédiction :
- **Saison Sèche (Déc→Juin)** - 212 jours
- **Saison Pluies (Juil→Nov)** - 153 jours

### 2. Jour de saison (t)
- **Plage** : 1 à 212 (saison sèche) ou 1 à 153 (saison pluies)
- **Signification** : Jour dans la saison
- **Exemple** : 
  - Saison sèche : t=100 = mi-mars (étiage)
  - Saison pluies : t=100 = mi-octobre (crue)

### 3. Coefficient k(A)
- **Plage** : 0.1 à 2.0
- **Valeur normale** : 1.0
- **Signification** : Coefficient d'humidité de l'année
  - k(A) < 0.8 : Année très sèche
  - k(A) = 0.8-0.9 : Année sèche
  - k(A) = 0.9-1.1 : Année normale
  - k(A) = 1.1-1.2 : Année humide
  - k(A) > 1.2 : Année très humide

### 4. Taux d'erreur ε (%)
- **Plage** : 1% à 8%
- **Valeur recommandée** : 8%
- **Signification** : Marge d'incertitude
  - Q_min = Q_central × (1 - ε)
  - Q_max = Q_central × (1 + ε)

### 5. Année
- **Plage** : 2020 à 2030
- **Signification** : Année de prédiction (pour les dates)

---

## 🔢 Fonctionnalités

### 1. Calculer Jour Unique
**Bouton** : 🔢 Calculer Jour Unique

**Fonction** : Calcule le débit pour un jour spécifique

**Résultat affiché** :
- Date calendaire
- Mois
- Coefficient mensuel (Cm)
- P(t) - Valeur du polynôme
- Q centrale - Débit prédit
- Q min (-8%) - Borne inférieure
- Q max (+8%) - Borne supérieure

**Exemple d'utilisation** :
1. Sélectionner "Saison Sèche"
2. Jour = 110 (mi-mars - étiage)
3. k(A) = 1.0 (année normale)
4. ε = 8%
5. Année = 2025
6. Cliquer sur "Calculer Jour Unique"

**Résultat** : Débit prédit pour le 20 mars 2026

---

### 2. Générer Saison Complète
**Bouton** : 📊 Générer Saison Complète

**Fonction** : Génère la table journalière pour toute la saison

**Résultat** :
- Table de 212 jours (saison sèche) ou 153 jours (saison pluies)
- Statistiques globales :
  - Débit moyen
  - Débit minimum
  - Débit maximum
  - Écart-type
- Aperçu des 10 premiers jours

**Exemple d'utilisation** :
1. Sélectionner "Saison Sèche"
2. k(A) = 1.0
3. ε = 8%
4. Année = 2025
5. Cliquer sur "Générer Saison Complète"

**Résultat** : Table complète de 212 jours avec tous les débits prédits

---

### 3. Exporter vers Excel
**Bouton** : 💾 Exporter vers Excel

**Fonction** : Exporte la table complète vers un fichier Excel

**Contenu du fichier** :
- **Feuille "Prédictions"** : Table journalière complète
  - Jour de saison (t)
  - Date
  - Mois
  - P(t)
  - Cm
  - Q_central
  - Q_min
  - Q_max

- **Feuille "Paramètres"** : Paramètres utilisés
  - Saison
  - Année
  - Coefficient k(A)
  - Taux erreur ε
  - Durée

**Note** : Vous devez d'abord générer une saison complète avant d'exporter.

---

## 📊 Exemples d'utilisation

### Exemple 1 : Prédiction étiage (saison sèche)
**Objectif** : Prévoir le débit pendant l'étiage de mars

**Étapes** :
1. Onglet : **📐 Formule Prédiction**
2. Saison : **Saison Sèche (Déc→Juin)**
3. Jour : **110** (mi-mars)
4. k(A) : **0.8** (année sèche)
5. ε : **8%**
6. Année : **2025**
7. Cliquer : **🔢 Calculer Jour Unique**

**Résultat attendu** : Débit très faible (étiage), environ 7-10 m³/s

---

### Exemple 2 : Prédiction crue (saison pluies)
**Objectif** : Prévoir le débit pendant la crue d'octobre

**Étapes** :
1. Onglet : **📐 Formule Prédiction**
2. Saison : **Saison Pluies (Juil→Nov)**
3. Jour : **100** (mi-octobre)
4. k(A) : **1.2** (année humide)
5. ε : **8%**
6. Année : **2025**
7. Cliquer : **🔢 Calculer Jour Unique**

**Résultat attendu** : Débit élevé (crue), environ 1400-1600 m³/s

---

### Exemple 3 : Table complète année normale
**Objectif** : Générer toutes les prédictions pour une année normale

**Étapes** :
1. Onglet : **📐 Formule Prédiction**
2. Saison : **Saison Sèche (Déc→Juin)**
3. k(A) : **1.0** (année normale)
4. ε : **8%**
5. Année : **2025**
6. Cliquer : **📊 Générer Saison Complète**
7. Attendre la génération (212 jours)
8. Cliquer : **💾 Exporter vers Excel**
9. Choisir l'emplacement et le nom du fichier

**Résultat** : Fichier Excel avec 212 jours de prédictions

---

## 💡 Conseils d'utilisation

### Choix du coefficient k(A)
Pour choisir le bon k(A), consultez les données historiques :

**Saison Sèche** :
- 2018-2019 : k(A) = 1.39 (très humide)
- 2013-2014 : k(A) = 1.27 (très humide)
- 2023-2024 : k(A) = 1.02 (normal)
- 2012-2013 : k(A) = 0.58 (très sec)

**Saison Pluies** :
- Années humides : k(A) > 1.1
- Années normales : k(A) ≈ 1.0
- Années sèches : k(A) < 0.9

### Interprétation des résultats

**Saison Sèche** :
- **Décembre** : Décrue finale (Q élevé)
- **Mars** : Étiage maximum (Q minimum)
- **Juin** : Remontée (Q augmente)

**Saison Pluies** :
- **Juillet** : Début montée
- **Octobre** : Crue maximum (Q maximum)
- **Novembre** : Décrue

### Validation des résultats
- Vérifiez que Q_min < Q_central < Q_max
- Vérifiez que les marges sont de ±8%
- Comparez avec les données historiques

---

## ⚠️ Notes importantes

1. **Séparation des saisons** : Les formules pour saison sèche et saison pluies sont complètement différentes. Ne les mélangez pas.

2. **Qualité du modèle** :
   - Saison sèche : R² = 0.994 (excellente)
   - Saison pluies : R² = 0.988 (excellente)

3. **Limites** :
   - Les prédictions sont basées sur des données historiques (2010-2025)
   - Les événements extrêmes peuvent dépasser les marges d'erreur
   - Utilisez toujours les bornes min/max pour la planification

4. **Export** : Les fichiers Excel peuvent être ouverts dans Excel, LibreOffice, ou tout autre tableur.

---

## 🆘 Dépannage

### Problème : "Erreur lors du calcul"
**Solution** : Vérifiez que tous les paramètres sont dans les plages valides

### Problème : "Veuillez d'abord générer une table complète"
**Solution** : Cliquez sur "Générer Saison Complète" avant d'exporter

### Problème : Le jour maximum ne change pas
**Solution** : Changez d'abord la saison, le maximum s'ajustera automatiquement

---

## 📞 Support

Pour toute question ou problème :
1. Consultez ce guide
2. Vérifiez les fichiers README dans `backend/formula/`
3. Exécutez les tests : `python test_saison_seche.py`

---

**Version** : 1.0.0  
**Date** : 20 avril 2026  
**Statut** : ✅ Opérationnel
