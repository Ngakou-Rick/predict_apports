"""
Module de calcul pour un jour unique.

Ce module permet de calculer rapidement les débits pour un jour spécifique
avec déduction automatique du mois et du coefficient mensuel.
"""

from datetime import datetime, timedelta
from typing import Dict
from backend.formula.formula_module import FormulaModule


class CalculatorModule:
    """Module de calcul pour un jour unique"""
    
    def __init__(self, formula_module: FormulaModule = None):
        """
        Initialise le calculateur
        
        Args:
            formula_module: Instance de FormulaModule (créée si None)
        """
        self.formula = formula_module if formula_module else FormulaModule()
    
    def calculate_single_day(self, t: int, k_A: float, epsilon: float, year: int = None, start_date: datetime = None) -> Dict:
        """
        Calcule les débits pour un jour spécifique
        
        Args:
            t: Jour de saison (1-153)
            k_A: Coefficient annuel
            epsilon: Taux d'erreur (0.01-0.08)
            year: Année de prédiction (optionnel, défaut: année courante)
            start_date: Date de début (optionnel, si fourni, remplace year)
            
        Returns:
            {
                't': int,
                'date': datetime,
                'month': str,
                'P_t': float,
                'Q_central': float,
                'Q_min': float,
                'Q_max': float,
                'Cm': float
            }
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        # Valider les entrées
        is_valid, error_msg = self.formula.validate_inputs(t, k_A, epsilon)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Calculer avec la formule
        result = self.formula.calculate_Q(t, k_A, epsilon)
        
        # Calculer la date
        if start_date is not None:
            date = start_date + timedelta(days=t - 1)
        elif year is None:
            year = datetime.now().year
            date = self._calculate_date(t, year)
        else:
            date = self._calculate_date(t, year)
        
        # Obtenir le nom du mois
        month_names = {
            7: 'Juillet',
            8: 'Août',
            9: 'Septembre',
            10: 'Octobre',
            11: 'Novembre'
        }
        month_name = month_names[result['month']]
        
        return {
            't': t,
            'date': date,
            'month': month_name,
            'P_t': result['P_t'],
            'Q_central': result['Q_central'],
            'Q_min': result['Q_inf'],
            'Q_max': result['Q_sup'],
            'Cm': result['Cm']
        }
    
    def format_results(self, results: Dict) -> str:
        """
        Formate les résultats pour affichage
        
        Args:
            results: Dictionnaire retourné par calculate_single_day
            
        Returns:
            Chaîne formatée pour affichage
        """
        date_str = results['date'].strftime('%d/%m/%Y')
        
        output = f"""
╔══════════════════════════════════════════════════════════╗
║           CALCUL DE DÉBIT POUR UN JOUR UNIQUE            ║
╠══════════════════════════════════════════════════════════╣
║ Jour de saison (t)    : {results['t']:>3d}                          ║
║ Date                  : {date_str}                      ║
║ Mois                  : {results['month']:<15}              ║
║ Coefficient mensuel   : {results['Cm']:.3f}                        ║
╠══════════════════════════════════════════════════════════╣
║ P(t)                  : {results['P_t']:>8.2f} m³/s                  ║
║ Q centrale            : {results['Q_central']:>8.2f} m³/s                  ║
║ Q min (-8%)           : {results['Q_min']:>8.2f} m³/s                  ║
║ Q max (+19%)          : {results['Q_max']:>8.2f} m³/s                  ║
╚══════════════════════════════════════════════════════════╝
"""
        return output
    
    def _calculate_date(self, t: int, year: int) -> datetime:
        """
        Calcule la date à partir du jour de saison
        
        Args:
            t: Jour de saison (1-153)
            year: Année
            
        Returns:
            Date correspondante
        """
        # 1er juillet = jour 1
        start_date = datetime(year, 7, 1)
        date = start_date + timedelta(days=t - 1)
        return date
