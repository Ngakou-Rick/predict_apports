# Document d'Exigences - Formule de Prédiction à 5 Phases pour la Saison des Pluies

## Introduction

Ce document définit les exigences pour l'implémentation d'une formule de prédiction à 5 phases pour la saison des pluies de la Rivière Tadang (2011-2024). La formule maîtresse utilise un polynôme d'ordre 6 avec des coefficients annuels et mensuels pour prédire les débits journaliers pendant la saison des pluies (1er juillet au 30 novembre, 153 jours).

## Glossaire

- **System**: Le système de prédiction hydrologique intégré dans phase2_prediction.py
- **Formule_Maîtresse**: La formule Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
- **Polynôme_P**: Polynôme d'ordre 6 pour calculer le débit de base P(t)
- **Coefficient_Annuel**: k(A) = Q̄_année / Q̄_historique (739 m³/s)
- **Coefficient_Mensuel**: Cm pour juillet (0.697), août (1.011), septembre (1.300), octobre (1.333), novembre (0.658)
- **Taux_Erreur**: ε ∈ [0.01; 0.08] choisi par l'utilisateur pour toute la saison
- **Jour_Saison**: t ∈ [1, 153] où 1 = 1er juillet et 153 = 30 novembre
- **Q_Historique**: Débit moyen historique de référence (739 m³/s)
- **Saison_Pluies**: Période du 1er juillet au 30 novembre (153 jours)
- **Interface_Utilisateur**: Interface graphique PyQt5 dans phase2_prediction.py
- **Calculateur**: Module de calcul pour un jour unique
- **Générateur_Tableau**: Module générant le tableau complet de 153 jours
- **Analyseur_Comparatif**: Module produisant les classements annuels et mensuels

## Exigences

### Exigence 1: Formule Maîtresse de Prédiction

**User Story:** En tant qu'hydrologue, je veux calculer les débits prédits avec la formule Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)], afin d'obtenir des prédictions précises pour la saison des pluies.

#### Critères d'Acceptation

1. THE Polynôme_P SHALL calculer P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴ − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2
2. WHEN Jour_Saison t est fourni, THE Polynôme_P SHALL retourner P(t) avec une précision de 2 décimales
3. THE System SHALL calculer Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
4. THE System SHALL calculer Q_inf = P(t) × k(A) × Cm × 0.92
5. THE System SHALL calculer Q_sup = P(t) × k(A) × Cm × 1.08
6. WHEN k(A) est fourni par l'utilisateur, THE System SHALL valider que k(A) > 0
7. WHEN ε est fourni par l'utilisateur, THE System SHALL valider que 0.01 ≤ ε ≤ 0.08
8. THE System SHALL déduire automatiquement le mois à partir de t (1-31→Juillet, 32-62→Août, 63-92→Septembre, 93-123→Octobre, 124-153→Novembre)
9. THE System SHALL appliquer le Coefficient_Mensuel correspondant au mois déduit
10. FOR ALL valeurs valides de t, k(A), et ε, calculer Q(t,A) puis recalculer avec les mêmes paramètres SHALL produire le même résultat (idempotence)

### Exigence 2: Affichage des Coefficients et Paramètres

**User Story:** En tant qu'hydrologue, je veux visualiser les coefficients annuels, mensuels et du polynôme dans des tableaux structurés, afin de comprendre les paramètres de la formule.

#### Critères d'Acceptation

1. THE System SHALL afficher le Tableau A avec les colonnes: Année, k(A), Humidité relative, Q moy, Rang humidité, Statut
2. THE System SHALL afficher le Tableau B avec les colonnes: Mois, Cm, Q moy, Intervalle P10-P90, Tendance %/j, Succession max ↑/↓
3. THE System SHALL afficher le Tableau C avec les colonnes: Terme, Coefficient, Exposant de t, Contribution
4. THE System SHALL calculer k(A) = Q̄_année / 739 pour chaque année de 2011 à 2024
5. THE System SHALL afficher R²=0.988 dans le Tableau C
6. WHEN l'utilisateur demande l'affichage des tableaux, THE System SHALL générer les trois tableaux en moins de 2 secondes
7. THE System SHALL formater les coefficients avec 3 décimales minimum
8. THE System SHALL trier le Tableau A par rang d'humidité (du plus humide au plus sec)
9. THE System SHALL afficher les Coefficients_Mensuels: Juillet=0.697, Août=1.011, Sep=1.300, Oct=1.333, Nov=0.658
10. FOR ALL années dans les données historiques (2011-2024), calculer k(A) puis afficher le tableau SHALL inclure toutes les années sans omission

