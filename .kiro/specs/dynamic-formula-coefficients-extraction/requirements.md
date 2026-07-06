# Requirements Document

## Introduction

Ce document définit les exigences pour rendre le système de prédiction hydrologique par formules universel et adaptable à n'importe quelle zone géographique. Actuellement, l'application utilise des coefficients codés en dur spécifiques au barrage de Mbakaou. Cette fonctionnalité permettra d'extraire automatiquement les coefficients à partir des données chargées par l'utilisateur, tout en maintenant la rétrocompatibilité avec les coefficients Mbakaou par défaut.

## Glossary

- **System**: Le système de prédiction hydrologique par formules
- **Coefficient_Extractor**: Le module responsable de l'extraction des coefficients à partir des données historiques
- **Formula_Module**: Le module de calcul de la formule maîtresse pour la saison des pluies
- **Formula_Module_Seche**: Le module de calcul de la formule maîtresse pour la saison sèche
- **Coefficients_Module**: Le module de gestion des coefficients annuels et mensuels
- **User**: L'utilisateur de l'application (hydrologue, ingénieur)
- **Historical_Data**: Les données historiques de débits chargées par l'utilisateur
- **Polynomial_Coefficients**: Les coefficients du polynôme P(t) d'ordre 6
- **Monthly_Coefficients**: Les coefficients mensuels Cm
- **Annual_Coefficient**: Le coefficient annuel k(A)
- **Q_Historical**: Le débit historique de référence moyen
- **Mbakaou_Coefficients**: Les coefficients par défaut spécifiques au barrage de Mbakaou
- **Data_Quality_Validator**: Le composant qui valide la qualité des données historiques
- **Season_Duration**: La durée fixe des saisons (153 jours pour pluies, 212 jours pour sèche)

## Requirements

### Requirement 1: Validation de la Qualité des Données

**User Story:** En tant qu'utilisateur, je veux que le système valide la qualité de mes données historiques, afin de garantir des prédictions fiables.

#### Acceptance Criteria

1. WHEN Historical_Data is loaded, THE Data_Quality_Validator SHALL verify that the data spans at least 10 years
2. WHEN Historical_Data is loaded, THE Data_Quality_Validator SHALL calculate the percentage of missing values
3. IF the data spans less than 10 years, THEN THE System SHALL display a warning message indicating insufficient historical depth
4. IF the percentage of missing values exceeds 15%, THEN THE System SHALL display a warning message indicating incomplete data
5. THE Data_Quality_Validator SHALL return a quality score between 0 and 100
6. WHEN data quality is insufficient, THE System SHALL allow the User to proceed with Mbakaou_Coefficients as fallback

### Requirement 2: Extraction des Coefficients du Polynôme

**User Story:** En tant qu'utilisateur, je veux que le système extraie automatiquement les coefficients du polynôme P(t) à partir de mes données, afin d'adapter les prédictions à ma zone géographique.

#### Acceptance Criteria

1. WHEN Historical_Data passes quality validation, THE Coefficient_Extractor SHALL fit a 6th-order polynomial to the seasonal flow data
2. THE Coefficient_Extractor SHALL extract coefficients for terms t⁶, t⁵, t⁴, t³, t², t¹, and t⁰
3. THE Coefficient_Extractor SHALL calculate the R² coefficient of determination for the polynomial fit
4. IF R² is less than 0.90, THEN THE System SHALL display a warning about low polynomial fit quality
5. THE Coefficient_Extractor SHALL store the extracted Polynomial_Coefficients for use in predictions
6. THE Coefficient_Extractor SHALL maintain separate polynomial coefficients for rainy season (153 days) and dry season (212 days)

### Requirement 3: Extraction des Coefficients Mensuels

**User Story:** En tant qu'utilisateur, je veux que le système calcule automatiquement les coefficients mensuels Cm à partir de mes données, afin de capturer les variations saisonnières propres à ma zone.

#### Acceptance Criteria

