# Calcul Normal des Coefficients Mensuels - Restauré

## Méthode de Calcul

Les coefficients mensuels Cm sont maintenant calculés **directement à partir de vos données réelles**, sans aucune amplification ou ajustement:

```
Cm = Q̄_mois / Q̄_saison
```

Où:
- `Q̄_mois` = Moyenne des débits pour le mois
- `Q̄_saison` = Moyenne des débits pour toute la saison

## Coefficients Extraits (Bamendji - Saison Sèche)

Basés sur 15 années hydrologiques (2010-2011 à 2024-2025):

| Mois | Q moyen (m³/s) | Cm calculé |
|------|----------------|------------|
| **Janvier** | 146.46 | **2.3755** (max) |
| Décembre | 116.81 | 1.8947 |
| Février | 98.63 | 1.5998 |
| Mars | 30.03 | 0.4871 |
| Avril | 13.37 | 0.2168 |
| Juin | 14.55 | 0.2360 |
| Mai | 11.87 | 0.1925 (min) |

**Moyenne saisonnière**: 61.65 m³/s

## Interprétation Hydrologique

Vos données de Bamendji montrent un pattern différent de Mbakaou:

### Bamendji (vos données)
- **Janvier** a le coefficient le plus élevé (2.3755)
- **Mai** a le coefficient le plus bas (0.1925)
- Pattern: Décembre-Janvier élevés → Décrue progressive → Étiage en mai

### Mbakaou (référence)
- **Juin** a le coefficient le plus élevé (2.3255)
- **Mars** a le coefficient le plus bas (0.3207)
- Pattern: Décembre élevé → Étiage mars-avril → Remontée en juin

**Conclusion**: Les deux sites ont des comportements hydrologiques différents, ce qui est **normal et attendu** car ils représentent des bassins versants différents avec des caractéristiques propres.

## Validation

### Test de Vérification
```bash
python test_calcul_normal.py
```

**Résultat**: ✅ SUCCÈS
- Les coefficients extraits correspondent **exactement** au calcul manuel
- Aucune amplification appliquée
- Calcul normal confirmé

### Comparaison Extrait vs Manuel

| Mois | Extrait | Manuel | Différence |
|------|---------|--------|------------|
| Décembre | 1.8947 | 1.8947 | 0.000000 ✅ |
| Janvier | 2.3755 | 2.3755 | 0.000000 ✅ |
| Février | 1.5998 | 1.5998 | 0.000000 ✅ |
| Mars | 0.4871 | 0.4871 | 0.000000 ✅ |
| Avril | 0.2168 | 0.2168 | 0.000000 ✅ |
| Mai | 0.1925 | 0.1925 | 0.000000 ✅ |
| Juin | 0.2360 | 0.2360 | 0.000000 ✅ |

## Fichiers Modifiés

- **backend/formula/coefficient_extractor.py**:
  - Méthode `extract_monthly_coefficients()` - calcul simple restauré
  - Suppression des méthodes `_adjust_dry_season_coefficients()` et `_adjust_rainy_season_coefficients()`

## Impact sur l'Application

Après redémarrage de l'application, les coefficients affichés seront:

1. **Phase 1 (Formule Maîtresse)**: Coefficients de Bamendji (janvier max)
2. **Phase 3 (Calculateur)**: Coefficients de Bamendji
3. **Phase 4 (Tableau Complet)**: Coefficients de Bamendji
4. **Phase 5 (Analyse Comparative)**: Coefficients de Bamendji

## Prochaines Étapes

1. ✅ **Cache nettoyé**
2. **Redémarrer l'application**: `python phase2_prediction.py`
3. **Charger le fichier**: "saison_seche bamendji.xlsx"
4. **Tester les phases**: Vérifier que les coefficients reflètent vos données

## Notes Importantes

- ✅ **Calcul direct**: Cm = Q̄_mois / Q̄_saison
- ✅ **Aucune amplification**: Les valeurs reflètent exactement vos données
- ✅ **Spécifique à Bamendji**: Les coefficients sont propres à votre site
- ✅ **Différent de Mbakaou**: C'est normal, chaque site a ses caractéristiques

## Comparaison Bamendji vs Mbakaou

| Mois | Bamendji | Mbakaou | Observation |
|------|----------|---------|-------------|
| Décembre | 1.8947 | 1.8140 | Similaire |
| Janvier | **2.3755** | 0.8654 | Bamendji beaucoup plus élevé |
| Février | 1.5998 | 0.4381 | Bamendji beaucoup plus élevé |
| Mars | 0.4871 | 0.3207 | Similaire |
| Avril | 0.2168 | 0.3406 | Similaire |
| Mai | 0.1925 | 0.8628 | Mbakaou plus élevé |
| Juin | 0.2360 | **2.3255** | Mbakaou beaucoup plus élevé |

**Interprétation**: 
- Bamendji: Influence forte de la saison des pluies en janvier-février
- Mbakaou: Remontée marquée en juin (transition vers saison pluies)
- Les deux patterns sont valides pour leurs sites respectifs
