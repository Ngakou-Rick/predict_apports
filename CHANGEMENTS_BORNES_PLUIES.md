# Changements appliqués : Bornes fixes -8%/+19% pour saison des pluies

## ✅ MODIFICATIONS BACKEND TERMINÉES

### 1. `backend/formula/formula_module.py`
- ✅ Méthode `calculate_Q()` : Bornes fixes Q_min = Q × 0.92 (-8%), Q_max = Q × 1.19 (+19%)
- ✅ Méthode `validate_inputs()` : Paramètre epsilon optionnel, pas de validation

### 2. `backend/formula/generator_module.py`
- ✅ Labels colonnes : "Q min (-8%)" et "Q max (+19%)"
- ✅ Validation : Appel sans epsilon

## ⚠️ MODIFICATIONS INTERFACE À FAIRE MANUELLEMENT

### Phase 1 (`show_phase1_formula_master`)
**Ligne ~1290** : Ajouter condition pour cacher le champ ε si season == 'rainy'

```python
# Champ ε - SEULEMENT pour saison sèche
if season == 'dry':
    spin_epsilon = QDoubleSpinBox()
    spin_epsilon.setMinimum(0.01)
    spin_epsilon.setMaximum(0.08)
    spin_epsilon.setValue(0.05)
    spin_epsilon.setDecimals(2)
    spin_epsilon.setSingleStep(0.01)
    spin_epsilon.setToolTip("Taux d'erreur ε entre 1% et 8%")
    form_layout.addRow("Taux d'erreur ε:", spin_epsilon)
else:
    # Saison des pluies : bornes fixes -8%/+19%, pas de saisie ε
    label_bornes = QLabel("Bornes fixes: -8% / +19%")
    label_bornes.setStyleSheet("color: #28a745; font-weight: bold;")
    form_layout.addRow("Bornes:", label_bornes)
    spin_epsilon = None  # Pas de champ epsilon
```

**Ligne ~1360** : Modifier la fonction `calculate()` pour gérer epsilon = None

```python
def calculate():
    try:
        k_A = spin_k_A.value()
        
        # Pour saison sèche : utiliser epsilon saisi
        # Pour saison des pluies : epsilon ignoré (bornes fixes)
        if season == 'dry':
            epsilon = spin_epsilon.value()
        else:
            epsilon = 0.08  # Valeur par défaut (ignorée dans calculate_Q)
        
        # Valider les entrées
        if season == 'dry':
            is_valid, error_msg = formula.validate_inputs(1, k_A, epsilon)
        else:
            is_valid, error_msg = formula.validate_inputs(1, k_A)
        
        # ... reste du code
```

### Phase 3 (`show_phase3_calculator`)
**Ligne ~1750** : Même modification que Phase 1

### Phase 4 (`show_phase4_full_table`)
**Ligne ~1970** : Même modification que Phase 1

## 📝 NOTES IMPORTANTES

1. **Saison sèche** : Pas de changement, ε reste variable (0.01-0.08)
2. **Saison des pluies** : Bornes fixes -8%/+19%, champ ε caché
3. **Validation** : epsilon optionnel dans validate_inputs()
4. **Calcul** : Les bornes sont toujours -8%/+19% pour saison des pluies

## 🧪 TESTS À EFFECTUER

1. ✅ Charger "saison_seche bamendji.xlsx"
2. ✅ Phase 1/3/4 saison sèche → Champ ε visible, bornes variables
3. ✅ Phase 1/3/4 saison des pluies → Message d'erreur (pas de données)
4. ⏳ Charger fichier saison des pluies
5. ⏳ Phase 1/3/4 saison des pluies → Champ ε caché, bornes fixes -8%/+19%
