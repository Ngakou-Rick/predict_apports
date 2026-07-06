"""
Exemple d'utilisation complète des modules de prédiction.

Ce script montre comment utiliser les modules pour les DEUX saisons :
- Saison des pluies (Juillet → Novembre)
- Saison sèche (Décembre → Juin)

IMPORTANT : Les deux saisons sont complètement séparées et indépendantes.
"""

from backend.formula import (
    # Saison des pluies
    FormulaModule,
    CalculatorModule,
    GeneratorModule,
    # Saison sèche
    FormulaModuleSeche,
    CalculatorModuleSeche,
    GeneratorModuleSeche
)


def exemple_saison_pluies():
    """Exemple d'utilisation pour la saison des pluies"""
    print("\n" + "=" * 70)
    print("SAISON DES PLUIES - Juillet → Novembre (153 jours)")
    print("=" * 70)
    
    # 1. Calcul pour un jour unique
    print("\n1️⃣  CALCUL JOUR UNIQUE (15 août - jour 46)")
    print("-" * 70)
    
    calculator = CalculatorModule()
    result = calculator.calculate_single_day(
        t=46,           # 15 août
        k_A=1.0,        # Année normale
        epsilon=0.08,   # ±8%
        year=2025
    )
    
    print(f"Date : {result['date'].strftime('%d/%m/%Y')}")
    print(f"Mois : {result['month']}")
    print(f"Q central : {result['Q_central']} m³/s")
    print(f"Q min : {result['Q_min']} m³/s")
    print(f"Q max : {result['Q_max']} m³/s")
    
    # 2. Génération table complète
    print("\n2️⃣  TABLE COMPLÈTE (153 jours)")
    print("-" * 70)
    
    generator = GeneratorModule()
    df_pluies = generator.generate_full_table(
        k_A=1.0,
        epsilon=0.08,
        year=2025
    )
    
    print(f"Nombre de jours : {len(df_pluies)}")
    print(f"Débit moyen : {df_pluies['Q centrale'].mean():.2f} m³/s")
    print(f"Débit min : {df_pluies['Q centrale'].min():.2f} m³/s")
    print(f"Débit max : {df_pluies['Q centrale'].max():.2f} m³/s")
    
    # 3. Résumé mensuel
    print("\n3️⃣  RÉSUMÉ MENSUEL")
    print("-" * 70)
    
    df_monthly = df_pluies.groupby('Mois').agg({
        'Q centrale': 'mean',
        't': 'count'
    }).round(2)
    df_monthly.columns = ['Q moyen', 'Jours']
    print(df_monthly.to_string())


def exemple_saison_seche():
    """Exemple d'utilisation pour la saison sèche"""
    print("\n" + "=" * 70)
    print("SAISON SÈCHE - Décembre → Juin (212 jours)")
    print("=" * 70)
    
    # 1. Calcul pour un jour unique
    print("\n1️⃣  CALCUL JOUR UNIQUE (15 mars - jour 105)")
    print("-" * 70)
    
    calculator = CalculatorModuleSeche()
    result = calculator.calculate_single_day(
        t=105,          # 15 mars (étiage)
        k_A=1.0,        # Année normale
        epsilon=0.08,   # ±8%
        year=2025
    )
    
    print(f"Date : {result['date'].strftime('%d/%m/%Y')}")
    print(f"Mois : {result['month']}")
    print(f"Q central : {result['Q_central']} m³/s")
    print(f"Q min : {result['Q_min']} m³/s")
    print(f"Q max : {result['Q_max']} m³/s")
    
    # 2. Génération table complète
    print("\n2️⃣  TABLE COMPLÈTE (212 jours)")
    print("-" * 70)
    
    generator = GeneratorModuleSeche()
    df_seche = generator.generate_full_season(
        k_A=1.0,
        epsilon=0.08,
        year=2025
    )
    
    print(f"Nombre de jours : {len(df_seche)}")
    print(f"Débit moyen : {df_seche['Q_central'].mean():.2f} m³/s")
    print(f"Débit min : {df_seche['Q_central'].min():.2f} m³/s")
    print(f"Débit max : {df_seche['Q_central'].max():.2f} m³/s")
    
    # 3. Résumé mensuel
    print("\n3️⃣  RÉSUMÉ MENSUEL")
    print("-" * 70)
    
    df_monthly = generator.generate_monthly_summary(k_A=1.0, epsilon=0.08, year=2025)
    print(df_monthly.to_string(index=False))


