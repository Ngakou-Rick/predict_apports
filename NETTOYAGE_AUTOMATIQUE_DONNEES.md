# NETTOYAGE AUTOMATIQUE DES DONNÉES

## ✅ Fonctionnalité implémentée

Tous les fichiers Excel uploadés dans l'application sont **automatiquement nettoyés** lors du chargement.

## 📋 Opérations de nettoyage appliquées

### 1. Normalisation des noms de colonnes
- Conversion en minuscules
- Suppression des espaces en début/fin
- Exemple: `"  DEBIT  "` → `"debit"`

### 2. Nettoyage de la colonne débit
- Remplacement des valeurs non-numériques par NaN:
  - `"-"`, `"--"`, `"---"`
  - `"N/A"`, `"NA"`
  - Espaces vides `""`, `" "`
- Conversion en type numérique (float64)
- Création de la colonne standard `"debits"`

### 3. Traitement de la colonne date
- Conversion en format datetime
- Gestion des erreurs de format
- Renommage en `"date"` (standard)

### 4. Suppression des lignes invalides
- Lignes avec date manquante
- Lignes avec débit manquant
- Tri par date croissante

## 🎯 Fichier modifié

**`backend/data_processing/seasonal_transformer.py`**

Méthode: `load_data(file_path: str)`

```python
def load_data(self, file_path: str) -> pd.DataFrame:
    """
    Charge les données depuis un fichier Excel avec nettoyage automatique
    
    Nettoyage appliqué:
    - Normalisation des noms de colonnes (minuscules, espaces supprimés)
    - Remplacement des valeurs non-numériques ('-', 'N/A', etc.) par NaN
    - Conversion des colonnes numériques
    - Suppression des lignes avec valeurs manquantes critiques
    """
```

## 📊 Exemple de résultat

### Avant nettoyage (fichier original)
```
date        debit
2015-01-01  9.30679
2015-01-02  -
2015-01-03  21.200887
2015-01-04  N/A
```

### Après nettoyage automatique
```
date        debits
2015-01-01  9.31
2015-01-03  21.20
```

**Résultat:**
- Lignes avec `-` et `N/A` supprimées
- Colonne renommée en `debits`
- Valeurs converties en float

## ✅ Tests effectués

### Test 1: Fichier avec valeurs non-numériques
```
Fichier: saison_sechemapé.xlsx (contient des '-')
Résultat: 
  - 17 lignes avec '-' supprimées
  - 2318 lignes valides conservées
  - Toutes les valeurs sont numériques ✅
```

### Test 2: Extraction des coefficients
```
Après nettoyage automatique:
  - Q_historical: 39.50 m³/s
  - R²: 0.9215
  - Score qualité: 85/100
  - 12 années de données ✅
```

### Test 3: Comparaison avec fichier pré-nettoyé
```
Fichier original (auto-nettoyé): 2318 lignes
Fichier pré-nettoyé:             2318 lignes
Différence:                      0 lignes ✅
```

## 🔄 Utilisation dans l'application

### Via ApplicationController
```python
from backend.core.application_controller import ApplicationController

controller = ApplicationController()

# Le nettoyage est automatique lors du chargement
result = controller.load_and_transform_data("votre_fichier.xlsx")

# Les données sont déjà nettoyées
if result['success']:
    # Extraction des coefficients avec données propres
    dry_coeffs = controller.dry_coefficients
    rainy_coeffs = controller.rainy_coefficients
```

### Via SeasonalTransformer directement
```python
from backend.data_processing.seasonal_transformer import SeasonalTransformer

transformer = SeasonalTransformer()

# Chargement avec nettoyage automatique
df = transformer.load_data("fichier_avec_erreurs.xlsx")

# Les données sont propres
print(df['debits'].dtype)  # float64
print(df['debits'].isna().sum())  # 0
```

## 💡 Avantages

1. **Pas de préparation manuelle** : Les utilisateurs peuvent uploader directement leurs fichiers
2. **Robustesse** : Gère automatiquement les erreurs de saisie courantes
3. **Cohérence** : Tous les fichiers sont traités de la même manière
4. **Qualité** : Garantit que seules des données valides sont utilisées pour les calculs

## ⚠️ Points d'attention

### Colonnes requises
Le fichier Excel doit contenir au minimum:
- Une colonne de **date** (détectée automatiquement)
- Une colonne de **débit** (détectée automatiquement)

### Formats acceptés
- **Date**: Tout format reconnu par pandas (DD/MM/YYYY, YYYY-MM-DD, etc.)
- **Débit**: Nombres décimaux (avec `.` ou `,`)

### Données supprimées
Les lignes suivantes sont automatiquement supprimées:
- Date manquante ou invalide
- Débit manquant ou non-numérique

## ✅ Conclusion

Le nettoyage automatique est **actif et fonctionnel** pour tous les fichiers uploadés dans l'application. Les utilisateurs n'ont plus besoin de nettoyer manuellement leurs données avant de les charger.

**Tous les fichiers Excel uploadés bénéficient automatiquement de ce nettoyage !** 🎉
