# Plan d'Implémentation - Formule de Prédiction à 5 Phases pour la Saison des Pluies

## Vue d'ensemble

Ce plan d'implémentation transforme la conception en tâches concrètes de développement. L'approche suit une stratégie incrémentale: construire les modules de base (formule, coefficients), ajouter les calculateurs et générateurs, intégrer dans l'UI PyQt5 existante, puis finaliser avec les exports et tests d'intégration.

**Architecture:** 5 modules backend + cache + export + intégration UI dans phase2_prediction.py

**Langage:** Python avec PyQt5, pandas, numpy, openpyxl, matplotlib

**Stratégie de test:** Property-based testing (hypothesis) pour les 25 propriétés de correction + tests unitaires pour cas spécifiques

## Tâches

- [x] 1. Créer la structure de base et le module FormulaModule
  - Créer le fichier `backend/formula/formula_module.py`
  - Implémenter la classe `FormulaModule` avec les constantes (POLY_COEFFS, MONTHLY_COEFFS, Q_HISTORICAL)
  - Implémenter `calculate_P(t)` pour calculer le polynôme d'ordre 6
  - Implémenter `deduce_month(t)` pour déduire le mois (1-31→7, 32-62→8, etc.)
  - Implémenter `calculate_Q(t, k_A, epsilon)` pour la formule maîtresse
  - Implémenter `validate_inputs(t, k_A, epsilon)` pour validation des paramètres
  - _Exigences: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_

- [ ]* 1.1 Écrire les tests property-based pour FormulaModule (Propriétés 1-7)
  - Créer `tests/property/test_properties_formula.py`
  - **Propriété 1: Idempotence du calcul** - Calculer Q(t,A) deux fois doit produire résultats identiques
  - **Valide: Exigences 1.10, 3.10**
  - **Propriété 2: Déduction correcte du mois** - Pour tout t ∈ [1,153], déduire le bon mois
  - **Valide: Exigences 1.8, 3.2, 4.4**
  - **Propriété 3: Application du coefficient mensuel** - Appliquer le bon Cm selon le mois déduit
  - **Valide: Exigences 1.9, 3.3**
  - **Propriété 4: Précision du polynôme** - P(t) doit égaler la formule exacte
  - **Valide: Exigences 1.1**
  - **Propriété 5: Correction de la formule maîtresse** - Q(t,A) = P(t) × k(A) × Cm × [1 ± ε]
  - **Valide: Exigences 1.3**
  - **Propriété 6: Calcul de la borne inférieure** - Q_inf = P(t) × k(A) × Cm × 0.92
  - **Valide: Exigences 1.4**
  - **Propriété 7: Calcul de la borne supérieure** - Q_sup = P(t) × k(A) × Cm × 1.08
  - **Valide: Exigences 1.5**
  - Configurer hypothesis avec minimum 100 itérations par test

- [ ]* 1.2 Écrire les tests property-based pour validation (Propriétés 8-10)
  - Créer `tests/property/test_properties_validation.py`
  - **Propriété 8: Validation du jour** - Rejeter t < 1 ou t > 153 avec message d'erreur
  - **Valide: Exigences 1.6, 3.5, 7.1**
  - **Propriété 9: Validation du coefficient annuel** - Rejeter k(A) ≤ 0 avec message d'erreur
  - **Valide: Exigences 1.6, 3.6, 7.2**
  - **Propriété 10: Validation d'epsilon** - Rejeter ε < 0.01 ou ε > 0.08 avec message d'erreur
  - **Valide: Exigences 1.7, 3.7, 7.3**

- [ ]* 1.3 Écrire les tests unitaires pour FormulaModule
  - Tester P(t) avec valeurs connues (t=1, t=77, t=153)
  - Tester déduction du mois aux frontières (t=31, t=32, t=62, t=63, etc.)
  - Tester calcul Q avec k(A)=1.0 et ε=0.05
  - Tester formatage avec 2 décimales
  - _Exigences: 1.1, 1.2, 1.8_

- [x] 2. Implémenter le module CoefficientsModule
  - Créer le fichier `backend/formula/coefficients_module.py`
  - Implémenter la classe `CoefficientsModule` avec initialisation des données historiques
  - Implémenter `calculate_annual_coefficients()` pour calculer k(A) = Q̄_année / 739
  - Implémenter `calculate_monthly_statistics()` pour statistiques mensuelles
  - Implémenter `get_polynomial_table()` pour tableau des coefficients du polynôme
  - Implémenter `get_k_A(year)` pour récupérer k(A) d'une année
  - Calculer humidité relative, rangs, statuts pour chaque année
  - _Exigences: 2.1, 2.2, 2.3, 2.4, 2.5, 2.7, 2.8_

