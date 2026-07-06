# Implementation Tasks

## Phase 1: Préparation et Nettoyage

### Task 1: Supprimer le Cache et Fichiers Obsolètes

**Description**: Supprimer le système de cache existant et nettoyer les fichiers Python compilés pour garantir la fraîcheur des fonctionnalités.

**Sub-tasks**:
- [ ] 1.1 Supprimer `backend/formula/cache_manager.py` si existe
- [ ] 1.2 Supprimer tous les dossiers `__pycache__` dans `backend/formula/`
- [ ] 1.3 Retirer toutes les références à `CacheManager` dans les modules existants
- [ ] 1.4 Vérifier qu'aucun import de `cache_manager` ne reste dans le code

**Acceptance Criteria**:
- Aucun fichier `cache_manager.py` n'existe
- Aucun dossier `__pycache__` dans `backend/formula/`
- Aucune référence à `CacheManager` dans le code
- Les tests existants passent toujours

---

## Phase 2: Création des Modules de Validation et Extraction

### Task 2: Créer DataQualityValidator

**Description**: Créer le module de validation de la qualité des données historiques.

**Sub-tasks**:
- [ ] 2.1 Créer `backend/formula/data_quality_validator.py`
- [ ] 2.2 Implémenter `__init__(self, data: pd.DataFrame)`
- [ ] 2.3 Implémenter `validate_years_count()` (minimum 10 ans)
- [ ] 2.4 Implémenter `validate_missing_values()` (maximum 15%)
- [ ] 2.5 Implémenter `validate_polynomial_fit(r_squared)` (minimum 0.90)
- [ ] 2.6 Implémenter `calculate_quality_score()` (0-100)
- [ ] 2.7 Implémenter `get_validation_report()`
- [ ] 2.8 Ajouter les constantes de classe (MIN_YEARS=10, MAX_MISSING_PERCENTAGE=15.0, MIN_R_SQUARED=0.90)

**Acceptance Criteria**:
- Le module existe et est importable
- Toutes les méthodes sont implémentées
- Le score de qualité est toujours entre 0 et 100
- Les validations retournent (bool, str) comme spécifié
- Le rapport contient toutes les clés requises

**Property Tests**: Property 1, Property 2

---

### Task 3: Créer CoefficientExtractor

**Description**: Créer le module d'extraction des coefficients à partir des données historiques.

**Sub-tasks**:
- [ ] 3.1 Créer `backend/formula/coefficient_extractor.py`
- [ ] 3.2 Implémenter `__init__(self, season_type: str, data: pd.DataFrame)`
- [ ] 3.3 Implémenter `validate_data_quality()` en utilisant DataQualityValidator
- [ ] 3.4 Implémenter `extract_polynomial_coefficients()` avec numpy.polyfit ordre 6
- [ ] 3.5 Implémenter `extract_monthly_coefficients()` avec normalisation
- [ ] 3.6 Implémenter `extract_Q_historical()` (moyenne globale)
- [ ] 3.7 Implémenter `extract_annual_coefficients()` (k(A) par année)
- [ ] 3.8 Implémenter `extract_all()` qui orchestre toutes les extractions
- [ ] 3.9 Gérer les deux saisons (rainy: 153 jours, dry: 212 jours)
- [ ] 3.10 Gérer les mois fixes (rainy: 7-11, dry: 12,1-6)

**Acceptance Criteria**:
- Le module existe et est importable
- L'extraction polynomiale retourne 7 coefficients + R²
- L'extraction mensuelle retourne le bon nombre de mois par saison
- Q_historical est la moyenne exacte des débits
- k(A) = Q_année / Q_historical pour chaque année
- extract_all() retourne un dictionnaire complet

**Property Tests**: Property 4, Property 5, Property 6, Property 7, Property 8

---

## Phase 3: Modification des Modules de Formules Existants

### Task 4: Modifier FormulaModule (Saison Pluies)

**Description**: Rendre FormulaModule capable d'accepter des coefficients dynamiques tout en préservant les coefficients Mbakaou par défaut.