### Exigence 3: Calculateur de Débit pour un Jour Unique

**User Story:** En tant qu'hydrologue, je veux calculer le débit prédit pour un jour spécifique, afin de tester rapidement différents scénarios.

#### Critères d'Acceptation

1. WHEN l'utilisateur fournit t (1-153), k(A), et ε (%), THE Calculateur SHALL calculer P(t), Q centrale, Q min, Q max
2. THE Calculateur SHALL déduire automatiquement le mois à partir de t
3. THE Calculateur SHALL déduire automatiquement Cm à partir du mois
4. THE Calculateur SHALL afficher les résultats avec les labels: P(t), Q centrale, Q min (-8%), Q max (+8%)
5. WHEN t < 1 OU t > 153, THE Calculateur SHALL retourner un message d'erreur "Jour invalide: doit être entre 1 et 153"
6. WHEN k(A) ≤ 0, THE Calculateur SHALL retourner un message d'erreur "Coefficient annuel invalide: doit être > 0"
7. WHEN ε < 0.01 OU ε > 0.08, THE Calculateur SHALL retourner un message d'erreur "Taux d'erreur invalide: doit être entre 1% et 8%"
8. THE Calculateur SHALL compléter le calcul en moins de 100 millisecondes
9. THE Calculateur SHALL formater les débits avec 2 décimales
10. FOR ALL combinaisons valides de (t, k(A), ε), calculer le débit deux fois consécutivement SHALL produire des résultats identiques

### Exigence 4: Générateur de Prédictions Journalières Complètes

**User Story:** En tant qu'hydrologue, je veux générer un tableau complet de 153 jours avec les prédictions, afin d'avoir une vue d'ensemble de toute la saison des pluies.

#### Critères d'Acceptation

1. WHEN l'utilisateur fournit k(A) et ε, THE Générateur_Tableau SHALL créer 153 lignes (une par jour)
2. THE Générateur_Tableau SHALL inclure les colonnes: t, Date, Mois, P(t), Q centrale, Q min (-8%), Q max (+8%), Q réelle, Écart %, Statut
3. THE Générateur_Tableau SHALL calculer la Date à partir de t (t=1 → 1er juillet, t=153 → 30 novembre)
4. THE Générateur_Tableau SHALL déduire le Mois à partir de t
5. THE Générateur_Tableau SHALL laisser "Q réelle" vide initialement
6. THE Générateur_Tableau SHALL calculer "Écart %" = ((Q réelle - Q centrale) / Q centrale) × 100 SEULEMENT si Q réelle est fournie
7. THE Générateur_Tableau SHALL assigner le Statut basé sur Q centrale: 🚨 Dangereux (>1200), 🔔 Élevé (900-1200), ✅ Normal (600-900), 🌤️ Modéré (400-600), ℹ️ Bas (<400)
8. THE Générateur_Tableau SHALL permettre l'export en format Excel (.xlsx)
9. THE Générateur_Tableau SHALL permettre l'export en format PDF
10. FOR ALL lignes du tableau, la somme des débits Q centrale divisée par 153 SHALL être approximativement égale à Q̄_année utilisé pour calculer k(A)

### Exigence 5: Analyse Comparative Annuelle et Mensuelle

**User Story:** En tant qu'hydrologue, je veux comparer les années et les mois par classement, afin d'identifier les périodes les plus humides et les plus sèches.

#### Critères d'Acceptation