- [ ]* 2.1 Écrire les tests property-based pour CoefficientsModule (Propriétés 11-15)
  - Créer `tests/property/test_properties_formatting.py`
  - **Propriété 11: Formatage de précision** - P(t) formaté avec exactement 2 décimales
  - **Valide: Exigences 1.2, 3.9**
  - **Propriété 12: Calcul du coefficient annuel** - k(A) = Q̄_année / 739
  - **Valide: Exigences 2.4**
  - **Propriété 13: Formatage des coefficients** - Coefficients avec au moins 3 décimales
  - **Valide: Exigences 2.7**
  - **Propriété 14: Complétude du tableau** - Tableau A contient toutes les années sans omission
  - **Valide: Exigences 2.10**
  - **Propriété 15: Attribution des qualifications** - Assigner correcte qualification selon k(A)
  - **Valide: Exigences 5.4, 5.5, 5.6, 5.7, 5.8**

- [ ]* 2.2 Écrire les tests unitaires pour CoefficientsModule
  - Tester calcul k(A) avec données connues (2011-2024)
  - Tester tri du Tableau A par rang d'humidité
  - Vérifier R²=0.988 dans Tableau C
  - Vérifier coefficients mensuels constants (Juillet=0.697, etc.)
  - Tester structure des tableaux (colonnes correctes)
  - _Exigences: 2.1, 2.2, 2.3, 2.5, 2.9_

- [x] 3. Implémenter le module CalculatorModule
  - Créer le fichier `backend/formula/calculator_module.py`
  - Implémenter la classe `CalculatorModule` avec référence à FormulaModule
  - Implémenter `calculate_single_day(t, k_A, epsilon)` pour calcul d'un jour unique
  - Implémenter `format_results(results)` pour formatage de l'affichage
  - Calculer automatiquement date, mois, Cm à partir de t
  - Retourner dict avec t, date, month, P_t, Q_central, Q_min, Q_max, Cm
  - _Exigences: 3.1, 3.2, 3.3, 3.4, 3.8, 3.9_

- [ ]* 3.1 Écrire les tests unitaires pour CalculatorModule
  - Tester calcul pour t=1 (1er juillet)
  - Tester calcul pour t=153 (30 novembre)
  - Tester calcul pour t=77 (milieu de saison)
  - Vérifier temps de calcul < 100ms
  - Vérifier formatage des résultats
  - _Exigences: 3.1, 3.4, 3.8, 3.9_

- [ ] 4. Checkpoint - Vérifier les modules de base
  - Exécuter tous les tests unitaires et property-based
  - Vérifier que tous les tests passent
  - Demander à l'utilisateur si des questions se posent

- [x] 5. Implémenter le module GeneratorModule
  - Créer le fichier `backend/formula/generator_module.py`
  - Implémenter la classe `GeneratorModule` avec référence à FormulaModule
  - Implémenter `generate_full_table(k_A, epsilon, year)` pour générer 153 lignes
  - Implémenter `assign_status(Q_central)` pour assigner statuts (🚨, 🔔, ✅, 🌤️, ℹ️)
  - Implémenter `calculate_dates(year)` pour calculer dates du 1er juillet au 30 novembre
  - Utiliser calculs vectorisés avec numpy pour performance
  - Retourner DataFrame avec colonnes: t, Date, Mois, P(t), Q centrale, Q min, Q max, Q réelle, Écart %, Statut
  - _Exigences: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

- [ ]* 5.1 Écrire les tests property-based pour GeneratorModule (Propriétés 16-20)
  - Créer `tests/property/test_properties_tables.py`
  - **Propriété 16: Nombre de lignes du tableau** - Tableau doit contenir exactement 153 lignes
  - **Valide: Exigences 4.1**
  - **Propriété 17: Correction du calcul de date** - t=1 → 1er juillet, t=153 → 30 novembre
  - **Valide: Exigences 4.3**
  - **Propriété 18: Attribution des statuts** - Assigner bon statut selon Q centrale
  - **Valide: Exigences 4.7**
  - **Propriété 19: Calcul de l'écart** - Écart % = ((Q réelle - Q centrale) / Q centrale) × 100
  - **Valide: Exigences 4.6**
  - **Propriété 20: Invariant du débit moyen** - Somme Q centrale / 153 ≈ Q̄_année (tolérance 5%)
  - **Valide: Exigences 4.10**

