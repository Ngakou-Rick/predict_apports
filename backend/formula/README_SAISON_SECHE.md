# Module de Formule - SAISON SECHE

## Vue d'ensemble

Ce module implémente les formules de prédiction des débits pour la **SAISON SECHE** (1er Décembre → 30 Juin).

**Caractéristiques :**
- Durée : 212 jours
- Période : 1er décembre → 30 juin
- Données historiques : 2010-2025
- R² = 0.994
- RMSE = 6.0 m³/s

## Structure des modules

### 1. `formula_module_seche.py`
Module principal contenant la formule maîtresse.

**Formule :**
```
Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]
```

**Polynôme P(t) (ordre 6) :**
```
P(t) = −4.129×10⁻¹¹·t⁶ + 2.720×10⁻⁸·t⁵ − 5.603×10⁻⁶·t⁴ 
       + 3.519×10⁻⁴·t³ + 2.809×10⁻²·t² − 5.229·t + 250.7
```

**Coefficients mensuels Cm :**
- Décembre : 1.814 (décrue finale)
- Janvier : 0.8654 (baisse nette)
- Février : 0.4381 (étiage débutant)
- Mars : 0.3207 (étiage maximum - mois le plus sec)
- Avril : 0.3406 (début de remontée)
- Mai : 0.8628 (remontée rapide)
- Juin : 2.3255 (amorce saison pluies)

**Exemple d'utilisation :**
```python
from backend.formula import FormulaModuleSeche

formula = FormulaModuleSeche()

# Calculer pour le jour 45 (mi-janvier)
result = formula.calculate_Q(t=45, k_A=1.0, epsilon=0.08)

print(f"P(t) = {result['P_t']} m³/s")
print(f"Q central = {result['Q_central']} m³/s")
print(f"Q min = {result['Q_inf']} m³/s")
print(f"Q max = {result['Q_sup']} m³/s")
print(f"Mois = {result['month']}")
print(f"Cm = {result['Cm']}")
```

### 2. `coefficients_module_seche.py`
Gestion des coefficients annuels k(A) et mensuels Cm.

**Coefficients annuels k(A) - Classement humidité :**

| Rang | Saison | k(A) | Q moy | Statut | Emoji |
|------|--------|------|-------|--------|-------|
| 1 | 2018-2019 | 1.3921 | 125.6 | Très humide | 🌊🌊🌊 |
| 2 | 2013-2014 | 1.2694 | 117.2 | Très humide | 🌊🌊🌊 |
| 3 | 2020-2021 | 1.1837 | 91.0 | Humide | 🌊🌊 |
| ... | ... | ... | ... | ... | ... |
| 14 | 2012-2013 | 0.5763 | 58.9 | Très sec | ☀️☀️ |

**Exemple d'utilisation :**
```python
from backend.formula import CoefficientsModuleSeche

coeffs = CoefficientsModuleSeche()

# Obtenir le tableau des coefficients annuels
df_annual = coeffs.calculate_annual_coefficients()
print(df_annual)

# Obtenir le tableau des coefficients mensuels
df_monthly = coeffs.calculate_monthly_statistics()
print(df_monthly)

# Obtenir k(A) pour une année spécifique
k_A_2020 = coeffs.get_k_A(2020)
print(f"k(A) pour 2020 = {k_A_2020}")
```

### 3. `calculator_module_seche.py`
Calcul rapide pour un jour unique.

**Exemple d'utilisation :**
```python
from backend.formula import CalculatorModuleSeche

calculator = CalculatorModuleSeche()

# Calculer pour le jour 100 (début mars)
result = calculator.calculate_single_day(
    t=100,
    k_A=1.0,
    epsilon=0.05,
    year=2025
)

print(f"Jour : {result['t']}")
print(f"Date : {result['date']}")
print(f"Mois : {result['month']}")
print(f"Q central : {result['Q_central']} m³/s")

# Afficher les résultats formatés
print(calculator.format_results(result))
```

### 4. `generator_module_seche.py`
Génération de la table journalière complète (212 jours).

**Exemple d'utilisation :**
```python
from backend.formula import GeneratorModuleSeche

generator = GeneratorModuleSeche()

# Générer la table complète pour toute la saison
df_full = generator.generate_full_season(
    k_A=1.0,
    epsilon=0.08,
    year=2025
)

print(df_full.head())
print(f"Nombre de jours : {len(df_full)}")

# Générer un résumé mensuel
df_monthly = generator.generate_monthly_summary(
    k_A=1.0,
    epsilon=0.08,
    year=2025
)

print(df_monthly)

# Exporter vers Excel
filepath = generator.export_to_excel(
    k_A=1.0,
    epsilon=0.08,
    year=2025,
    filename="predictions_seche"
)

print(f"Fichier exporté : {filepath}")

# Obtenir les statistiques globales
stats = generator.get_statistics(k_A=1.0, epsilon=0.08)
print(f"Débit moyen : {stats['Q_mean']} m³/s")
print(f"Débit min : {stats['Q_min']} m³/s")
print(f"Débit max : {stats['Q_max']} m³/s")
```

### 5. `analyzer_module_seche.py`
Analyses avancées et statistiques.