1. THE Analyseur_Comparatif SHALL générer un classement annuel avec les colonnes: Rang, Année, k(A), Q moy, Qualif., vs Moyenne
2. THE Analyseur_Comparatif SHALL générer un classement mensuel avec les colonnes: Rang, Mois, Q moy, Cm, Tendance %/j, Variabilité CV, Statut
3. THE Analyseur_Comparatif SHALL trier le classement annuel par k(A) décroissant
4. THE Analyseur_Comparatif SHALL assigner Qualif. = "Très humide" si k(A) > 1.2
5. THE Analyseur_Comparatif SHALL assigner Qualif. = "Humide" si 1.1 < k(A) ≤ 1.2
6. THE Analyseur_Comparatif SHALL assigner Qualif. = "Normal" si 0.9 ≤ k(A) ≤ 1.1
7. THE Analyseur_Comparatif SHALL assigner Qualif. = "Sec" si 0.8 ≤ k(A) < 0.9
8. THE Analyseur_Comparatif SHALL assigner Qualif. = "Très sec" si k(A) < 0.8
9. THE Analyseur_Comparatif SHALL calculer "vs Moyenne" = ((k(A) - 1.0) / 1.0) × 100
10. THE Analyseur_Comparatif SHALL calculer CV = (écart-type / moyenne) × 100 pour chaque mois
11. THE Analyseur_Comparatif SHALL trier le classement mensuel par Q moy décroissant
12. THE Analyseur_Comparatif SHALL calculer la Tendance %/j comme la variation moyenne quotidienne en pourcentage
13. FOR ALL mois dans la Saison_Pluies, le classement mensuel SHALL inclure exactement 5 mois (Juillet, Août, Septembre, Octobre, Novembre)

### Exigence 6: Intégration dans l'Interface Utilisateur Existante

**User Story:** En tant qu'utilisateur de l'application, je veux accéder aux 5 phases via l'interface graphique existante, afin d'utiliser la formule sans modifier mon workflow actuel.

#### Critères d'Acceptation

1. WHEN l'utilisateur clique sur "🔮 Générer Prédictions (Formule)", THE Interface_Utilisateur SHALL afficher un dialogue de sélection des 5 phases
2. THE Interface_Utilisateur SHALL ajouter les options: "Phase 1: Formule Maîtresse", "Phase 2: Coefficients", "Phase 3: Calculateur", "Phase 4: Tableau Complet", "Phase 5: Analyse Comparative"
3. WHEN l'utilisateur sélectionne "Phase 1", THE System SHALL afficher un formulaire pour saisir k(A) et ε
4. WHEN l'utilisateur sélectionne "Phase 2", THE System SHALL afficher les trois tableaux (A, B, C)
5. WHEN l'utilisateur sélectionne "Phase 3", THE System SHALL afficher le calculateur de jour unique
6. WHEN l'utilisateur sélectionne "Phase 4", THE System SHALL générer le tableau de 153 jours
7. WHEN l'utilisateur sélectionne "Phase 5", THE System SHALL afficher les classements annuel et mensuel
8. THE Interface_Utilisateur SHALL préserver les fonctionnalités existantes de phase2_prediction.py
9. THE Interface_Utilisateur SHALL permettre la navigation entre les 5 phases sans perdre les données saisies
10. WHEN l'utilisateur exporte depuis Phase 4, THE System SHALL inclure toutes les colonnes du tableau dans le fichier Excel ou PDF

### Exigence 7: Validation et Gestion des Erreurs

**User Story:** En tant qu'utilisateur, je veux recevoir des messages d'erreur clairs quand je saisis des valeurs invalides, afin de corriger rapidement mes erreurs.

#### Critères d'Acceptation

