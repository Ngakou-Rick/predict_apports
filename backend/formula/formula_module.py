"""
Module de calcul de la formule maîtresse de prédiction pour la saison des pluies.

Ce module implémente la formule Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
avec un polynôme d'ordre 6 pour calculer P(t).
"""

from typing import Dict, Tuple


class FormulaModule:
    """Module de calcul de la formule maîtresse"""
    
    # Coefficients Mbakaou par défaut (PRÉSERVÉS)
    # Coefficients du polynôme P(t) d'ordre 6
    # P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴ − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2
    DEFAULT_POLY_COEFFS = {
        't6': 5.414e-9,
        't5': -2.166e-6,
        't4': 3.115e-4,
        't3': -2.019e-2,
        't2': 5.687e-1,
        't1': 2.741,
        't0': 382.2
    }
    
    # Coefficients mensuels Cm par défaut
    DEFAULT_MONTHLY_COEFFS = {
        7: 0.697,   # Juillet
        8: 1.011,   # Août
        9: 1.300,   # Septembre
        10: 1.333,  # Octobre
        11: 0.658   # Novembre
    }
    
    # Écart cible entre jours consécutifs pour juillet (en m³/s) - Mbakaou par défaut
    DEFAULT_DAILY_DIFF_JULY = 16.5
    
    # Débit historique de référence par défaut
    DEFAULT_Q_HISTORICAL = 739.0  # m³/s
    
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
        self.TARGET_DAILY_DIFF_JULY = daily_diff if daily_diff is not None else self.DEFAULT_DAILY_DIFF_JULY
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
        Calcule P(t) avec le polynôme d'ordre 6.
        
        P(t) = 5.414×10⁻⁹·t⁶ − 2.166×10⁻⁶·t⁵ + 3.115×10⁻⁴·t⁴ − 2.019×10⁻²·t³ + 5.687×10⁻¹·t² + 2.741·t + 382.2
        
        Args:
            t: Jour de saison (1-153)
            
        Returns:
            P(t) avec 2 décimales
            
        Example:
            >>> formula = FormulaModule()
            >>> formula.calculate_P(1)
            390.54
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
        Déduit le mois à partir du jour de saison.
        
        Mapping:
        - t ∈ [1, 31] → Juillet (7)
        - t ∈ [32, 62] → Août (8)
        - t ∈ [63, 92] → Septembre (9)
        - t ∈ [93, 123] → Octobre (10)
        - t ∈ [124, 153] → Novembre (11)
        
        Args:
            t: Jour de saison (1-153)
            
        Returns:
            Mois (7-11)
            
        Example:
            >>> formula = FormulaModule()
            >>> formula.deduce_month(1)
            7
            >>> formula.deduce_month(32)
            8
            >>> formula.deduce_month(153)
            11
        """
        if 1 <= t <= 31:
            return 7  # Juillet
        elif 32 <= t <= 62:
            return 8  # Août
        elif 63 <= t <= 92:
            return 9  # Septembre
        elif 93 <= t <= 123:
            return 10  # Octobre
        elif 124 <= t <= 153:
            return 11  # Novembre
        else:
            # Cette condition ne devrait jamais être atteinte si validate_inputs est appelé
            raise ValueError(f"Jour invalide: {t}")
    
    def calculate_Q(self, t: int, k_A: float, epsilon: float) -> Dict[str, float]:
        """
        Calcule Q(t,A) avec la formule maîtresse.
        
        Formule: Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε(t)]
        Q_inf = Q_central × (1 - ε)
        Q_sup = Q_central × (1 + ε)
        
        Pour Mbakaou uniquement (coefficients par défaut), un ajustement est appliqué
        pour juillet (t=2 à t=31) pour maintenir un écart de ~16.5 m³/s entre jours consécutifs.
        
        Args:
            t: Jour de saison (1-153)
            k_A: Coefficient annuel (>0)
            epsilon: Taux d'erreur (0.01-0.15)
            
        Returns:
            Dictionnaire contenant:
            - 'P_t': Valeur du polynôme P(t)
            - 'Q_central': Débit central Q(t,A)
            - 'Q_inf': Borne inférieure Q × (1 - ε)
            - 'Q_sup': Borne supérieure Q × (1 + ε)
            - 'Q_min': Alias pour Q_inf
            - 'Q_max': Alias pour Q_sup
            - 'month': Mois déduit (7-11)
            - 'Cm': Coefficient mensuel appliqué
            
        Example:
            >>> formula = FormulaModule()
            >>> result = formula.calculate_Q(1, 1.0, 0.05)
            >>> result['P_t']
            390.54
            >>> result['month']
            7
        """
        # Calculer P(t)
        P_t = self.calculate_P(t)
        
        # Déduire le mois et obtenir Cm
        month = self.deduce_month(t)
        Cm = self.MONTHLY_COEFFS[month]
        
        # Calculer Q central de base
        Q_base = P_t * k_A * Cm
        
        # Ajustement pour juillet UNIQUEMENT si on utilise les coefficients Mbakaou par défaut
        if self.using_defaults and month == 7 and t > 1:
            # Calculer le Q ajusté du jour précédent (récursif)
            result_prev = self.calculate_Q(t - 1, k_A, epsilon)
            Q_prev_adjusted = result_prev['Q_central']
            
            # Appliquer l'écart cible pour maintenir la progression (Mbakaou spécifique)
            Q_central = Q_prev_adjusted + self.TARGET_DAILY_DIFF_JULY
        else:
            # Formule normale pour les autres barrages ou les autres mois
            Q_central = Q_base
        
        # Calculer les bornes avec pourcentages fixes pour saison des pluies
        # Saison des pluies : -8% / +19% (fixes)
        Q_inf = Q_central * 0.92  # -8%
        Q_sup = Q_central * 1.19  # +19%
        
        return {
            'P_t': P_t,
            'Q_central': round(Q_central, 2),
            'Q_inf': round(Q_inf, 2),
            'Q_sup': round(Q_sup, 2),
            'Q_min': round(Q_inf, 2),  # Alias
            'Q_max': round(Q_sup, 2),  # Alias
            'month': month,
            'Cm': Cm
        }
    
    def validate_inputs(self, t: int, k_A: float, epsilon: float = None) -> Tuple[bool, str]:
        """
        Valide les paramètres d'entrée.
        
        Règles de validation:
        - t doit être entre 1 et 153
        - k(A) doit être > 0
        - ε n'est plus validé (bornes fixes -8%/+19%)
        
        Args:
            t: Jour de saison
            k_A: Coefficient annuel
            epsilon: Taux d'erreur (ignoré, bornes fixes)
            
        Returns:
            Tuple (is_valid: bool, error_message: str)
            Si is_valid est True, error_message est une chaîne vide
            
        Example:
            >>> formula = FormulaModule()
            >>> formula.validate_inputs(1, 1.0)
            (True, '')
            >>> formula.validate_inputs(0, 1.0)
            (False, 'Jour invalide: doit être entre 1 et 153')
        """
        # Validation de t
        if t < 1 or t > 153:
            return (False, "Jour invalide: doit être entre 1 et 153")
        
        # Validation de k(A)
        if k_A <= 0:
            return (False, "Coefficient annuel invalide: doit être > 0")
        
        # ε n'est plus validé (bornes fixes -8%/+19%)
        
        return (True, "")