**Sub-tasks**:
- [ ] 4.1 Renommer les constantes actuelles en `DEFAULT_POLY_COEFFS`, `DEFAULT_MONTHLY_COEFFS`, `DEFAULT_Q_HISTORICAL`
- [ ] 4.2 Modifier `__init__` pour accepter `poly_coeffs`, `monthly_coeffs`, `Q_historical` optionnels
- [ ] 4.3 Ajouter l'attribut `self.using_defaults` pour tracer la source
- [ ] 4.4 Implémenter `get_coefficients_source()` retournant 'Mbakaou (défaut)' ou 'Extraits des données'
- [ ] 4.5 Préserver toutes les méthodes existantes (`calculate_P`, `deduce_month`, `calculate_Q`, `validate_inputs`)
- [ ] 4.6 Préserver l'ajustement juillet (TARGET_DAILY_DIFF_JULY = 16.5)
- [ ] 4.7 Vérifier que les coefficients par défaut sont identiques aux valeurs actuelles

**Acceptance Criteria**:
- FormulaModule() sans arguments utilise coefficients Mbakaou
- FormulaModule(poly_coeffs=...) utilise coefficients fournis
- get_coefficients_source() retourne la bonne source
- Tous les tests existants passent
- La formule Q(t,A) = P(t) × k(A) × Cm × [1 ± ε] est préservée
- Les bornes -8%/+19% sont préservées

**Property Tests**: Property 12, Property 13

---

### Task 5: Modifier FormulaModuleSeche (Saison Sèche)

**Description**: Appliquer les mêmes modifications que Task 4 pour la saison sèche.

**Sub-tasks**:
- [ ] 5.1 Renommer les constantes actuelles en `DEFAULT_POLY_COEFFS`, `DEFAULT_MONTHLY_COEFFS`, `DEFAULT_Q_HISTORICAL`
- [ ] 5.2 Modifier `__init__` pour accepter coefficients optionnels
- [ ] 5.3 Ajouter `self.using_defaults` et `get_coefficients_source()`
- [ ] 5.4 Préserver toutes les méthodes existantes
- [ ] 5.5 Vérifier que les coefficients par défaut sont identiques aux valeurs actuelles
- [ ] 5.6 Préserver les bornes ±8% pour la saison sèche

**Acceptance Criteria**:
- FormulaModuleSeche() sans arguments utilise coefficients Mbakaou
- FormulaModuleSeche(poly_coeffs=...) utilise coefficients fournis
- get_coefficients_source() retourne la bonne source
- Tous les tests existants passent
- Les bornes ±8% sont préservées

**Property Tests**: Property 11, Property 12, Property 13

---

### Task 6: Modifier CoefficientsModule

**Description**: Rendre CoefficientsModule capable d'accepter des coefficients extraits.

**Sub-tasks**:
- [ ] 6.1 Modifier `__init__` pour accepter `Q_historical`, `monthly_coeffs`, `annual_coeffs` optionnels
- [ ] 6.2 Utiliser les valeurs fournies ou les valeurs par défaut Mbakaou
- [ ] 6.3 Préserver toutes les méthodes existantes (`calculate_annual_coefficients`, `calculate_monthly_statistics`, etc.)
- [ ] 6.4 Vérifier que le comportement par défaut est identique à l'actuel

**Acceptance Criteria**:
- CoefficientsModule() sans arguments utilise coefficients Mbakaou
- CoefficientsModule(Q_historical=...) utilise la valeur fournie
- Tous les tests existants passent
- Les calculs de k(A) utilisent le Q_historical fourni

**Property Tests**: Property 8, Property 9, Property 10

---

### Task 7: Modifier CoefficientsModuleSeche

**Description**: Créer ou modifier le module de coefficients pour la saison sèche.