1. WHEN t < 1 OU t > 153, THE System SHALL afficher "Erreur: Jour de saison doit être entre 1 et 153"
2. WHEN k(A) ≤ 0, THE System SHALL afficher "Erreur: Coefficient annuel doit être strictement positif"
3. WHEN ε < 0.01 OU ε > 0.08, THE System SHALL afficher "Erreur: Taux d'erreur doit être entre 1% et 8%"
4. WHEN les données historiques sont manquantes pour une année, THE System SHALL afficher "Avertissement: Données incomplètes pour l'année [année]"
5. WHEN l'utilisateur tente d'exporter sans avoir généré de prédictions, THE System SHALL afficher "Erreur: Veuillez d'abord générer les prédictions"
6. THE System SHALL valider tous les paramètres avant de lancer les calculs
7. THE System SHALL afficher les messages d'erreur dans une boîte de dialogue modale
8. THE System SHALL logger toutes les erreurs dans un fichier de log
9. WHEN une erreur de calcul survient, THE System SHALL afficher le message d'erreur et permettre à l'utilisateur de corriger les paramètres
10. FOR ALL erreurs de validation, afficher le message puis permettre une nouvelle saisie SHALL permettre à l'utilisateur de corriger sans redémarrer l'application

### Exigence 8: Performance et Optimisation

**User Story:** En tant qu'utilisateur, je veux que les calculs soient rapides, afin de tester plusieurs scénarios efficacement.

#### Critères d'Acceptation

1. THE System SHALL calculer P(t) pour un jour unique en moins de 10 millisecondes
2. THE System SHALL générer le tableau complet de 153 jours en moins de 500 millisecondes
3. THE System SHALL afficher les tableaux de coefficients en moins de 2 secondes
4. THE System SHALL générer les classements comparatifs en moins de 1 seconde
5. THE System SHALL exporter le tableau Excel en moins de 3 secondes
6. THE System SHALL exporter le PDF en moins de 5 secondes
7. THE System SHALL mettre en cache les coefficients calculés pour éviter les recalculs
8. WHEN l'utilisateur change k(A) ou ε, THE System SHALL recalculer uniquement les valeurs affectées
9. THE System SHALL utiliser des calculs vectorisés pour le tableau de 153 jours
10. FOR ALL opérations de calcul, utiliser des structures de données optimisées SHALL maintenir les temps de réponse sous les seuils définis même avec 14 ans de données historiques

### Exigence 9: Export et Persistance des Données

**User Story:** En tant qu'hydrologue, je veux exporter les résultats en Excel et PDF, afin de partager les prédictions avec mon équipe.

#### Critères d'Acceptation

1. THE System SHALL exporter le tableau de 153 jours en format Excel (.xlsx)
2. THE System SHALL exporter le tableau de 153 jours en format PDF
3. THE System SHALL exporter les tableaux de coefficients (A, B, C) en format Excel
4. THE System SHALL exporter les classements comparatifs en format Excel
5. THE System SHALL inclure un graphique des prédictions dans l'export PDF
6. THE System SHALL nommer les fichiers exportés avec le format: predictions_formule_[date]_[heure].xlsx
7. THE System SHALL sauvegarder les exports dans le dossier "exports/"
8. THE System SHALL inclure les métadonnées (k(A), ε, date de génération) dans les exports
9. WHEN l'export échoue, THE System SHALL afficher un message d'erreur explicite
10. FOR ALL exports Excel, ouvrir le fichier dans Excel SHALL afficher toutes les colonnes correctement formatées sans erreur

### Exigence 10: Documentation et Aide Contextuelle

**User Story:** En tant qu'utilisateur, je veux accéder à une aide contextuelle pour chaque phase, afin de comprendre comment utiliser la formule.

#### Critères d'Acceptation

1. THE System SHALL afficher une infobulle explicative pour chaque champ de saisie
2. THE System SHALL inclure un bouton "?" à côté de chaque phase pour afficher l'aide
3. WHEN l'utilisateur clique sur "?", THE System SHALL afficher une fenêtre d'aide avec la description de la phase
4. THE System SHALL expliquer la signification de k(A) dans l'aide de Phase 1
5. THE System SHALL expliquer la signification de ε dans l'aide de Phase 1
6. THE System SHALL expliquer la signification des colonnes du Tableau A dans l'aide de Phase 2
7. THE System SHALL expliquer la signification des statuts (🚨, 🔔, ✅, 🌤️, ℹ️) dans l'aide de Phase 4
8. THE System SHALL expliquer la signification de CV (Coefficient de Variation) dans l'aide de Phase 5
9. THE System SHALL inclure des exemples de valeurs typiques pour k(A) et ε
10. THE System SHALL afficher l'aide en français

