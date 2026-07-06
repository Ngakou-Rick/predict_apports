"""
Textes d'aide pour les 5 phases de prédiction
"""

HELP_TEXTS = {
    1: {
        'title': 'Phase 1: Formule Maîtresse',
        'content': """
<h2>📐 Phase 1: Formule Maîtresse</h2>

<h3>Description</h3>
<p>Cette phase permet de calculer les débits prédits avec la formule maîtresse:</p>
<p><b>Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]</b></p>

<h3>Paramètres</h3>

<h4>Coefficient annuel k(A)</h4>
<ul>
<li><b>Définition:</b> k(A) = Q̄_année / Q̄_historique (739 m³/s)</li>
<li><b>Signification:</b> Représente l'humidité relative de l'année</li>
<li><b>Valeurs typiques:</b>
  <ul>
    <li>k(A) > 1.2: Année très humide</li>
    <li>1.1 < k(A) ≤ 1.2: Année humide</li>
    <li>0.9 ≤ k(A) ≤ 1.1: Année normale</li>
    <li>0.8 ≤ k(A) < 0.9: Année sèche</li>
    <li>k(A) < 0.8: Année très sèche</li>
  </ul>
</li>
<li><b>Exemple:</b> Pour une année avec Q̄ = 850 m³/s, k(A) = 850/739 = 1.150 (année humide)</li>
</ul>

<h4>Taux d'erreur ε</h4>
<ul>
<li><b>Définition:</b> Marge d'erreur appliquée à toute la saison</li>
<li><b>Plage valide:</b> 1% à 8% (0.01 à 0.08)</li>
<li><b>Valeur recommandée:</b> 5% (0.05)</li>
<li><b>Utilisation:</b> Permet de calculer les bornes Q_min et Q_max</li>
</ul>

<h3>Formule Complète</h3>
<p><b>Polynôme P(t):</b></p>
<p>P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴ − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2</p>
<p><b>R² = 0.988</b> (excellente précision)</p>

<h3>Coefficients Mensuels (Cm)</h3>
<ul>
<li>Juillet: 0.697</li>
<li>Août: 1.011</li>
<li>Septembre: 1.300</li>
<li>Octobre: 1.333</li>
<li>Novembre: 0.658</li>
</ul>

<h3>Bornes de Calcul</h3>
<ul>
<li><b>Q_inf:</b> P(t) × k(A) × Cm × 0.92 (borne inférieure -8%)</li>
<li><b>Q_sup:</b> P(t) × k(A) × Cm × 1.19 (borne supérieure +19%)</li>
</ul>
"""
    },
    
    2: {
        'title': 'Phase 2: Coefficients',
        'content': """
<h2>📊 Phase 2: Coefficients Annuels, Mensuels et Polynomiaux</h2>

<h3>Description</h3>
<p>Cette phase affiche trois tableaux contenant tous les coefficients utilisés dans la formule de prédiction.</p>

<h3>Tableau A: Coefficients Annuels</h3>
<p>Affiche les coefficients k(A) pour chaque année présente dans vos données historiques.</p>

<h4>Colonnes:</h4>
<ul>
<li><b>Année:</b> Année hydrologique</li>
<li><b>k(A):</b> Coefficient annuel (Q̄_année / 739)</li>
<li><b>Humidité relative:</b> Pourcentage par rapport à la moyenne historique</li>
<li><b>Q moy:</b> Débit moyen de l'année (m³/s)</li>
<li><b>Rang humidité:</b> Classement de l'année (1 = plus humide)</li>
<li><b>Statut:</b> Qualification (Très humide, Humide, Normal, Sec, Très sec)</li>
</ul>

<h3>Tableau B: Coefficients Mensuels</h3>
<p>Affiche les statistiques pour chaque mois de la saison des pluies.</p>

<h4>Colonnes:</h4>
<ul>
<li><b>Mois:</b> Nom du mois</li>
<li><b>Cm:</b> Coefficient mensuel</li>
<li><b>Q moy:</b> Débit moyen du mois (m³/s)</li>
<li><b>Intervalle P10-P90:</b> Plage de variation (10e et 90e percentiles)</li>
<li><b>Tendance %/j:</b> Variation moyenne quotidienne en pourcentage</li>
<li><b>Succession max ↑/↓:</b> Plus longue série de jours consécutifs en hausse/baisse</li>
</ul>

<h3>Tableau C: Coefficients du Polynôme</h3>
<p>Affiche les coefficients du polynôme P(t) d'ordre 6.</p>

<h4>Colonnes:</h4>
<ul>
<li><b>Terme:</b> Nom du terme (t⁶, t⁵, etc.)</li>
<li><b>Coefficient:</b> Valeur numérique du coefficient</li>
<li><b>Exposant de t:</b> Puissance de t</li>
<li><b>Contribution:</b> Importance relative du terme</li>
</ul>

<p><b>R² = 0.988:</b> Le polynôme explique 98.8% de la variance des débits observés.</p>

<h3>Export</h3>
<p>Vous pouvez exporter les trois tableaux en format Excel pour analyse ultérieure.</p>
"""
    },
    
    3: {
        'title': 'Phase 3: Calculateur',
        'content': """
<h2>🧮 Phase 3: Calculateur de Débit pour un Jour Unique</h2>

<h3>Description</h3>
<p>Cette phase permet de calculer rapidement le débit prédit pour un jour spécifique de la saison des pluies.</p>

<h3>Paramètres d'Entrée</h3>

<h4>Jour de saison (t)</h4>
<ul>
<li><b>Plage valide:</b> 1 à 153</li>
<li><b>Correspondance:</b>
  <ul>
    <li>t = 1: 1er juillet</li>
    <li>t = 31: 31 juillet</li>
    <li>t = 32: 1er août</li>
    <li>t = 153: 30 novembre</li>
  </ul>
</li>
</ul>

<h4>Coefficient annuel k(A)</h4>
<ul>
<li>Voir Phase 1 pour plus de détails</li>
<li><b>Valeur par défaut:</b> 1.0 (année normale)</li>
</ul>

<h4>Taux d'erreur ε</h4>
<ul>
<li>Voir Phase 1 pour plus de détails</li>
<li><b>Valeur par défaut:</b> 0.05 (5%)</li>
</ul>

<h3>Résultats Affichés</h3>
<ul>
<li><b>Date:</b> Date calendaire correspondant au jour t</li>
<li><b>Mois:</b> Mois déduit automatiquement</li>
<li><b>Cm:</b> Coefficient mensuel appliqué</li>
<li><b>P(t):</b> Valeur du polynôme pour le jour t</li>
<li><b>Q centrale:</b> Débit prédit central</li>
<li><b>Q min (-8%):</b> Borne inférieure</li>
<li><b>Q max (+19%):</b> Borne supérieure</li>
<li><b>Statut:</b> Interprétation du débit (Dangereux, Élevé, Normal, Modéré, Bas)</li>
</ul>

<h3>Statuts de Débit</h3>
<ul>
<li>🚨 <b>Dangereux:</b> Q > 1200 m³/s</li>
<li>🔔 <b>Élevé:</b> 900 ≤ Q ≤ 1200 m³/s</li>
<li>✅ <b>Normal:</b> 600 ≤ Q < 900 m³/s</li>
<li>🌤️ <b>Modéré:</b> 400 ≤ Q < 600 m³/s</li>
<li>ℹ️ <b>Bas:</b> Q < 400 m³/s</li>
</ul>

<h3>Performance</h3>
<p>Le calcul est effectué en moins de 100 millisecondes.</p>
"""
    },
    
    4: {
        'title': 'Phase 4: Tableau Complet',
        'content': """
<h2>📋 Phase 4: Tableau Complet de 153 Jours</h2>

<h3>Description</h3>
<p>Cette phase génère un tableau complet avec les prédictions pour tous les jours de la saison des pluies (153 jours).</p>

<h3>Paramètres d'Entrée</h3>
<ul>
<li><b>k(A):</b> Coefficient annuel</li>
<li><b>ε:</b> Taux d'erreur</li>
<li><b>Année:</b> Année de prédiction (pour le calcul des dates)</li>
</ul>

<h3>Colonnes du Tableau</h3>
<ul>
<li><b>t:</b> Jour de saison (1-153)</li>
<li><b>Date:</b> Date calendaire</li>
<li><b>Mois:</b> Nom du mois</li>
<li><b>P(t):</b> Valeur du polynôme</li>
<li><b>Q centrale:</b> Débit prédit central (m³/s)</li>
<li><b>Q min (-8%):</b> Borne inférieure (m³/s)</li>
<li><b>Q max (+19%):</b> Borne supérieure (m³/s)</li>
<li><b>Q réelle:</b> Débit observé (vide initialement, à remplir manuellement)</li>
<li><b>Écart %:</b> Écart entre prédit et observé (calculé si Q réelle fournie)</li>
<li><b>Statut:</b> Interprétation du débit (🚨, 🔔, ✅, 🌤️, ℹ️)</li>
</ul>

<h3>Statuts de Débit</h3>
<ul>
<li>🚨 <b>Dangereux:</b> Q > 1200 m³/s - Risque d'inondation élevé</li>
<li>🔔 <b>Élevé:</b> 900-1200 m³/s - Surveillance accrue recommandée</li>
<li>✅ <b>Normal:</b> 600-900 m³/s - Conditions normales</li>
<li>🌤️ <b>Modéré:</b> 400-600 m³/s - Débit modéré</li>
<li>ℹ️ <b>Bas:</b> < 400 m³/s - Débit faible</li>
</ul>

<h3>Export</h3>
<p>Le tableau peut être exporté en deux formats:</p>
<ul>
<li><b>Excel (.xlsx):</b> Pour analyse et modification dans Excel</li>
<li><b>PDF:</b> Pour impression et partage (inclut un graphique)</li>
</ul>

<p>Les fichiers sont sauvegardés dans le dossier <code>exports/</code> avec le format:</p>
<p><code>predictions_formule_YYYYMMDD_HHMMSS.xlsx</code></p>

<h3>Métadonnées Incluses</h3>
<p>Les exports incluent automatiquement:</p>
<ul>
<li>Valeur de k(A) utilisée</li>
<li>Valeur de ε utilisée</li>
<li>Date et heure de génération</li>
<li>Année de prédiction</li>
</ul>

<h3>Performance</h3>
<p>La génération du tableau de 153 jours prend moins de 500 millisecondes grâce aux calculs vectorisés.</p>
"""
    },
    
    5: {
        'title': 'Phase 5: Analyse Comparative',
        'content': """
<h2>📈 Phase 5: Analyse Comparative Annuelle et Mensuelle</h2>

<h3>Description</h3>
<p>Cette phase affiche deux classements pour identifier les périodes les plus humides et les plus sèches.</p>

<h3>Classement Annuel</h3>
<p>Classe toutes les années présentes dans vos données par ordre d'humidité décroissante.</p>

<h4>Colonnes:</h4>
<ul>
<li><b>Rang:</b> Position dans le classement (1 = année la plus humide)</li>
<li><b>Année:</b> Année hydrologique</li>
<li><b>k(A):</b> Coefficient annuel</li>
<li><b>Q moy:</b> Débit moyen de l'année (m³/s)</li>
<li><b>Qualif.:</b> Qualification de l'année</li>
<li><b>vs Moyenne:</b> Écart par rapport à la moyenne historique (%)</li>
</ul>

<h4>Qualifications:</h4>
<ul>
<li><b>Très humide:</b> k(A) > 1.2 (+20% par rapport à la moyenne)</li>
<li><b>Humide:</b> 1.1 < k(A) ≤ 1.2 (+10% à +20%)</li>
<li><b>Normal:</b> 0.9 ≤ k(A) ≤ 1.1 (-10% à +10%)</li>
<li><b>Sec:</b> 0.8 ≤ k(A) < 0.9 (-20% à -10%)</li>
<li><b>Très sec:</b> k(A) < 0.8 (plus de -20%)</li>
</ul>

<h3>Classement Mensuel</h3>
<p>Classe les 5 mois de la saison des pluies par débit moyen décroissant.</p>

<h4>Colonnes:</h4>
<ul>
<li><b>Rang:</b> Position dans le classement (1 = mois le plus humide)</li>
<li><b>Mois:</b> Nom du mois</li>
<li><b>Q moy:</b> Débit moyen du mois (m³/s)</li>
<li><b>Cm:</b> Coefficient mensuel</li>
<li><b>Tendance %/j:</b> Variation moyenne quotidienne (%)</li>
<li><b>Variabilité CV:</b> Coefficient de variation (écart-type / moyenne × 100)</li>
<li><b>Statut:</b> Interprétation du mois</li>
</ul>

<h4>Coefficient de Variation (CV):</h4>
<ul>
<li><b>CV < 20%:</b> Faible variabilité (débit stable)</li>
<li><b>20% ≤ CV < 40%:</b> Variabilité modérée</li>
<li><b>CV ≥ 40%:</b> Forte variabilité (débit très variable)</li>
</ul>

<h3>Utilisation</h3>
<p>Ces classements permettent de:</p>
<ul>
<li>Identifier les années de référence (très humides ou très sèches)</li>
<li>Comprendre la saisonnalité des débits</li>
<li>Évaluer la variabilité inter-annuelle et intra-annuelle</li>
<li>Choisir des valeurs de k(A) appropriées pour les prédictions</li>
</ul>

<h3>Export</h3>
<p>Les deux classements peuvent être exportés ensemble en format Excel.</p>
"""
    }
}


def get_help_text(phase_number):
    """
    Retourne le texte d'aide pour une phase donnée
    
    Args:
        phase_number: Numéro de la phase (1-5)
        
    Returns:
        dict avec 'title' et 'content' ou None si phase invalide
    """
    return HELP_TEXTS.get(phase_number)