1. WHEN Historical_Data passes quality validation, THE Coefficient_Extractor SHALL calculate the mean flow for each month
2. FOR the rainy season, THE Coefficient_Extractor SHALL calculate Monthly_Coefficients for months 7, 8, 9, 10, and 11
3. FOR the dry season, THE Coefficient_Extractor SHALL calculate Monthly_Coefficients for months 12, 1, 2, 3, 4, 5, and 6
4. THE Coefficient_Extractor SHALL normalize Monthly_Coefficients relative to the seasonal mean flow
5. THE Coefficient_Extractor SHALL store the extracted Monthly_Coefficients for use in predictions
6. THE System SHALL use the fixed Season_Duration values (153 days for rainy, 212 days for dry) for all zones

### Requirement 4: Calcul du Débit Historique de Référence

**User Story:** En tant qu'utilisateur, je veux que le système calcule le débit historique moyen Q_Historical à partir de mes données, afin d'avoir une référence adaptée à ma zone.

#### Acceptance Criteria

1. WHEN Historical_Data passes quality validation, THE Coefficient_Extractor SHALL calculate the mean flow across all historical data for the rainy season
2. WHEN Historical_Data passes quality validation, THE Coefficient_Extractor SHALL calculate the mean flow across all historical data for the dry season
3. THE Coefficient_Extractor SHALL store Q_Historical separately for rainy season and dry season
4. THE System SHALL use the extracted Q_Historical values for calculating Annual_Coefficient k(A)
5. THE System SHALL display the calculated Q_Historical values to the User for verification

### Requirement 5: Calcul des Coefficients Annuels

**User Story:** En tant qu'utilisateur, je veux que le système calcule automatiquement les coefficients annuels k(A) pour chaque année de mes données, afin de capturer la variabilité interannuelle.

#### Acceptance Criteria

1. WHEN Historical_Data passes quality validation, THE Coefficient_Extractor SHALL calculate Annual_Coefficient k(A) for each year using the formula k(A) = Q̄_année / Q̄_historique
2. THE Coefficient_Extractor SHALL store all calculated Annual_Coefficient values indexed by year
3. THE System SHALL provide Annual_Coefficient values to Formula_Module and Formula_Module_Seche for predictions
4. THE System SHALL calculate humidity status for each year based on k(A) thresholds
5. THE System SHALL rank years by humidity level from wettest to driest

### Requirement 6: Rétrocompatibilité avec les Coefficients Mbakaou

**User Story:** En tant qu'utilisateur, je veux que le système utilise les coefficients Mbakaou par défaut quand aucune donnée n'est chargée, afin de maintenir la compatibilité avec les prédictions existantes.

#### Acceptance Criteria

1. WHEN no Historical_Data is loaded, THE System SHALL use Mbakaou_Coefficients for all predictions
2. WHEN Historical_Data is loaded but fails quality validation, THE System SHALL offer to use Mbakaou_Coefficients as fallback
3. THE System SHALL preserve the existing Mbakaou_Coefficients values in the codebase
4. THE System SHALL clearly indicate to the User whether Mbakaou_Coefficients or extracted coefficients are being used
5. THE System SHALL allow the User to manually switch between Mbakaou_Coefficients and extracted coefficients

### Requirement 7: Intégration avec les Modules de Formules Existants

**User Story:** En tant qu'utilisateur, je veux que les coefficients extraits soient automatiquement utilisés par les modules de prédiction, afin d'obtenir des prédictions adaptées à ma zone sans configuration manuelle.

#### Acceptance Criteria

1. WHEN coefficients are extracted, THE System SHALL update Formula_Module with the new Polynomial_Coefficients and Monthly_Coefficients for rainy season
2. WHEN coefficients are extracted, THE System SHALL update Formula_Module_Seche with the new Polynomial_Coefficients and Monthly_Coefficients for dry season
3. WHEN coefficients are extracted, THE System SHALL update Coefficients_Module with the new Annual_Coefficient values and Q_Historical
4. THE System SHALL maintain the existing formula structure Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
5. THE System SHALL preserve the existing validation logic in Formula_Module and Formula_Module_Seche
6. THE System SHALL preserve the July adjustment logic in Formula_Module (16.5 m³/s daily increment)

