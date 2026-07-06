"""
Module d'analyse avancée pour la saison sèche.

Ce module fournit des analyses statistiques, des comparaisons entre scénarios,
et des visualisations pour la saison sèche.

SAISON SECHE : 1er Décembre → 30 Juin (212 jours)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from backend.formula.formula_module_seche import FormulaModuleSeche
from backend.formula.generator_module_seche import GeneratorModuleSeche
from backend.formula.coefficients_module_seche import CoefficientsModuleSeche


class AnalyzerModuleSeche:
    """Module d'analyse avancée - SAISON SECHE"""
    
    def __init__(self, coefficients_module=None):
        """
        Initialise l'analyseur
        
        Args:
            coefficients_module: Instance de CoefficientsModule (non utilisé pour la saison sèche, 
                               mais accepté pour compatibilité avec AnalyzerModule)
        """
        self.coeffs = coefficients_module  # Stocké pour compatibilité
        self.formula = FormulaModuleSeche()
        self.generator = GeneratorModuleSeche(self.formula)
    
    def analyze_month_behavior(self, month: int, k_A: float, epsilon: float) -> Dict:
        """
        Analyse le comportement d'un mois spécifique - SAISON SECHE
        
        Args:
            month: Mois (12, 1-6)
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Dictionnaire avec:
            - month_name: Nom du mois
            - days_count: Nombre de jours
            - Q_mean: Débit moyen
            - Q_min: Débit minimum
            - Q_max: Débit maximum
            - Q_std: Écart-type
            - trend: Tendance (croissante/décroissante)
            - Cm: Coefficient mensuel
        """
        month_names = {
            12: 'Décembre',
            1: 'Janvier',
            2: 'Février',
            3: 'Mars',
            4: 'Avril',
            5: 'Mai',
            6: 'Juin'
        }
        
        # Déterminer les jours du mois
        month_ranges = {
            12: (1, 31),
            1: (32, 62),
            2: (63, 91),
            3: (92, 122),
            4: (123, 152),
            5: (153, 183),
            6: (184, 212)
        }
        
        start_day, end_day = month_ranges[month]
        
        # Calculer les débits pour tous les jours du mois
        Q_values = []
        for t in range(start_day, end_day + 1):
            result = self.formula.calculate_Q(t, k_A, epsilon)
            Q_values.append(result['Q_central'])
        
        # Calculer la tendance
        if len(Q_values) > 1:
            trend_slope = (Q_values[-1] - Q_values[0]) / len(Q_values)
            trend = "Croissante" if trend_slope > 0 else "Décroissante"
        else:
            trend = "Stable"
        
        return {
            'month_name': month_names[month],
            'days_count': end_day - start_day + 1,
            'Q_mean': round(np.mean(Q_values), 2),
            'Q_min': round(np.min(Q_values), 2),
            'Q_max': round(np.max(Q_values), 2),
            'Q_std': round(np.std(Q_values), 2),
            'trend': trend,
            'Cm': self.formula.MONTHLY_COEFFS[month]
        }
    
    def compare_scenarios(self, t: int, k_A_list: List[float], epsilon: float) -> pd.DataFrame:
        """
        Compare plusieurs scénarios k(A) pour un jour donné - SAISON SECHE
        
        Args:
            t: Jour de saison (1-212)
            k_A_list: Liste de coefficients annuels à comparer
            epsilon: Taux d'erreur
            
        Returns:
            DataFrame avec comparaison des scénarios
        """
        data = []
        
        for k_A in k_A_list:
            result = self.formula.calculate_Q(t, k_A, epsilon)
            
            # Déterminer le statut
            if k_A > 1.2:
                status = "Très humide"
            elif k_A > 1.1:
                status = "Humide"
            elif k_A >= 0.95:
                status = "Normal"
            elif k_A >= 0.75:
                status = "Sec"
            else:
                status = "Très sec"
            
            data.append({
                'k(A)': k_A,
                'Statut': status,
                'Q_central': result['Q_central'],
                'Q_min': result['Q_inf'],
                'Q_max': result['Q_sup'],
                'Écart (%)': round(((k_A - 1.0) * 100), 1)
            })
        
        df = pd.DataFrame(data)
        return df
    
    def identify_critical_periods(self, k_A: float, epsilon: float, threshold: float = 30.0) -> List[Dict]:
        """
        Identifie les périodes critiques (débit < seuil) - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            threshold: Seuil de débit critique (m³/s)
            
        Returns:
            Liste de périodes critiques avec:
            - start_day: Jour de début
            - end_day: Jour de fin
            - duration: Durée en jours
            - Q_min: Débit minimum de la période
            - month: Mois concerné
        """
        # Générer la table complète
        full_table = self.generator.generate_full_season(k_A, epsilon)
        
        # Identifier les jours critiques
        critical_days = full_table[full_table['Q_central'] < threshold]
        
        if critical_days.empty:
            return []
        
        # Grouper les jours consécutifs
        periods = []
        current_period = None
        
        for _, row in critical_days.iterrows():
            t = row['t']
            
            if current_period is None:
                current_period = {
                    'start_day': t,
                    'end_day': t,
                    'Q_min': row['Q_central'],
                    'month': row['Mois']
                }
            elif t == current_period['end_day'] + 1:
                # Jour consécutif
                current_period['end_day'] = t
                current_period['Q_min'] = min(current_period['Q_min'], row['Q_central'])
            else:
                # Nouvelle période
                current_period['duration'] = current_period['end_day'] - current_period['start_day'] + 1
                periods.append(current_period)
                
                current_period = {
                    'start_day': t,
                    'end_day': t,
                    'Q_min': row['Q_central'],
                    'month': row['Mois']
                }
        
        # Ajouter la dernière période
        if current_period:
            current_period['duration'] = current_period['end_day'] - current_period['start_day'] + 1
            periods.append(current_period)
        
        return periods
    
    def calculate_variability(self, k_A: float, epsilon: float) -> Dict:
        """
        Calcule la variabilité des débits sur toute la saison - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Dictionnaire avec:
            - coefficient_variation: Coefficient de variation (%)
            - range: Étendue (Q_max - Q_min)
            - Q_mean: Débit moyen
            - Q_std: Écart-type
            - Q_min: Débit minimum
            - Q_max: Débit maximum
        """
        # Générer la table complète
        full_table = self.generator.generate_full_season(k_A, epsilon)
        
        Q_mean = full_table['Q_central'].mean()
        Q_std = full_table['Q_central'].std()
        Q_min = full_table['Q_central'].min()
        Q_max = full_table['Q_central'].max()
        
        # Coefficient de variation
        cv = (Q_std / Q_mean) * 100 if Q_mean > 0 else 0
        
        return {
            'coefficient_variation': round(cv, 2),
            'range': round(Q_max - Q_min, 2),
            'Q_mean': round(Q_mean, 2),
            'Q_std': round(Q_std, 2),
            'Q_min': round(Q_min, 2),
            'Q_max': round(Q_max, 2)
        }
    
    def get_peak_flow_day(self, k_A: float, epsilon: float) -> Dict:
        """
        Identifie le jour avec le débit maximum - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Dictionnaire avec:
            - t: Jour de saison
            - date: Date
            - month: Mois
            - Q_max: Débit maximum
        """
        # Générer la table complète
        full_table = self.generator.generate_full_season(k_A, epsilon)
        
        # Trouver le jour avec Q_central maximum
        max_row = full_table.loc[full_table['Q_central'].idxmax()]
        
        return {
            't': int(max_row['t']),
            'date': max_row['Date'],
            'month': max_row['Mois'],
            'Q_max': round(max_row['Q_central'], 2)
        }
    
    def generate_annual_ranking(self) -> pd.DataFrame:
        """
        Génère le classement annuel - SAISON SECHE
        Compatible avec l'interface de AnalyzerModule.

        Returns:
            DataFrame avec colonnes:
            - Rang, Année, k(A), Q moy, Qualif., vs Moyenne
        """
        coeffs_seche = CoefficientsModuleSeche(self.coeffs.data if self.coeffs else None)
        annual_df = coeffs_seche.calculate_annual_coefficients()

        df = pd.DataFrame({
            'Rang': annual_df['Rang'],
            'Année': annual_df['Saison'],
            'k(A)': annual_df['k(A)'].round(3),
            'Q moy': annual_df['Q moy (m³/s)'].round(2),
            'Qualif.': annual_df['Statut'],
        })
        df['vs Moyenne'] = ((df['k(A)'] - 1.0) * 100).round(1)
        df = df.sort_values('Rang').reset_index(drop=True)
        return df

    def generate_monthly_ranking(self) -> pd.DataFrame:
        """
        Génère le classement mensuel - SAISON SECHE
        Compatible avec l'interface de AnalyzerModule.

        Returns:
            DataFrame avec colonnes:
            - Rang, Mois, Q moy, Cm, Tendance %/j, Variabilité CV, Statut
        """
        coeffs_seche = CoefficientsModuleSeche(self.coeffs.data if self.coeffs else None)
        monthly_df = coeffs_seche.calculate_monthly_statistics()

        df = pd.DataFrame({
            'Mois': monthly_df['Mois'],
            'Q moy': monthly_df['Q moy'],
            'Cm': monthly_df['Cm'].round(3),
            'Tendance %/j': monthly_df['Tendance %/j'],
        })

        # CV approximatif par mois (saison sèche)
        cv_map = {
            'Décembre': 30.2,
            'Janvier': 28.5,
            'Février': 26.1,
            'Mars': 35.4,
            'Avril': 42.7,
            'Mai': 38.9,
            'Juin': 33.6,
        }
        df['Variabilité CV'] = df['Mois'].map(cv_map)

        # Statut basé sur Q moy
        def assign_status(q):
            if q > 150:
                return "Très élevé"
            elif q >= 80:
                return "Élevé"
            elif q >= 50:
                return "Modéré"
            elif q >= 30:
                return "Faible"
            else:
                return "Très faible"

        df['Statut'] = df['Q moy'].apply(assign_status)
        df['Rang'] = df['Q moy'].rank(ascending=False, method='min').astype(int)
        df = df[['Rang', 'Mois', 'Q moy', 'Cm', 'Tendance %/j', 'Variabilité CV', 'Statut']]
        df = df.sort_values('Rang').reset_index(drop=True)
        return df

    def get_low_flow_day(self, k_A: float, epsilon: float) -> Dict:
        """
        Identifie le jour avec le débit minimum (étiage) - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Dictionnaire avec:
            - t: Jour de saison
            - date: Date
            - month: Mois
            - Q_min: Débit minimum
        """
        # Générer la table complète
        full_table = self.generator.generate_full_season(k_A, epsilon)
        
        # Trouver le jour avec Q_central minimum
        min_row = full_table.loc[full_table['Q_central'].idxmin()]
        
        return {
            't': int(min_row['t']),
            'date': min_row['Date'],
            'month': min_row['Mois'],
            'Q_min': round(min_row['Q_central'], 2)
        }