- [ ]* 5.2 Écrire les tests unitaires pour GeneratorModule
  - Tester génération complète avec k(A)=1.0, ε=0.05
  - Vérifier structure du DataFrame (10 colonnes)
  - Tester calcul des dates pour année 2024
  - Tester attribution des statuts aux frontières (Q=400, 600, 900, 1200)
  - Vérifier temps de génération < 500ms
  - _Exigences: 4.1, 4.2, 4.3, 4.7, 8.2_

- [x] 6. Implémenter le module AnalyzerModule
  - Créer le fichier `backend/formula/analyzer_module.py`
  - Implémenter la classe `AnalyzerModule` avec référence à CoefficientsModule
  - Implémenter `generate_annual_ranking()` pour classement annuel par k(A)
  - Implémenter `generate_monthly_ranking()` pour classement mensuel par Q moy
  - Implémenter `assign_qualification(k_A)` pour qualifications (Très humide, Humide, Normal, Sec, Très sec)
  - Implémenter `calculate_cv(data)` pour coefficient de variation
  - Calculer "vs Moyenne" = ((k(A) - 1.0) / 1.0) × 100
  - _Exigences: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 5.10, 5.11_

- [ ]* 6.1 Écrire les tests property-based pour AnalyzerModule (Propriétés 21-25)
  - Ajouter à `tests/property/test_properties_tables.py`
  - **Propriété 21: Calcul vs Moyenne** - "vs Moyenne" = ((k(A) - 1.0) / 1.0) × 100
  - **Valide: Exigences 5.9**
  - **Propriété 22: Coefficient de variation** - CV = (écart-type / moyenne) × 100
  - **Valide: Exigences 5.10**
  - **Propriété 23: Tri du classement annuel** - Lignes triées par k(A) décroissant
  - **Valide: Exigences 2.8, 5.3**
  - **Propriété 24: Tri du classement mensuel** - Lignes triées par Q moy décroissant
  - **Valide: Exigences 5.11**
  - **Propriété 25: Complétude du classement mensuel** - Exactement 5 mois (Juillet-Novembre)
  - **Valide: Exigences 5.13**

- [ ]* 6.2 Écrire les tests unitaires pour AnalyzerModule
  - Tester classement annuel avec données 2011-2024
  - Tester attribution des qualifications aux frontières (k(A)=0.8, 0.9, 1.1, 1.2)
  - Tester calcul CV avec données connues
  - Vérifier structure des DataFrames de classement
  - Vérifier temps de génération < 1s
  - _Exigences: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 5.8, 8.4_

- [x] 7. Implémenter le CacheManager
  - Créer le fichier `backend/formula/cache_manager.py`
  - Implémenter la classe `CacheManager` avec dict de cache et timestamps
  - Implémenter `get(key)` pour récupérer valeur du cache
  - Implémenter `set(key, value, ttl)` pour stocker avec TTL
  - Implémenter `invalidate(key)` pour invalider une entrée
  - Implémenter `clear()` pour vider tout le cache
  - _Exigences: 8.7, 8.8_

- [ ]* 7.1 Écrire les tests unitaires pour CacheManager
  - Tester stockage et récupération
  - Tester expiration TTL
  - Tester invalidation
  - Tester clear
  - _Exigences: 8.7_

- [ ] 8. Checkpoint - Vérifier tous les modules backend
  - Exécuter tous les tests (unitaires + property-based)
  - Vérifier que les 25 propriétés passent
  - Vérifier les performances (P(t) < 10ms, tableau < 500ms)
  - Demander à l'utilisateur si des questions se posent

- [x] 9. Implémenter le ExportManager
  - Créer le fichier `backend/formula/export_manager.py`
  - Implémenter la classe `ExportManager`
  - Implémenter `export_to_excel(data, filename, metadata)` avec openpyxl
  - Implémenter `export_to_pdf(data, filename, metadata)` avec matplotlib
  - Implémenter `create_prediction_chart(data)` pour graphique des prédictions
  - Inclure métadonnées (k(A), ε, date génération) dans exports
  - Nommer fichiers: predictions_formule_[date]_[heure].xlsx
  - Sauvegarder dans dossier "exports/"
  - _Exigences: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8_

- [ ]* 9.1 Écrire les tests d'intégration pour ExportManager
  - Créer `tests/integration/test_export_integration.py`
  - Tester export Excel avec données complètes
  - Tester export PDF avec graphique
  - Vérifier que fichiers peuvent être ouverts sans erreur
  - Vérifier temps d'export Excel < 3s
  - Vérifier temps d'export PDF < 5s
  - Vérifier gestion des erreurs (permissions, chemins invalides)
  - _Exigences: 9.1, 9.2, 9.5, 9.6, 9.9, 9.10, 8.5, 8.6_