**Sub-tasks**:
- [ ] 7.1 Vérifier si `backend/formula/coefficients_module_seche.py` existe
- [ ] 7.2 Si non, créer le module en miroir de CoefficientsModule
- [ ] 7.3 Si oui, appliquer les mêmes modifications que Task 6
- [ ] 7.4 Utiliser les valeurs par défaut de la saison sèche (Q_HISTORICAL = 98.2)

**Acceptance Criteria**:
- Le module existe et fonctionne pour la saison sèche
- Accepte des coefficients optionnels
- Utilise les bonnes valeurs par défaut (98.2 m³/s)

---

### Task 8: Modifier CalculatorModule et CalculatorModuleSeche

**Description**: Mettre à jour les modules de calcul pour utiliser les FormulaModule modifiés.

**Sub-tasks**:
- [ ] 8.1 Modifier `CalculatorModule.__init__` pour accepter un `formula_module` optionnel
- [ ] 8.2 Modifier `CalculatorModuleSeche.__init__` pour accepter un `formula_module` optionnel
- [ ] 8.3 Préserver toutes les méthodes existantes
- [ ] 8.4 Vérifier que le comportement par défaut est inchangé

**Acceptance Criteria**:
- Les modules acceptent des FormulaModule personnalisés
- Le comportement par défaut utilise FormulaModule() sans arguments
- Tous les tests existants passent

---

### Task 9: Modifier GeneratorModule et GeneratorModuleSeche

**Description**: Mettre à jour les modules de génération pour utiliser les FormulaModule modifiés.

**Sub-tasks**:
- [ ] 9.1 Modifier `GeneratorModule.__init__` pour accepter un `formula_module` optionnel
- [ ] 9.2 Modifier `GeneratorModuleSeche.__init__` pour accepter un `formula_module` optionnel (si existe)
- [ ] 9.3 Préserver toutes les méthodes existantes
- [ ] 9.4 Vérifier que le comportement par défaut est inchangé

**Acceptance Criteria**:
- Les modules acceptent des FormulaModule personnalisés
- Le comportement par défaut utilise FormulaModule() sans arguments
- Tous les tests existants passent

---

## Phase 4: Intégration avec ApplicationController

### Task 10: Ajouter l'Extraction au Chargement des Données

**Description**: Intégrer l'extraction automatique des coefficients lors du chargement des données dans ApplicationController.

**Sub-tasks**:
- [ ] 10.1 Ajouter des attributs pour stocker les coefficients extraits (`self.rainy_coefficients`, `self.dry_coefficients`)
- [ ] 10.2 Modifier `load_and_transform_data()` pour appeler CoefficientExtractor après séparation des saisons
- [ ] 10.3 Extraire les coefficients pour la saison des pluies
- [ ] 10.4 Extraire les coefficients pour la saison sèche
- [ ] 10.5 Valider la qualité des données et afficher les avertissements si nécessaire
- [ ] 10.6 Stocker les coefficients extraits dans le contrôleur
- [ ] 10.7 Gérer le fallback vers Mbakaou si la qualité est insuffisante
- [ ] 10.8 Retourner les informations d'extraction dans le résultat

**Acceptance Criteria**:
- Les coefficients sont extraits automatiquement au chargement
- Les avertissements de qualité sont affichés si nécessaire
- Le fallback vers Mbakaou fonctionne
- Les coefficients sont accessibles pour les prédictions

**Property Tests**: Property 2, Property 3

---

### Task 11: Créer des Méthodes pour Obtenir les Modules de Formules

**Description**: Ajouter des méthodes dans ApplicationController pour obtenir les modules de formules avec les bons coefficients.

**Sub-tasks**:
- [ ] 11.1 Créer `get_formula_module_rainy()` qui retourne FormulaModule avec coefficients extraits ou par défaut
- [ ] 11.2 Créer `get_formula_module_dry()` qui retourne FormulaModuleSeche avec coefficients extraits ou par défaut
- [ ] 11.3 Créer `get_coefficients_module_rainy()` qui retourne CoefficientsModule avec coefficients extraits
- [ ] 11.4 Créer `get_coefficients_module_dry()` qui retourne CoefficientsModuleSeche avec coefficients extraits
- [ ] 11.5 Gérer le cas où aucune donnée n'est chargée (retourner modules par défaut)

