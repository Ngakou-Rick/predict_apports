# ⚡ Démarrage Rapide - 5 Minutes

## Installation Express

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Tester l'installation
python test_app.py

# 3. Lancer l'application
python main.py
```

## Premier Workflow

### 1️⃣ Charger les Données (30 secondes)
- Cliquez sur **"📁 Charger Données Excel"**
- Sélectionnez votre fichier (ex: `modele test.xlsx`)
- Attendez la confirmation ✅

### 2️⃣ Configurer (15 secondes)
- **Saison**: Choisir "Saison Sèche" ou "Saison des Pluies"
- **Année**: Sélectionner dans la liste
- **Modèle**: Laisser "Random Forest" (recommandé)

### 3️⃣ Analyser (1 minute)
- Cliquez sur **"🔍 Analyser"**
- Consultez l'onglet **"📈 Analyse"**
- Vérifiez les statistiques

### 4️⃣ Prédire (1 minute)
- Cliquez sur **"🎯 Prédire"**
- Consultez l'onglet **"🤖 Prédiction"**
- Vérifiez le R² (> 0.7 = bon modèle)

### 5️⃣ Exporter (30 secondes)
- Onglet **"📤 Export"**
- Cliquez sur **"📊 Exporter vers Excel"** ou **"📄 Exporter vers PDF"**
- Choisissez l'emplacement
- Terminé! 🎉

## Format des Données

Votre fichier Excel doit avoir ces colonnes:

| Date       | Debits | Pluie | Tmax | Tmin | ETP |
|------------|--------|-------|------|------|-----|
| 2020-01-01 | 150.5  | 0.0   | 35.2 | 18.5 | 5.2 |
| 2020-01-02 | 148.3  | 2.5   | 34.8 | 19.0 | 5.0 |

## Interprétation Rapide

### Métriques de Performance
- **R² > 0.9**: Excellent ⭐⭐⭐
- **R² > 0.7**: Bon ⭐⭐
- **R² > 0.5**: Acceptable ⭐
- **R² < 0.5**: À améliorer ⚠️

### Corrélations
- **|r| > 0.7**: Forte relation
- **|r| > 0.4**: Relation modérée
- **|r| < 0.4**: Faible relation

## Résolution Rapide

### ❌ Erreur de chargement
```bash
pip install --upgrade openpyxl pandas
```

### ❌ Interface ne s'affiche pas
```bash
pip install --upgrade PyQt5
```

### ❌ Erreur de prédiction
- Vérifiez qu'il y a au moins 30 jours de données
- Essayez un autre modèle

## Aide Rapide

- 📖 Guide complet: `GUIDE_UTILISATEUR.md`
- 🔧 Installation: `INSTALLATION.md`
- 📚 Documentation: `README.md`

## Raccourcis Clavier

- **Ctrl+O**: Ouvrir fichier
- **Ctrl+S**: Sauvegarder
- **Ctrl+Q**: Quitter

## Conseils Pro

1. **Toujours vérifier** les données avant analyse
2. **Comparer plusieurs modèles** pour choisir le meilleur
3. **Sauvegarder régulièrement** vos exports
4. **Documenter** vos analyses

---

**Prêt à commencer? Lancez `python main.py` ! 🚀**