- [x] 10. Créer les classes d'exceptions personnalisées
  - Créer le fichier `backend/formula/exceptions.py`
  - Implémenter `FormulaError` (exception de base)
  - Implémenter `InvalidDayError` pour jour invalide
  - Implémenter `InvalidCoefficientError` pour k(A) invalide
  - Implémenter `InvalidEpsilonError` pour ε invalide
  - Implémenter `MissingDataError` pour données manquantes
  - Implémenter `ExportError` pour erreurs d'export
  - _Exigences: 7.1, 7.2, 7.3, 7.4, 7.5, 7.9_

- [ ]* 10.1 Écrire les tests unitaires pour exceptions
  - Tester que chaque exception est levée dans les bons cas
  - Tester messages d'erreur exacts
  - Vérifier hiérarchie des exceptions
  - _Exigences: 7.1, 7.2, 7.3, 7.4_

- [x] 11. Intégrer dans l'UI PyQt5 - Créer PhaseSelectionDialog
  - Modifier `phase2_prediction.py`
  - Créer la classe `PhaseSelectionDialog(QDialog)` après la classe `ProgressDialog`
  - Implémenter `init_ui()` avec 5 boutons pour les phases
  - Boutons: "Phase 1: Formule Maîtresse", "Phase 2: Coefficients", "Phase 3: Calculateur", "Phase 4: Tableau Complet", "Phase 5: Analyse Comparative"
  - Implémenter `get_selected_phase()` pour retourner phase sélectionnée (1-5)
  - Styliser avec CSS cohérent avec l'application existante
  - _Exigences: 6.1, 6.2_

- [x] 12. Intégrer dans l'UI PyQt5 - Connecter le bouton "Générer Prédictions (Formule)"
  - Dans `PredictionWindow.create_control_panel()`, le bouton existe déjà (ligne ~450)
  - Implémenter la méthode `generate_predictions_formula(self)` dans `PredictionWindow`
  - Afficher `PhaseSelectionDialog` au clic
  - Récupérer la phase sélectionnée
  - Router vers la méthode appropriée selon la phase
  - _Exigences: 6.1, 6.2, 6.8_

- [x] 13. Implémenter Phase 1 dans l'UI - Formule Maîtresse
  - Créer la méthode `show_phase1_formula_master(self)` dans `PredictionWindow`
  - Créer un dialogue avec formulaire pour saisir k(A) et ε
  - Valider les entrées avec FormulaModule.validate_inputs()
  - Afficher les résultats dans un dialogue ou onglet
  - Gérer les erreurs avec messages clairs
  - _Exigences: 6.3, 7.1, 7.2, 7.3, 7.6, 7.7_

- [x] 14. Implémenter Phase 2 dans l'UI - Coefficients
  - Créer la méthode `show_phase2_coefficients(self)` dans `PredictionWindow`
  - Instancier CoefficientsModule avec données historiques
  - Générer les trois tableaux (A, B, C)
  - Afficher dans QTableWidget ou QTextEdit formaté
  - Vérifier temps d'affichage < 2s
  - _Exigences: 6.4, 2.1, 2.2, 2.3, 8.3_

- [x] 15. Implémenter Phase 3 dans l'UI - Calculateur
  - Créer la méthode `show_phase3_calculator(self)` dans `PredictionWindow`
  - Créer un dialogue avec formulaire pour saisir t, k(A), ε
  - Instancier CalculatorModule
  - Calculer et afficher P(t), Q centrale, Q min, Q max
  - Afficher mois et Cm déduits automatiquement
  - Gérer les erreurs de validation
  - _Exigences: 6.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 16. Implémenter Phase 4 dans l'UI - Tableau Complet
  - Créer la méthode `show_phase4_full_table(self)` dans `PredictionWindow`
  - Créer un dialogue avec formulaire pour saisir k(A), ε, année
  - Instancier GeneratorModule
  - Générer le tableau de 153 jours
  - Afficher dans QTableWidget avec toutes les colonnes
  - Ajouter boutons "Exporter Excel" et "Exporter PDF"
  - Connecter aux méthodes d'export
  - Stocker les prédictions dans self.future_predictions pour export ultérieur
  - _Exigences: 6.6, 4.1, 4.2, 4.8, 4.9, 6.10_