**Acceptance Criteria**:
- Les méthodes retournent les bons modules avec les bons coefficients
- Sans données chargées, les modules par défaut sont retournés
- Les coefficients extraits sont utilisés quand disponibles

**Property Tests**: Property 3, Property 10

---

## Phase 5: Interface Utilisateur

### Task 12: Afficher les Coefficients Extraits dans l'UI

**Description**: Ajouter l'affichage des coefficients extraits dans l'interface utilisateur.

**Sub-tasks**:
- [ ] 12.1 Ajouter une section "Coefficients Utilisés" dans les onglets de prédiction par formules
- [ ] 12.2 Afficher la source des coefficients (Mbakaou ou Extraits)
- [ ] 12.3 Afficher le tableau des coefficients polynomiaux avec R²
- [ ] 12.4 Afficher le tableau des coefficients mensuels Cm
- [ ] 12.5 Afficher Q_historical avec comparaison Mbakaou vs Extrait
- [ ] 12.6 Afficher le score de qualité des données
- [ ] 12.7 Afficher les avertissements de qualité si présents

**Acceptance Criteria**:
- Les coefficients sont visibles dans l'UI
- La source est clairement indiquée
- Les avertissements sont affichés en rouge/orange
- Le score de qualité est affiché avec une barre de progression

---

### Task 13: Ajouter un Bouton de Rafraîchissement

**Description**: Ajouter un bouton pour re-extraire les coefficients manuellement.

**Sub-tasks**:
- [ ] 13.1 Ajouter un bouton "🔄 Rafraîchir Coefficients" dans les onglets de formules
- [ ] 13.2 Connecter le bouton à une méthode qui re-déclenche l'extraction
- [ ] 13.3 Afficher un message de confirmation après rafraîchissement
- [ ] 13.4 Mettre à jour l'affichage des coefficients après rafraîchissement

**Acceptance Criteria**:
- Le bouton est visible et cliquable
- Les coefficients sont re-extraits au clic
- L'affichage est mis à jour automatiquement
- Un message de confirmation est affiché

---

### Task 14: Modifier les Méthodes de Prédiction par Formules

**Description**: Mettre à jour les méthodes de prédiction dans l'UI pour utiliser les coefficients extraits.

**Sub-tasks**:
- [ ] 14.1 Modifier `calculate_single_day_formula('rainy')` pour utiliser `get_formula_module_rainy()`
- [ ] 14.2 Modifier `calculate_single_day_formula('dry')` pour utiliser `get_formula_module_dry()`
- [ ] 14.3 Modifier `generate_full_season_formula('rainy')` pour utiliser `get_formula_module_rainy()`
- [ ] 14.4 Modifier `generate_full_season_formula('dry')` pour utiliser `get_formula_module_dry()`
- [ ] 14.5 Afficher la source des coefficients dans les résultats

**Acceptance Criteria**:
- Les prédictions utilisent les coefficients extraits quand disponibles
- Les prédictions utilisent Mbakaou par défaut sans données
- La source est indiquée dans les résultats
- Tous les calculs sont corrects

**Property Tests**: Property 12, Property 14

---

## Phase 6: Tests

### Task 15: Créer les Tests de Propriétés

**Description**: Implémenter tous les tests de propriétés définis dans le design.

