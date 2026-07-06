# Plan d'Implémentation: Bouton Retour au Menu des Phases

## Vue d'ensemble

Cette implémentation ajoute un bouton de navigation "🔙 Retour au Menu des Phases" dans les onglets de prédiction par formules (saison sèche et saison pluies) de l'application de prévision hydrologique. Le bouton permettra aux utilisateurs de basculer facilement vers l'onglet Données sans perdre leurs données chargées en mémoire.

**Fichier à modifier**: `frontend/ui/main_window.py`

**Langage**: Python (PyQt5)

**Approche**: Ajouter un bouton de navigation dans les deux onglets de formules qui utilise `self.tabs.setCurrentIndex(0)` pour revenir à l'onglet Données.

## Tâches

- [x] 1. Créer la méthode helper pour le bouton de navigation
  - Ajouter la méthode `create_navigation_button()` dans la classe `MainWindow`
  - Implémenter le style CSS personnalisé avec les couleurs spécifiées (#6c757d, hover: #5a6268, pressed: #545b62)
  - Configurer le texte du bouton: "🔙 Retour au Menu des Phases"
  - Définir la hauteur minimale à 40px et le border-radius à 5px
  - Ajouter le tooltip: "Retourner au menu principal pour choisir un autre mode de prédiction"
  - Configurer l'accessibilité: `setFocusPolicy(Qt.StrongFocus)`, `setAccessibleName()`, `setAccessibleDescription()`
  - Connecter le signal `clicked` à la méthode handler `navigate_to_main_menu`
  - _Exigences: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 1.1 Écrire des tests unitaires pour la création du bouton
  - Tester que le bouton est créé avec le texte correct
  - Tester que le style CSS contient les bonnes couleurs
  - Tester que la hauteur minimale est de 40px
  - Tester que le tooltip est défini correctement
  - Tester que les propriétés d'accessibilité sont configurées
  - _Exigences: 1.1, 1.4, 1.5, 4.2, 4.3, 4.4, 4.5, 7.1, 7.2, 7.3, 7.4_

- [x] 2. Créer la méthode handler de navigation
  - Ajouter la méthode `navigate_to_main_menu()` dans la classe `MainWindow`
  - Implémenter la logique de changement d'onglet avec `self.tabs.setCurrentIndex(0)`
  - Ajouter la gestion d'erreur avec try-except pour les cas limites
  - Ajouter le logging pour tracer les navigations
  - Vérifier que l'index de l'onglet est valide avant de changer
  - _Exigences: 2.1, 2.2, 2.4, 6.1, 6.2, 6.3, 6.4_

- [ ]* 2.1 Écrire des tests unitaires pour la navigation
  - Tester que `setCurrentIndex(0)` est appelé correctement
  - Tester la gestion d'erreur quand l'index est invalide
  - Tester que les données en mémoire sont préservées après navigation
  - Tester les clics multiples rapides sur le bouton
  - _Exigences: 2.1, 2.2, 2.4, 3.1, 3.4, 6.2, 6.3_

- [x] 3. Intégrer le bouton dans l'onglet Saison Sèche
  - Modifier la méthode `create_formula_dry_tab()` dans `frontend/ui/main_window.py`
  - Appeler `self.create_navigation_button()` pour créer le bouton
  - Ajouter le bouton au layout principal après la zone de résultats (`self.dry_results`)
  - Utiliser `layout.addWidget()` pour positionner le bouton en bas de l'onglet
  - Vérifier visuellement que le bouton s'intègre harmonieusement avec l'interface existante
  - _Exigences: 1.1, 1.2, 1.3, 4.1, 5.1, 5.2, 5.4, 5.5_

- [ ]* 3.1 Écrire des tests d'intégration pour l'onglet Saison Sèche
  - Tester que le bouton est présent dans l'onglet créé
  - Tester que le bouton est positionné après la zone de résultats
  - Tester le workflow complet: charger données → calculer → naviguer → revenir
  - Tester que les résultats de calcul sont préservés après navigation
  - _Exigences: 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.5_

- [x] 4. Intégrer le bouton dans l'onglet Saison Pluies
  - Modifier la méthode `create_formula_rainy_tab()` dans `frontend/ui/main_window.py`
  - Appeler `self.create_navigation_button()` pour créer le bouton
  - Ajouter le bouton au layout principal après la zone de résultats (`self.rainy_results`)
  - Utiliser `layout.addWidget()` pour positionner le bouton en bas de l'onglet
  - Vérifier que le positionnement est cohérent avec l'onglet Saison Sèche
  - _Exigences: 1.1, 1.2, 1.3, 4.1, 5.1, 5.2, 5.4, 5.5, 6.5_

- [ ]* 4.1 Écrire des tests d'intégration pour l'onglet Saison Pluies
  - Tester que le bouton est présent dans l'onglet créé
  - Tester que le bouton est positionné après la zone de résultats
  - Tester le workflow complet: charger données → calculer → naviguer → revenir
  - Tester que les résultats de calcul sont préservés après navigation
  - _Exigences: 1.1, 1.2, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.5, 6.5_

- [ ] 5. Checkpoint - Vérifier l'intégration complète
  - Lancer l'application et vérifier que les deux onglets affichent le bouton
  - Tester la navigation depuis l'onglet Saison Sèche vers l'onglet Données
  - Tester la navigation depuis l'onglet Saison Pluies vers l'onglet Données
  - Vérifier que les données chargées restent en mémoire après navigation
  - Vérifier que les résultats de calcul sont préservés
  - Tester l'accessibilité au clavier (Tab + Enter)
  - Vérifier les effets visuels (hover, pressed)
  - S'assurer qu'il n'y a pas d'erreurs dans la console
  - Demander à l'utilisateur si des questions ou ajustements sont nécessaires

- [ ]* 6. Écrire des tests d'intégration pour la navigation entre onglets
  - Tester la navigation: Saison Sèche → Données → Saison Pluies → Données
  - Tester que les données sont préservées lors de multiples navigations
  - Tester que les paramètres de calcul (k(A), epsilon, année) sont préservés
  - Tester la navigation avec et sans données chargées
  - _Exigences: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 3.5, 6.1, 6.2, 6.5_

- [ ] 7. Tests manuels et raffinement final
  - Effectuer les tests manuels de la checklist d'accessibilité
  - Vérifier le contraste des couleurs pour la conformité WCAG
  - Tester avec un lecteur d'écran si disponible
  - Vérifier que le tooltip s'affiche correctement au survol
  - Tester sur différentes résolutions d'écran
  - Ajuster le style CSS si nécessaire pour améliorer l'apparence
  - Documenter tout comportement inattendu ou limitation découverte
  - _Exigences: 7.1, 7.2, 7.3, 7.4, 7.5_

## Notes

- Les tâches marquées avec `*` sont optionnelles et peuvent être ignorées pour un MVP rapide
- Chaque tâche référence les exigences spécifiques du document requirements.md pour la traçabilité
- Les checkpoints permettent une validation incrémentale de l'implémentation
- Les tests unitaires et d'intégration valident les cas d'usage principaux et les cas limites
- L'implémentation ne modifie pas la logique métier existante des calculs de prédiction
- Les données en mémoire (`self.current_data`, `self.dry_formula_df`, `self.rainy_formula_df`) sont automatiquement préservées lors de la navigation car elles sont des attributs d'instance de `MainWindow`

## Checklist de Tests Manuels

- [ ] Le bouton apparaît dans l'onglet Saison Sèche
- [ ] Le bouton apparaît dans l'onglet Saison Pluies
- [ ] Le bouton a le texte correct: "🔙 Retour au Menu des Phases"
- [ ] Le bouton a la couleur de fond correcte (#6c757d)
- [ ] L'effet hover fonctionne (couleur change à #5a6268)
- [ ] L'effet pressed fonctionne (couleur change à #545b62)
- [ ] Le clic sur le bouton navigue vers l'onglet Données
- [ ] Les données chargées restent en mémoire après navigation
- [ ] Les résultats de calcul restent visibles après navigation
- [ ] La navigation au clavier fonctionne (Tab + Enter)
- [ ] Le tooltip s'affiche au survol
- [ ] Le bouton est visuellement cohérent dans les deux onglets
- [ ] Aucune erreur dans la console lors de la navigation
- [ ] Le contraste de couleur est suffisant pour la lisibilité

## Estimation de l'Effort

- **Tâche 1**: Création du bouton helper - 1 heure
- **Tâche 2**: Handler de navigation - 30 minutes
- **Tâche 3**: Intégration Saison Sèche - 1 heure
- **Tâche 4**: Intégration Saison Pluies - 1 heure
- **Tâche 5**: Checkpoint et vérification - 30 minutes
- **Tâche 6**: Tests d'intégration (optionnel) - 1 heure
- **Tâche 7**: Tests manuels et raffinement - 1 heure

**Total estimé**: 6 heures (4.5 heures sans les tests optionnels)