def comparaison_saisons():
    """Comparaison entre les deux saisons"""
    print("\n" + "=" * 70)
    print("COMPARAISON SAISON PLUIES vs SAISON SÈCHE")
    print("=" * 70)
    
    # Générer les données pour les deux saisons
    gen_pluies = GeneratorModule()
    gen_seche = GeneratorModuleSeche()
    
    df_pluies = gen_pluies.generate_full_table(k_A=1.0, epsilon=0.08, year=2025)
    df_seche = gen_seche.generate_full_season(k_A=1.0, epsilon=0.08, year=2025)
    
    stats_pluies = {
        'duration_days': len(df_pluies),
        'Q_mean': df_pluies['Q centrale'].mean(),
        'Q_min': df_pluies['Q centrale'].min(),
        'Q_max': df_pluies['Q centrale'].max(),
        'Q_std': df_pluies['Q centrale'].std()
    }
    
    stats_seche = {
        'duration_days': len(df_seche),
        'Q_mean': df_seche['Q_central'].mean(),
        'Q_min': df_seche['Q_central'].min(),
        'Q_max': df_seche['Q_central'].max(),
        'Q_std': df_seche['Q_central'].std()
    }
    
    print("\n📊 STATISTIQUES COMPARATIVES")
    print("-" * 70)
    print(f"{'Caractéristique':<25} {'Saison Pluies':>20} {'Saison Sèche':>20}")
    print("-" * 70)
    print(f"{'Durée (jours)':<25} {stats_pluies['duration_days']:>20} {stats_seche['duration_days']:>20}")
    print(f"{'Débit moyen (m³/s)':<25} {stats_pluies['Q_mean']:>20.2f} {stats_seche['Q_mean']:>20.2f}")
    print(f"{'Débit min (m³/s)':<25} {stats_pluies['Q_min']:>20.2f} {stats_seche['Q_min']:>20.2f}")
    print(f"{'Débit max (m³/s)':<25} {stats_pluies['Q_max']:>20.2f} {stats_seche['Q_max']:>20.2f}")
    print(f"{'Écart-type (m³/s)':<25} {stats_pluies['Q_std']:>20.2f} {stats_seche['Q_std']:>20.2f}")
    print("-" * 70)
    
    # Calcul du ratio
    ratio_moyen = stats_pluies['Q_mean'] / stats_seche['Q_mean']
    print(f"\n💡 Le débit moyen de la saison des pluies est {ratio_moyen:.2f}x celui de la saison sèche")
    
    # Périodes critiques
    print("\n⚠️  PÉRIODES CRITIQUES")
    print("-" * 70)
    print("Saison des pluies : Octobre (débit maximum)")
    print("Saison sèche      : Mars (étiage - débit minimum)")


def exemple_scenarios_multiples():
    """Exemple avec plusieurs scénarios k(A)"""
    print("\n" + "=" * 70)
    print("COMPARAISON DE SCÉNARIOS k(A)")
    print("=" * 70)
    
    scenarios = [
        (0.6, "Très sec"),
        (0.8, "Sec"),
        (1.0, "Normal"),
        (1.2, "Humide"),
        (1.4, "Très humide")
    ]
    
    # Saison sèche - jour d'étiage (jour 110)
    print("\n🌵 SAISON SÈCHE - Jour 110 (mi-mars - étiage)")
    print("-" * 70)
    print(f"{'k(A)':<10} {'Statut':<15} {'Q central (m³/s)':>20}")
    print("-" * 70)
    
    formula_seche = FormulaModuleSeche()
    for k_A, statut in scenarios:
        result = formula_seche.calculate_Q(t=110, k_A=k_A, epsilon=0.08)
        print(f"{k_A:<10.2f} {statut:<15} {result['Q_central']:>20.2f}")
    
    # Saison pluies - pic (jour 100)
    print("\n🌧️  SAISON PLUIES - Jour 100 (mi-octobre - pic)")
    print("-" * 70)
    print(f"{'k(A)':<10} {'Statut':<15} {'Q central (m³/s)':>20}")
    print("-" * 70)
    
    formula_pluies = FormulaModule()
    for k_A, statut in scenarios:
        result = formula_pluies.calculate_Q(t=100, k_A=k_A, epsilon=0.08)
        print(f"{k_A:<10.2f} {statut:<15} {result['Q_central']:>20.2f}")