**Sub-tasks**:
- [ ] 15.1 Installer hypothesis (`pip install hypothesis`)
- [ ] 15.2 Créer `tests/test_properties_coefficient_extraction.py`
- [ ] 15.3 Implémenter test_property_1_data_quality_validation
- [ ] 15.4 Implémenter test_property_2_conditional_warnings
- [ ] 15.5 Implémenter test_property_3_mbakaou_fallback
- [ ] 15.6 Implémenter test_property_4_polynomial_structure
- [ ] 15.7 Implémenter test_property_5_monthly_structure
- [ ] 15.8 Implémenter test_property_6_monthly_normalization
- [ ] 15.9 Implémenter test_property_7_Q_historical_calculation
- [ ] 15.10 Implémenter test_property_8_k_A_formula
- [ ] 15.11 Implémenter test_property_9_humidity_ranking
- [ ] 15.12 Implémenter test_property_10_coefficient_persistence
- [ ] 15.13 Implémenter test_property_11_season_separation
- [ ] 15.14 Implémenter test_property_12_formula_preservation
- [ ] 15.15 Implémenter test_property_13_validation_preservation
- [ ] 15.16 Implémenter test_property_14_fixed_season_durations
- [ ] 15.17 Implémenter test_property_15_descriptive_error_messages
- [ ] 15.18 Configurer hypothesis pour minimum 100 itérations par test
- [ ] 15.19 Ajouter les tags de feature et property dans chaque test

**Acceptance Criteria**:
- Tous les 15 tests de propriétés sont implémentés
- Chaque test a le tag approprié
- Tous les tests passent avec 100+ itérations
- La couverture des propriétés est de 100%

---

### Task 16: Créer les Tests Unitaires

**Description**: Créer les tests unitaires pour les nouveaux modules et les intégrations.

**Sub-tasks**:
- [ ] 16.1 Créer `tests/test_data_quality_validator.py`
- [ ] 16.2 Créer `tests/test_coefficient_extractor.py`
- [ ] 16.3 Créer `tests/test_formula_module_dynamic.py`
- [ ] 16.4 Créer `tests/test_integration_extraction.py`
- [ ] 16.5 Tester tous les cas d'erreur (données insuffisantes, R² faible, etc.)
- [ ] 16.6 Tester le fallback vers Mbakaou
- [ ] 16.7 Tester l'affichage UI des coefficients

**Acceptance Criteria**:
- Couverture de code >= 90% pour les nouveaux modules
- Tous les cas d'erreur sont testés
- Les tests d'intégration passent
- Les tests UI passent

---

### Task 17: Tests de Régression

**Description**: Vérifier que tous les tests existants passent toujours.

**Sub-tasks**:
- [ ] 17.1 Exécuter tous les tests existants de FormulaModule
- [ ] 17.2 Exécuter tous les tests existants de FormulaModuleSeche
- [ ] 17.3 Exécuter tous les tests existants de CoefficientsModule
- [ ] 17.4 Exécuter tous les tests existants de l'UI
- [ ] 17.5 Vérifier que les modules ML/Analyse/Climat sont inchangés
- [ ] 17.6 Corriger tout test cassé

**Acceptance Criteria**:
- 100% des tests existants passent
- Aucune régression détectée
- Les modules non-concernés sont inchangés

---

## Phase 7: Documentation et Finalisation

### Task 18: Mettre à Jour la Documentation

**Description**: Mettre à jour la documentation pour refléter les nouvelles fonctionnalités.

**Sub-tasks**:
- [ ] 18.1 Mettre à jour `backend/formula/README.md` avec l'extraction de coefficients
- [ ] 18.2 Mettre à jour `backend/formula/README_SAISON_SECHE.md` avec l'extraction
- [ ] 18.3 Créer `docs/EXTRACTION_COEFFICIENTS_GUIDE.md` avec guide utilisateur
- [ ] 18.4 Ajouter des exemples d'utilisation avec différentes zones géographiques
- [ ] 18.5 Documenter les seuils de qualité et les avertissements
- [ ] 18.6 Documenter le fallback vers Mbakaou

**Acceptance Criteria**:
- Toute la documentation est à jour
- Le guide utilisateur est complet et clair
- Des exemples sont fournis
- Les seuils et avertissements sont documentés

---

### Task 19: Nettoyage Final et Vérifications

**Description**: Effectuer un nettoyage final et vérifier que tout fonctionne.

