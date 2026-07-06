# ✅ VÉRIFICATION DES FORMULES PAR SAISON

## 📊 Résumé des Différences

| Caractéristique | 🌧️ Saison des Pluies | 🌵 Saison Sèche |
|----------------|----------------------|------------------|
| **Période** | Juillet → Novembre | Décembre → Juin |
| **Durée** | 153 jours | 212 jours |
| **R²** | 0.988 | 0.994 |
| **RMSE** | 25.3 m³/s | 6.0 m³/s |
| **Q̄ historique** | 739.0 m³/s | 98.2 m³/s |

---

## 🔢 Polynômes P(t) - Ordre 6

### 🌧️ Saison des Pluies
```
P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴ 
       − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2
```

**Coefficients:**
- t⁶: 5.414e-9
- t⁵: -2.166e-6
- t⁴: 3.115e-4
- t³: -2.019e-2
- t²: 5.687e-1
- t¹: 2.741
- t⁰: 382.2

### 🌵 Saison Sèche
```
P(t) = −4.129×10⁻¹¹·t⁶ + 2.720×10⁻⁸·t⁵ − 5.603×10⁻⁶·t⁴ 
       + 3.519×10⁻⁴·t³ + 2.809×10⁻²·t² − 5.229·t + 250.7
```

**Coefficients:**
- t⁶: -4.129e-11
- t⁵: 2.720e-8
- t⁴: -5.603e-6
- t³: 3.519e-4
- t²: 2.809e-2
- t¹: -5.229
- t⁰: 250.7

---

## 📅 Coefficients Mensuels Cm

### 🌧️ Saison des Pluies (5 mois)
| Mois | Coefficient Cm |
|------|----------------|
| Juillet (7) | 0.697 |
| Août (8) | 1.011 |
| Septembre (9) | 1.300 |
| Octobre (10) | 1.333 |
| Novembre (11) | 0.658 |

### 🌵 Saison Sèche (7 mois)
| Mois | Coefficient Cm |
|------|----------------|
| Décembre (12) | 1.814 |
| Janvier (1) | 0.8654 |
| Février (2) | 0.4381 |
| Mars (3) | 0.3207 ⭐ (plus sec) |
| Avril (4) | 0.3406 |
| Mai (5) | 0.8628 |
| Juin (6) | 2.3255 |

---

## 📦 Modules Backend Vérifiés

### ✅ Tous les modules existent pour les deux saisons:

#### 🌧️ Saison des Pluies
- ✅ `formula_module.py`
- ✅ `coefficients_module.py`
- ✅ `calculator_module.py`
- ✅ `generator_module.py`
- ✅ `analyzer_module.py`

#### 🌵 Saison Sèche
- ✅ `formula_module_seche.py`
- ✅ `coefficients_module_seche.py`
- ✅ `calculator_module_seche.py`
- ✅ `generator_module_seche.py`
- ✅ `analyzer_module_seche.py`

---

## 🔄 Intégration dans Phase 2

### ✅ Flux de Travail Implémenté

1. **Étape 1: Sélection de Saison**
   - Dialogue `SeasonSelectionDialog`
   - Choix: 🌵 Saison Sèche ou 🌧️ Saison des Pluies

2. **Étape 2: Sélection de Phase**
   - Dialogue `PhaseSelectionDialog` (adapté à la saison)
   - 5 phases disponibles

3. **Étape 3: Exécution**
   - Utilise automatiquement les bons modules selon la saison

### ✅ Méthodes Mises à Jour

Toutes les méthodes acceptent maintenant le paramètre `season`:

```python
def show_phase1_formula_master(self, season='rainy')
def show_phase2_coefficients(self, season='rainy')
def show_phase3_calculator(self, season='rainy')
def show_phase4_full_table(self, season='rainy')
def show_phase5_comparative_analysis(self, season='rainy')
```

### ✅ Import Dynamique

Chaque méthode importe le bon module:

```python
if season == 'dry':
    from backend.formula.xxx_module_seche import XXXModuleSeche as XXXModule
else:
    from backend.formula.xxx_module import XXXModule
```

---

## 🎯 Formule Complète

### 🌧️ Saison des Pluies
```
Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]

où:
- P(t) = polynôme ordre 6 (153 jours)
- k(A) = Q̄_année / 739.0
- Cm = coefficient mensuel (juillet-novembre)
- ε = taux d'erreur (1-8%)
```

### 🌵 Saison Sèche
```
Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]

où:
- P(t) = polynôme ordre 6 (212 jours)
- k(A) = Q̄_année / 98.2
- Cm = coefficient mensuel (décembre-juin)
- ε = taux d'erreur (1-8%)
```

---

## ✅ CONCLUSION

**Toutes les formules sont correctement intégrées dans leur saison respective !**

- ✅ Polynômes différents et adaptés
- ✅ Coefficients mensuels spécifiques
- ✅ Durées correctes (153 vs 212 jours)
- ✅ Débits de référence adaptés
- ✅ Modules backend séparés
- ✅ Interface utilisateur avec choix de saison
- ✅ Import dynamique selon la saison sélectionnée

**Date de vérification:** 2026-04-20
