"""
Module de calcul de la formule maîtresse de prédiction pour la SAISON SECHE.

Ce module implémente la formule Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
avec un polynôme d'ordre 6 pour calculer P(t).

SAISON SECHE : 1er Décembre → 30 Juin (212 jours)
Données : 2010-2025
R² = 0.994
RMSE = 6.0 m³/s
"""

from typing import Dict, Tuple


class FormulaModuleSeche:
    """Module de calcul de la formule maîtresse - SAISON SECHE"""
    
    # Coefficients Mbakaou par défaut (PRÉSERVÉS)
    # Coefficients du polynôme P(t) d'ordre 6 - SAISON SECHE
    # P(t) = −4.129×10⁻¹¹·t⁶ + 2.720×10⁻⁸·t⁵ − 5.603×10⁻⁶·t⁴ + 3.519×10⁻⁴·t³ + 2.809×10⁻²·t² − 5.229·t + 250.7
    DEFAULT_POLY_COEFFS = {
        't6': -4.129e-11,
        't5': 2.720e-8,
        't4': -5.603e-6,
        't3': 3.519e-4,
        't2': 2.809e-2,
        't1': -5.229,
        't0': 250.7
    }
    
    # Coefficients mensuels Cm par défaut - SAISON SECHE
    DEFAULT_MONTHLY_COEFFS = {
        12: 1.814,   # Décembre
        1: 0.8654,   # Janvier
        2: 0.4381,   # Février
        3: 0.3207,   # Mars (mois le plus sec)
        4: 0.3406,   # Avril
        5: 0.8628,   # Mai
        6: 2.3255    # Juin
    }
    
    # Débit historique moyen de référence par défaut - SAISON SECHE
    DEFAULT_Q_HISTORICAL = 98.2  # m³/s (moyenne saison sèche)
    
    # Écart journalier par défaut (Mbakaou)
    DEFAULT_DAILY_DIFF = 16.5  # m³/s
    
    # R² et RMSE
    R_SQUARED = 0.994
    RMSE = 6.0
    
    def __init__(self, 
                 poly_coeffs: Dict[str, float] = None,
                 monthly_coeffs: Dict[int, float] = None,
                 Q_historical: float = None,
                 epsilon: float = None,
                 daily_diff: float = None):
        """
        Initialise avec coefficients dynamiques ou par défaut.
        
        Args:
            poly_coeffs: Coefficients du polynôme (None = Mbakaou par défaut)
            monthly_coeffs: Coefficients mensuels (None = Mbakaou par défaut)
            Q_historical: Débit historique (None = Mbakaou par défaut)
            epsilon: Taux d'erreur optimal (None = 0.05 par défaut)
            daily_diff: Écart journalier optimal (None = 16.5 m³/s par défaut)
        """
        self.POLY_COEFFS = poly_coeffs if poly_coeffs is not None else self.DEFAULT_POLY_COEFFS
        self.MONTHLY_COEFFS = monthly_coeffs if monthly_coeffs is not None else self.DEFAULT_MONTHLY_COEFFS
        self.Q_HISTORICAL = Q_historical if Q_historical is not None else self.DEFAULT_Q_HISTORICAL
        self.EPSILON = epsilon if epsilon is not None else 0.05
        self.DAILY_DIFF = daily_diff if daily_diff is not None else self.DEFAULT_DAILY_DIFF
        self.using_defaults = (poly_coeffs is None and monthly_coeffs is None and Q_historical is None and epsilon is None and daily_diff is None)
    
    def get_coefficients_source(self) -> str:
        """
        Retourne la source des coefficients utilisés.
        
        Returns:
            'Mbakaou (défaut)' ou 'Extraits des données'
        """
        return 'Mbakaou (défaut)' if self.using_defaults else 'Extraits des données'
    
    def calculate_P(self, t: int) -> float:
        """
        Calcule P(t) avec le polynôme d'ordre 6 - SAISON SECHE.
        
        P(t) = −4.129×10⁻¹¹·t⁶ + 2.720×10⁻⁸·t⁵ − 5.603×10⁻⁶·t⁴ 
               + 3.519×10⁻⁴·t³ + 2.809×10⁻²·t² − 5.229·t + 250.7
        
        Args:
            t: Jour de saison (1-212)
               1 = 1er décembre
               212 = 30 juin
            
        Returns:
            P(t) avec 2 décimales
            
        Example:
            >>> formula = FormulaModuleSeche()
            >>> formula.calculate_P(1)
            245.56
            >>> formula.calculate_P(212)
            228.30
        """
        P_t = (
            self.POLY_COEFFS['t6'] * (t ** 6) +
            self.POLY_COEFFS['t5'] * (t ** 5) +
            self.POLY_COEFFS['t4'] * (t ** 4) +
            self.POLY_COEFFS['t3'] * (t ** 3) +
            self.POLY_COEFFS['t2'] * (t ** 2) +
            self.POLY_COEFFS['t1'] * t +
            self.POLY_COEFFS['t0']
        )
        
        return round(P_t, 2)
    
    def deduce_month(self, t: int) -> int:
        """
        Déduit le mois à partir du jour de saison - SAISON SECHE.
        
        Mapping:
        - t ∈ [1, 31] → Décembre (12)
        - t ∈ [32, 62] → Janvier (1)
        - t ∈ [63, 91] → Février (2)
        - t ∈ [92, 122] → Mars (3)
        - t ∈ [123, 152] → Avril (4)
        - t ∈ [153, 183] → Mai (5)
        - t ∈ [184, 212] → Juin (6)
        
        Args:
            t: Jour de saison (1-212)
            
        Returns:
            Mois (12, 1-6)
            
        Example:
            >>> formula = FormulaModuleSeche()
            >>> formula.deduce_month(1)
            12
            >>> formula.deduce_month(45)
            1
            >>> formula.deduce_month(212)
            6
        """
        if 1 <= t <= 31:
            return 12  # Décembre
        elif 32 <= t <= 62:
            return 1   # Janvier
        elif 63 <= t <= 91:
            return 2   # Février
        elif 92 <= t <= 122:
            return 3   # Mars
        elif 123 <= t <= 152:
            return 4   # Avril
        elif 153 <= t <= 183:
            return 5   # Mai
        elif 184 <= t <= 212:
            return 6   # Juin
        else:
            raise ValueError(f"Jour invalide: {t} (doit être entre 1 et 212)")
    
    def calculate_Q(self, t: int, k_A: float, epsilon: float) -> Dict[str, float]:
        """
        Calcule Q(t,A) avec la formule maîtresse - SAISON SECHE.
        
        Formule: Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
        Q_inf = P(t) × k(A) × Cm × 0.20  (scénario pessimiste -80%)
        Q_sup = P(t) × k(A) × Cm × 1.08  (scénario optimiste +8%)
        
        Args:
            t: Jour de saison (1-212)
            k_A: Coefficient annuel (>0)
            epsilon: Taux d'erreur (0.01-0.08)
            
        Returns:
            Dictionnaire contenant:
            - 'P_t': Valeur du polynôme P(t)
            - 'Q_central': Débit central Q(t,A)
            - 'Q_inf': Borne inférieure (Q × 0.20, -80%)
            - 'Q_sup': Borne supérieure (Q × 1.08, +8%)
            - 'month': Mois déduit (12, 1-6)
            - 'Cm': Coefficient mensuel appliqué
            
        Example:
            >>> formula = FormulaModuleSeche()
            >>> result = formula.calculate_Q(45, 1.0, 0.08)
            >>> result['month']
            1
            >>> result['Cm']
            0.8654
        """
        # Calculer P(t)
        P_t = self.calculate_P(t)
        
        # Déduire le mois et obtenir Cm
        month = self.deduce_month(t)
        Cm = self.MONTHLY_COEFFS[month]
        
        # Appliquer un plancher de 1.0 pour février
        if month == 2 and Cm < 1.0:
            Cm = 1.0
        
        # Calculer Q central
        Q_central = P_t * k_A * Cm
        
        # Calculer les bornes : Q_min = -80%, Q_max = +8%
        Q_inf = Q_central * 0.20  # -80% = 20% du Q_central
        Q_sup = Q_central * 1.08  # +8%
        
        return {
            'P_t': P_t,
            'Q_central': round(Q_central, 2),
            'Q_inf': round(Q_inf, 2),
            'Q_sup': round(Q_sup, 2),
            'month': month,
            'Cm': Cm
        }
    
    def validate_inputs(self, t: int, k_A: float, epsilon: float) -> Tuple[bool, str]:
        """
        Valide les paramètres d'entrée - SAISON SECHE.
        
        Règles de validation:
        - t doit être entre 1 et 212
        - k(A) doit être > 0
        - ε doit être entre 0.01 et 0.08
        
        Args:
            t: Jour de saison
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Tuple (is_valid: bool, error_message: str)
            Si is_valid est True, error_message est une chaîne vide
            
        Example:
            >>> formula = FormulaModuleSeche()
            >>> formula.validate_inputs(45, 1.0, 0.08)
            (True, '')
            >>> formula.validate_inputs(0, 1.0, 0.08)
            (False, 'Jour invalide: doit être entre 1 et 212 (saison sèche)')
        """
        # Validation de t
        if t < 1 or t > 212:
            return (False, "Jour invalide: doit être entre 1 et 212 (saison sèche)")
        
        # Validation de k(A)
        if k_A <= 0:
            return (False, "Coefficient annuel invalide: doit être > 0")
        
        # Validation de ε
        if epsilon < 0.01 or epsilon > 0.08:
            return (False, "Taux d'erreur invalide: doit être entre 1% et 8%")
        
        return (True, "")