### Requirement 8: Gestion du Cache et Rafraîchissement

**User Story:** En tant qu'utilisateur, je veux que le système rafraîchisse automatiquement les coefficients quand je charge de nouvelles données, afin d'éviter d'utiliser des coefficients obsolètes.

#### Acceptance Criteria

1. WHEN new Historical_Data is loaded, THE System SHALL clear any cached coefficient values
2. WHEN new Historical_Data is loaded, THE System SHALL trigger automatic extraction of new coefficients
3. THE System SHALL store extracted coefficients in memory for the current session
4. WHEN the User closes the application, THE System SHALL revert to Mbakaou_Coefficients for the next session
5. THE System SHALL provide a manual refresh button to re-extract coefficients from loaded data

### Requirement 9: Affichage des Coefficients Extraits

**User Story:** En tant qu'utilisateur, je veux visualiser les coefficients extraits dans l'interface, afin de vérifier leur cohérence et leur qualité.

#### Acceptance Criteria

1. WHEN coefficients are extracted, THE System SHALL display the Polynomial_Coefficients table with R² value
2. WHEN coefficients are extracted, THE System SHALL display the Monthly_Coefficients table with mean flows
3. WHEN coefficients are extracted, THE System SHALL display the Annual_Coefficient table with humidity rankings
4. THE System SHALL display the extracted Q_Historical value alongside the Mbakaou default value for comparison
5. THE System SHALL highlight any coefficients that differ significantly from Mbakaou_Coefficients
6. THE System SHALL provide export functionality for the extracted coefficients table

### Requirement 10: Préservation de la Méthodologie Scientifique

**User Story:** En tant qu'utilisateur, je veux que le système maintienne la même méthodologie scientifique pour toutes les zones, afin de garantir la cohérence et la validité des prédictions.

#### Acceptance Criteria

1. THE System SHALL use the same polynomial order (6) for all geographic zones
2. THE System SHALL use the same Season_Duration values (153 days rainy, 212 days dry) for all zones
3. THE System SHALL use the same month count (5 months rainy, 7 months dry) for all zones
4. THE System SHALL use the same confidence interval bounds (±8% for dry season, -8%/+19% for rainy season)
5. THE System SHALL use the same formula structure Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)] for all zones
6. THE System SHALL validate that epsilon remains between 0.01 and 0.08 for all zones

### Requirement 11: Limitation du Scope aux Modules de Formules

**User Story:** En tant qu'utilisateur, je veux que les modifications soient limitées aux modules de prédiction par formules, afin de ne pas perturber les autres fonctionnalités de l'application.

#### Acceptance Criteria

1. THE System SHALL modify only formula_module.py, formula_module_seche.py, calculator_module.py, calculator_module_seche.py, generator_module.py, generator_module_seche.py, coefficients_module.py, and coefficients_module_seche.py
2. THE System SHALL preserve the ML prediction modules unchanged
3. THE System SHALL preserve the analysis modules unchanged
4. THE System SHALL preserve the climate modules unchanged
5. THE System SHALL preserve the export modules unchanged
6. THE System SHALL preserve the UI modules except for coefficient display enhancements

### Requirement 12: Gestion des Erreurs et Messages Utilisateur

**User Story:** En tant qu'utilisateur, je veux recevoir des messages clairs en cas de problème avec l'extraction des coefficients, afin de comprendre comment résoudre les problèmes.

#### Acceptance Criteria

1. WHEN coefficient extraction fails, THE System SHALL display a descriptive error message indicating the cause
2. WHEN data quality is insufficient, THE System SHALL display specific warnings about which quality criteria failed
3. WHEN polynomial fit quality is low, THE System SHALL display the R² value and suggest data improvements
4. WHEN extraction succeeds, THE System SHALL display a success message with a summary of extracted coefficients
5. THE System SHALL log all extraction attempts and results for debugging purposes
6. THE System SHALL provide actionable recommendations when extraction fails