- [x] 17. Implémenter Phase 5 dans l'UI - Analyse Comparative
  - Créer la méthode `show_phase5_comparative_analysis(self)` dans `PredictionWindow`
  - Instancier AnalyzerModule avec CoefficientsModule
  - Générer classement annuel et mensuel
  - Afficher dans deux QTableWidget côte à côte ou onglets
  - Ajouter bouton "Exporter Excel" pour les classements
  - _Exigences: 6.7, 5.1, 5.2, 9.4_

- [x] 18. Implémenter la navigation entre phases
  - Permettre retour au dialogue de sélection depuis chaque phase
  - Préserver les données saisies (k(A), ε) entre phases
  - Ajouter bouton "Retour" dans chaque dialogue de phase
  - _Exigences: 6.9_

- [x] 19. Implémenter l'aide contextuelle
  - Créer le fichier `backend/formula/help_texts.py` avec textes d'aide
  - Ajouter bouton "?" à côté de chaque phase dans PhaseSelectionDialog
  - Créer la méthode `show_help(phase_number)` pour afficher aide
  - Implémenter infobulles (tooltips) pour champs de saisie
  - Textes en français avec exemples de valeurs typiques
  - _Exigences: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 10.9, 10.10_

- [ ]* 19.1 Écrire les tests d'intégration pour l'UI
  - Créer `tests/integration/test_ui_integration.py`
  - Tester ouverture de PhaseSelectionDialog
  - Tester navigation vers chaque phase
  - Tester validation des formulaires
  - Tester affichage des messages d'erreur
  - Tester préservation des données entre phases
  - _Exigences: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.9_

- [x] 20. Implémenter le logging des erreurs
  - Créer le fichier `backend/formula/logger.py`
  - Configurer logging Python avec fichier de log
  - Logger toutes les erreurs de validation
  - Logger toutes les erreurs de calcul
  - Logger toutes les erreurs d'export
  - Fichier de log: `logs/formula_predictions.log`
  - _Exigences: 7.8_

- [ ]* 20.1 Écrire les tests unitaires pour logging
  - Tester que erreurs sont loggées correctement
  - Vérifier format des messages de log
  - Tester rotation des fichiers de log
  - _Exigences: 7.8_

- [x] 21. Checkpoint - Tests d'intégration complets
  - Exécuter le workflow complet Phase 1 → Phase 4 → Export
  - Tester avec données réelles (2011-2024)
  - Vérifier tous les exports (Excel, PDF)
  - Vérifier toutes les performances (<500ms pour 153 jours)
  - Demander à l'utilisateur si des questions se posent

- [ ]* 22. Écrire les tests de performance
  - Créer `tests/integration/test_performance.py`
  - Mesurer temps de calcul P(t) < 10ms
  - Mesurer temps de génération 153 jours < 500ms
  - Mesurer temps d'affichage tableaux < 2s
  - Mesurer temps de génération classements < 1s
  - Mesurer temps d'export Excel < 3s
  - Mesurer temps d'export PDF < 5s
  - _Exigences: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

- [ ]* 23. Écrire les tests end-to-end
  - Créer `tests/integration/test_end_to_end.py`
  - Tester workflow complet: charger données → Phase 1 → Phase 4 → Export Excel
  - Tester workflow: Phase 2 → Phase 5 → Export classements
  - Tester workflow: Phase 3 → calculs multiples
  - Vérifier que fichiers exportés sont valides
  - _Exigences: 6.1-6.10, 9.1-9.10_

- [x] 24. Créer la documentation utilisateur
  - Créer le fichier `docs/FORMULE_PREDICTION_GUIDE.md`
  - Documenter chaque phase avec captures d'écran
  - Expliquer la signification de k(A), ε, Cm
  - Fournir exemples de valeurs typiques
  - Expliquer les statuts et qualifications
  - Inclure FAQ et troubleshooting
  - _Exigences: 10.1-10.10_

- [x] 25. Finaliser et valider
  - Exécuter tous les tests (unitaires, property-based, intégration, performance)
  - Vérifier couverture de code > 90%
  - Vérifier que les 25 propriétés passent avec 1000 itérations
  - Vérifier que les 100 critères d'acceptation sont satisfaits
  - Créer un rapport de validation final
  - Demander validation finale à l'utilisateur

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être sautées pour un MVP rapide
- Chaque tâche référence les exigences spécifiques pour traçabilité
- Les checkpoints permettent une validation incrémentale
- Les tests property-based valident les propriétés universelles de correction
- Les tests unitaires valident les cas spécifiques et edge cases
- Les tests d'intégration valident les workflows end-to-end
- L'implémentation suit une approche bottom-up: modules de base → calculateurs → UI → exports