def exemple_annee_complete():
    """Exemple de prédiction pour une année complète (2 saisons)"""
    print("\n" + "=" * 70)
    print("PRÉDICTION ANNÉE COMPLÈTE 2025-2026")
    print("=" * 70)
    
    k_A = 1.0  # Année normale
    epsilon = 0.08
    
    # Saison des pluies 2025 (juillet-novembre)
    print("\n📅 SAISON DES PLUIES 2025 (Juillet → Novembre)")
    print("-" * 70)
    gen_pluies = GeneratorModule()
    df_pluies = gen_pluies.generate_full_table(k_A=k_A, epsilon=epsilon, year=2025)
    
    print(f"Début : {df_pluies.iloc[0]['Date'].strftime('%d/%m/%Y')}")
    print(f"Fin   : {df_pluies.iloc[-1]['Date'].strftime('%d/%m/%Y')}")
    print(f"Durée : {len(df_pluies)} jours")
    print(f"Q moyen : {df_pluies['Q centrale'].mean():.2f} m³/s")
    
    # Saison sèche 2025-2026 (décembre-juin)
    print("\n📅 SAISON SÈCHE 2025-2026 (Décembre → Juin)")
    print("-" * 70)
    gen_seche = GeneratorModuleSeche()
    df_seche = gen_seche.generate_full_season(k_A=k_A, epsilon=epsilon, year=2025)
    
    print(f"Début : {df_seche.iloc[0]['Date']}")
    print(f"Fin   : {df_seche.iloc[-1]['Date']}")
    print(f"Durée : {len(df_seche)} jours")
    print(f"Q moyen : {df_seche['Q_central'].mean():.2f} m³/s")
    
    # Total année
    print("\n📊 TOTAL ANNÉE HYDROLOGIQUE 2025-2026")
    print("-" * 70)
    total_jours = len(df_pluies) + len(df_seche)
    Q_moyen_annuel = (df_pluies['Q centrale'].sum() + df_seche['Q_central'].sum()) / total_jours
    
    print(f"Durée totale : {total_jours} jours")
    print(f"Q moyen annuel : {Q_moyen_annuel:.2f} m³/s")
    print(f"Q max (pluies) : {df_pluies['Q centrale'].max():.2f} m³/s")
    print(f"Q min (sèche)  : {df_seche['Q_central'].min():.2f} m³/s")


def main():
    """Fonction principale"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "EXEMPLE UTILISATION COMPLÈTE" + " " * 25 + "║")
    print("║" + " " * 10 + "Prédiction Débits - Saisons Pluies & Sèche" + " " * 16 + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Exemples individuels
        exemple_saison_pluies()
        exemple_saison_seche()
        
        # Comparaisons
        comparaison_saisons()
        exemple_scenarios_multiples()
        
        # Année complète
        exemple_annee_complete()
        
        print("\n" + "=" * 70)
        print("✅ TOUS LES EXEMPLES EXÉCUTÉS AVEC SUCCÈS")
        print("=" * 70)
        print("\n💡 Les modules sont prêts à être utilisés dans votre application !")
        print("\n📚 Consultez les fichiers README pour plus d'informations :")
        print("   - backend/formula/README.md (saison pluies)")
        print("   - backend/formula/README_SAISON_SECHE.md (saison sèche)")
        print()
        
    except Exception as e:
        print("\n" + "=" * 70)
        print("❌ ERREUR")
        print("=" * 70)
        print(f"\nErreur : {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
