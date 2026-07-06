# Modules Backend - Formule de Prédiction

Ce dossier contient tous les modules backend pour la formule de prédiction à 5 phases de la saison des pluies.

## Modules Implémentés

### 1. FormulaModule (`formula_module.py`)
Module de base pour le calcul de la formule maîtresse Q(t,A) = P(t) × k(A) × Cm × [1 ± ε].

**Fonctionnalités:**
- Calcul du polynôme P(t) d'ordre 6
- Calcul de Q(t,A) avec bornes Q_inf et Q_sup
- Déduction automatique du mois à partir du jour de saison
- Validation des paramètres d'entrée

**Exemple d'utilisation:**
```python
from backend.formula import FormulaModule

formula = FormulaModule()
result = formula.calculate_Q(t=50, k_A=1.05, epsilon=0.08)
print(f"Q centrale: {result['Q_central']} m³/s")
```

### 2. CoefficientsModule (`coefficients_module.py`)
Gestion des coefficients annuels k(A) et mensuels Cm.

**Fonctionnalités:**
- Calcul de k(A) pour chaque année (2011-2024)
- Génération du Tableau A (coefficients annuels)
- Génération du Tableau B (statistiques mensuelles)
- Génération du Tableau C (coefficients du polynôme)

**Exemple d'utilisation:**
```python
from backend.formula import CoefficientsModule

coeffs = CoefficientsModule()
tableau_a = coeffs.calculate_annual_coefficients()
k_A_2020 = coeffs.get_k_A(2020)
```

### 3. CalculatorModule (`calculator_module.py`)
Calculateur pour un jour unique avec formatage des résultats.

**Fonctionnalités:**
- Calcul rapide pour un jour spécifique
- Déduction automatique du mois et Cm
- Formatage des résultats pour affichage

**Exemple d'utilisation:**
```python
from backend.formula import CalculatorModule

calc = CalculatorModule()
result = calc.calculate_single_day(t=50, k_A=1.05, epsilon=0.08, year=2024)
formatted = calc.format_results(result)
print(formatted)
```

### 4. GeneratorModule (`generator_module.py`)
Génération du tableau complet de 153 jours avec calculs vectorisés.

**Fonctionnalités:**
- Génération de 153 prédictions journalières
- Calcul des dates (1er juillet → 30 novembre)
- Attribution des statuts (🚨, 🔔, ✅, 🌤️, ℹ️)
- Mise à jour des débits réels et calcul des écarts

**Exemple d'utilisation:**
```python
from backend.formula import GeneratorModule

gen = GeneratorModule()
df = gen.generate_full_table(k_A=1.05, epsilon=0.08, year=2024)
print(f"Tableau de {len(df)} jours généré")
```

### 5. AnalyzerModule (`analyzer_module.py`)
Analyse comparative annuelle et mensuelle.

**Fonctionnalités:**
- Classement annuel par k(A)
- Classement mensuel par Q moyen
- Qualifications (Très humide, Humide, Normal, Sec, Très sec)
- Calcul du coefficient de variation (CV)
- Résumé comparatif

**Exemple d'utilisation:**
```python
from backend.formula import AnalyzerModule

analyzer = AnalyzerModule()
annual_ranking = analyzer.generate_annual_ranking()
monthly_ranking = analyzer.generate_monthly_ranking()
summary = analyzer.generate_comparison_summary()
```

### 6. CacheManager (`cache_manager.py`)
Gestionnaire de cache avec TTL pour optimiser les performances.

**Fonctionnalités:**
- Stockage avec Time To Live (TTL)
- Invalidation automatique des entrées expirées
- Statistiques du cache
- Nettoyage des entrées expirées

**Exemple d'utilisation:**
```python
from backend.formula import CacheManager

cache = CacheManager()
cache.set('coefficients_2024', data, ttl=3600)
data = cache.get('coefficients_2024')
```

### 7. ExportManager (`export_manager.py`)
Export des résultats en Excel et PDF.

**Fonctionnalités:**
- Export Excel avec formatage
- Export PDF avec graphiques
- Création de graphiques matplotlib
- Export des tableaux de coefficients

**Exemple d'utilisation:**
```python
from backend.formula import ExportManager

export_mgr = ExportManager()
excel_path = export_mgr.export_to_excel(df, 'predictions.xlsx', metadata)
chart_path = export_mgr.create_prediction_chart(df, metadata)
```

### 8. Exceptions (`exceptions.py`)
Hiérarchie d'exceptions personnalisées.

**Exceptions disponibles:**
- `FormulaError`: Exception de base
- `InvalidDayError`: Jour de saison invalide
- `InvalidCoefficientError`: Coefficient k(A) invalide
- `InvalidEpsilonError`: Taux d'erreur invalide
- `MissingDataError`: Données historiques manquantes
- `ExportError`: Erreur lors de l'export
- `ValidationError`: Erreur de validation générique
- `CalculationError`: Erreur lors d'un calcul

**Exemple d'utilisation:**
```python
from backend.formula import InvalidDayError

try:
    result = formula.calculate_Q(t=200, k_A=1.0, epsilon=0.08)
except InvalidDayError as e:
    print(f"Erreur: {e}")
```

## Tests

Un script de test complet est disponible: `test_modules_backend.py`

Pour exécuter les tests:
```bash
python test_modules_backend.py
```

## Dépendances

- `pandas`: Manipulation de données
- `numpy`: Calculs vectorisés
- `matplotlib`: Génération de graphiques
- `openpyxl`: Export Excel (optionnel)

## Performance

Les modules sont optimisés pour:
- Calcul P(t): < 10ms
- Génération 153 jours: < 500ms
- Export Excel: < 3s
- Export PDF: < 5s

## Architecture

```
backend/formula/
├── formula_module.py       # Module de base (formule maîtresse)
├── coefficients_module.py  # Gestion des coefficients
├── calculator_module.py    # Calculateur jour unique
├── generator_module.py     # Génération tableau 153 jours
├── analyzer_module.py      # Analyse comparative
├── cache_manager.py        # Gestionnaire de cache
├── export_manager.py       # Export Excel/PDF
├── exceptions.py           # Exceptions personnalisées
├── __init__.py            # Exports publics
└── README.md              # Cette documentation
```

## Intégration UI

Ces modules sont conçus pour être intégrés dans l'interface PyQt5 existante (`phase2_prediction.py`) via un dialogue de sélection des 5 phases.

## Auteur

Implémenté selon les spécifications du document de conception `rainy-season-prediction-formula`.