**Sub-tasks**:
- [ ] 19.1 Supprimer tous les fichiers `__pycache__` restants
- [ ] 19.2 Supprimer tous les fichiers `.pyc` restants
- [ ] 19.3 Vérifier qu'aucune référence à `cache_manager` ne reste
- [ ] 19.4 Vérifier que les imports sont corrects dans tous les fichiers
- [ ] 19.5 Exécuter un linter (pylint ou flake8) sur les nouveaux fichiers
- [ ] 19.6 Vérifier que les constantes Mbakaou sont préservées
- [ ] 19.7 Tester l'application de bout en bout avec un dataset Mbakaou
- [ ] 19.8 Tester l'application de bout en bout avec un dataset d'une autre zone
- [ ] 19.9 Tester l'application sans données chargées

**Acceptance Criteria**:
- Aucun fichier cache ne reste
- Le linter ne rapporte aucune erreur critique
- Les tests de bout en bout passent
- L'application fonctionne avec Mbakaou, une autre zone, et sans données

---

## Phase 8: Export et Visualisation (Optionnel)

### Task 20*: Ajouter l'Export des Coefficients Extraits

**Description**: Permettre l'export des coefficients extraits vers Excel.

**Sub-tasks**:
- [ ] 20.1 Ajouter un bouton "💾 Exporter Coefficients" dans l'UI
- [ ] 20.2 Créer une méthode pour formater les coefficients en DataFrame
- [ ] 20.3 Exporter vers Excel avec plusieurs feuilles (Polynôme, Mensuels, Annuels, Qualité)
- [ ] 20.4 Inclure les métadonnées (date d'extraction, source de données, score qualité)

**Acceptance Criteria**:
- Le bouton d'export est visible
- L'export génère un fichier Excel valide
- Toutes les informations sont présentes
- Le fichier est bien formaté

---

### Task 21*: Ajouter des Graphiques de Comparaison

**Description**: Visualiser la comparaison entre coefficients Mbakaou et extraits.

**Sub-tasks**:
- [ ] 21.1 Créer un graphique comparant les polynômes P(t) Mbakaou vs Extrait
- [ ] 21.2 Créer un graphique comparant les Cm Mbakaou vs Extrait
- [ ] 21.3 Afficher les graphiques dans l'UI
- [ ] 21.4 Permettre l'export des graphiques en PNG

**Acceptance Criteria**:
- Les graphiques sont visibles dans l'UI
- La comparaison est claire et lisible
- Les graphiques peuvent être exportés

---

## Notes d'Implémentation

### Ordre d'Exécution Recommandé

1. **Phase 1** (Nettoyage) - Critique pour éviter les conflits
2. **Phase 2** (Nouveaux modules) - Base de la fonctionnalité
3. **Phase 3** (Modifications modules existants) - Intégration
4. **Phase 4** (ApplicationController) - Orchestration
5. **Phase 5** (UI) - Interface utilisateur
6. **Phase 6** (Tests) - Validation
7. **Phase 7** (Documentation) - Finalisation
8. **Phase 8** (Optionnel) - Améliorations

### Dépendances entre Tâches

- Task 2 doit être complétée avant Task 3
- Task 3 doit être complétée avant Task 10
- Tasks 4-9 peuvent être faites en parallèle
- Task 10 doit être complétée avant Task 11
- Task 11 doit être complétée avant Task 14
- Tasks 12-14 peuvent être faites en parallèle
- Task 15-17 doivent être faites après toutes les implémentations
- Task 18-19 sont les dernières

### Estimation de Temps

- Phase 1: 1-2 heures
- Phase 2: 8-12 heures
- Phase 3: 6-8 heures
- Phase 4: 4-6 heures
- Phase 5: 6-8 heures
- Phase 6: 12-16 heures
- Phase 7: 4-6 heures
- Phase 8: 4-6 heures (optionnel)

**Total estimé**: 45-64 heures (sans Phase 8)

### Priorités

**Critique** (Must Have):
- Tasks 1-14, 17, 19

**Important** (Should Have):
- Tasks 15-16, 18

**Optionnel** (Nice to Have):
- Tasks 20-21