**Exemple d'utilisation :**
```python
from backend.formula import AnalyzerModuleSeche

analyzer = AnalyzerModuleSeche()

# Analyser le comportement de mars (étiage)
mars_analysis = analyzer.analyze_month_behavior(
    month=3,
    k_A=1.0,
    epsilon=0.08
)

print(f"Mois : {mars_analysis['month_name']}")
print(f"Débit moyen : {mars_analysis['Q_mean']} m³/s")
print(f"Tendance : {mars_analysis['trend']}")

# Comparer plusieurs scénarios k(A)
df_comparison = analyzer.compare_scenarios(
    t=100,
    k_A_list=[0.6, 0.8, 1.0, 1.2, 1.4],
    epsilon=0.08
)

print(df_comparison)

# Identifier les périodes critiques (débit < 30 m³/s)
critical_periods = analyzer.identify_critical_periods(
    k_A=0.8,
    epsilon=0.08,
    threshold=30.0
)

for period in critical_periods:
    print(f"Période critique : jours {period['start_day']}-{period['end_day']}")
    print(f"Durée : {period['duration']} jours")
    print(f"Q min : {period['Q_min']} m³/s")

# Calculer la variabilité
variability = analyzer.calculate_variability(k_A=1.0, epsilon=0.08)
print(f"Coefficient de variation : {variability['coefficient_variation']}%")

# Trouver le jour d'étiage (débit minimum)
low_flow = analyzer.get_low_flow_day(k_A=1.0, epsilon=0.08)
print(f"Étiage au jour {low_flow['t']} ({low_flow['date']})")
print(f"Mois : {low_flow['month']}")
print(f"Q min : {low_flow['Q_min']} m³/s")

# Trouver le jour de débit maximum
peak_flow = analyzer.get_peak_flow_day(k_A=1.0, epsilon=0.08)
print(f"Débit max au jour {peak_flow['t']} ({peak_flow['date']})")
print(f"Q max : {peak_flow['Q_max']} m³/s")
```

## Différences avec la saison des pluies

| Caractéristique | Saison Pluies | Saison Sèche |
|----------------|---------------|--------------|
| Période | Juillet → Novembre | Décembre → Juin |
| Durée | 153 jours | 212 jours |
| Jours de saison | t ∈ [1, 153] | t ∈ [1, 212] |
| Mois | 7, 8, 9, 10, 11 | 12, 1, 2, 3, 4, 5, 6 |
| R² | 0.988 | 0.994 |
| Q historique | 739 m³/s | 98.2 m³/s |
| Mois critique | Octobre (max) | Mars (min - étiage) |

## Validation des entrées

**Règles de validation :**
- `t` : doit être entre 1 et 212
- `k(A)` : doit être > 0
- `ε` : doit être entre 0.01 et 0.08 (1% à 8%)

**Exemple :**
```python
from backend.formula import FormulaModuleSeche

formula = FormulaModuleSeche()

# Valider les entrées
is_valid, error_msg = formula.validate_inputs(t=100, k_A=1.0, epsilon=0.05)

if is_valid:
    result = formula.calculate_Q(t=100, k_A=1.0, epsilon=0.05)
else:
    print(f"Erreur : {error_msg}")
```

## Notes importantes

1. **Séparation complète** : Les modules de la saison sèche sont complètement indépendants de ceux de la saison des pluies.

2. **Pas de mélange** : Utilisez toujours les modules `*_seche.py` pour la saison sèche et les modules sans suffixe pour la saison des pluies.

3. **Étiage** : Mars est le mois le plus sec (Cm = 0.3207), période d'étiage maximum.

4. **Remontée** : Mai et juin montrent une forte remontée des débits (Cm = 0.8628 et 2.3255).

5. **Précision** : R² = 0.994 indique une excellente qualité d'ajustement du modèle.

## Exemples complets

### Exemple 1 : Prédiction pour une année normale
```python
from backend.formula import (
    FormulaModuleSeche,
    CalculatorModuleSeche,
    GeneratorModuleSeche
)

# Année normale : k(A) ≈ 1.0
calculator = CalculatorModuleSeche()

# Prédire le 15 mars (jour 105)
result = calculator.calculate_single_day(t=105, k_A=1.0, epsilon=0.08, year=2025)
print(calculator.format_results(result))

# Générer la table complète
generator = GeneratorModuleSeche()
df = generator.generate_full_season(k_A=1.0, epsilon=0.08, year=2025)
df.to_csv('predictions_seche_2025.csv', index=False)
```

### Exemple 2 : Analyse d'une année sèche
```python
from backend.formula import AnalyzerModuleSeche

analyzer = AnalyzerModuleSeche()

# Année très sèche : k(A) = 0.58
k_A_sec = 0.58

# Identifier les périodes critiques
critical = analyzer.identify_critical_periods(
    k_A=k_A_sec,
    epsilon=0.08,
    threshold=25.0
)

print(f"Nombre de périodes critiques : {len(critical)}")

# Analyser la variabilité
var = analyzer.calculate_variability(k_A=k_A_sec, epsilon=0.08)
print(f"Débit moyen : {var['Q_mean']} m³/s")
print(f"Étendue : {var['range']} m³/s")
```

### Exemple 3 : Comparaison saisons humides vs sèches
```python
from backend.formula import AnalyzerModuleSeche

analyzer = AnalyzerModuleSeche()

# Comparer différents scénarios pour le jour d'étiage (jour 110)
scenarios = analyzer.compare_scenarios(
    t=110,
    k_A_list=[0.58, 0.80, 1.0, 1.20, 1.39],
    epsilon=0.08
)

print(scenarios)
```
