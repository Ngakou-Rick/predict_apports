"""
Module d'extraction des coefficients à partir de données historiques.

Ce module extrait automatiquement:
- Coefficients du polynôme P(t) d'ordre 6
- Coefficients mensuels Cm
- Débit historique Q_HISTORICAL
- Coefficients annuels k(A)
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
from backend.formula.data_quality_validator import DataQualityValidator


class CoefficientExtractor:
    """
    Extracteur de coefficients à partir de données historiques.
    
    Attributes:
        season_type: 'rainy' (153 jours) ou 'dry' (212 jours)
        data: DataFrame avec colonnes ['date', 'debits', 'saison_annee']
        quality_score: Score de qualité des données (0-100)
    """
    
    # Durées fixes des saisons
    SEASON_DURATIONS = {
        'rainy': 153,  # Juillet → Novembre
        'dry': 212     # Décembre → Juin
    }
    
    # Mois par saison
    SEASON_MONTHS = {
        'rainy': [7, 8, 9, 10, 11],  # Juillet à Novembre
        'dry': [12, 1, 2, 3, 4, 5, 6]  # Décembre à Juin
    }
    
    def __init__(self, season_type: str, data: pd.DataFrame):
        """
        Initialise l'extracteur.
        
        Args:
            season_type: 'rainy' (153 jours) ou 'dry' (212 jours)
            data: Données historiques de la saison
        """
        if season_type not in ['rainy', 'dry']:
            raise ValueError("season_type doit être 'rainy' ou 'dry'")
        
        self.season_type = season_type
        self.data = data
        self.validator = DataQualityValidator(data)
        self.quality_report = None
    
    def validate_data_quality(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Valide la qualité des données historiques.
        
        Returns:
            Tuple (is_valid, quality_report)
            quality_report contient:
            - years_count: Nombre d'années
            - missing_percentage: % de valeurs manquantes
            - quality_score: Score 0-100
            - warnings: Liste des avertissements
        """
        self.quality_report = self.validator.get_validation_report()
        return (self.quality_report['is_valid'], self.quality_report)
    
    def extract_polynomial_coefficients(self) -> Dict[str, float]:
        """
        Extrait les coefficients du polynôme P(t) d'ordre 6.
        
        Utilise numpy.polyfit pour ajuster un polynôme d'ordre 6
        sur les données de débit en fonction du jour de saison.
        
        Returns:
            Dict avec clés: 't6', 't5', 't4', 't3', 't2', 't1', 't0', 'r_squared'
        """
        # Préparer les données: grouper par jour de saison et calculer la moyenne
        season_duration = self.SEASON_DURATIONS[self.season_type]
        
        # Créer une colonne jour_saison si elle n'existe pas
        if 'jour_saison' not in self.data.columns:
            # Calculer le jour de saison à partir de la date
            self.data['jour_saison'] = self._calculate_season_day()
        
        # Grouper par jour de saison et calculer la moyenne des débits
        daily_means = self.data.groupby('jour_saison')['debits'].mean()
        
        # Préparer les données pour polyfit
        t_values = daily_means.index.values
        Q_values = daily_means.values
        
        # Ajuster un polynôme d'ordre 6
        coeffs = np.polyfit(t_values, Q_values, 6)
        
        # Calculer R²
        Q_pred = np.polyval(coeffs, t_values)
        ss_res = np.sum((Q_values - Q_pred) ** 2)
        ss_tot = np.sum((Q_values - np.mean(Q_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
        
        return {
            't6': float(coeffs[0]),
            't5': float(coeffs[1]),
            't4': float(coeffs[2]),
            't3': float(coeffs[3]),
            't2': float(coeffs[4]),
            't1': float(coeffs[5]),
            't0': float(coeffs[6]),
            'r_squared': float(r_squared)
        }
    
    def extract_monthly_coefficients(self) -> Dict[int, float]:
        """
        Extrait les coefficients mensuels Cm.
        
        Calcule la moyenne des débits pour chaque mois,
        puis normalise par rapport à la moyenne saisonnière.
        
        Formule: Cm = Q̄_mois / Q̄_saison
        
        Returns:
            Dict {mois: Cm}
            - Pluies: {7: Cm_juillet, 8: Cm_août, ..., 11: Cm_novembre}
            - Sèche: {12: Cm_décembre, 1: Cm_janvier, ..., 6: Cm_juin}
        """
        # Extraire le mois de la date
        if 'date' in self.data.columns:
            self.data['mois'] = pd.to_datetime(self.data['date']).dt.month
        
        # Calculer la moyenne des débits par mois
        monthly_means = self.data.groupby('mois')['debits'].mean()
        
        # Calculer la moyenne saisonnière globale
        season_mean = self.data['debits'].mean()
        
        # Calculer les coefficients Cm (normalisés)
        monthly_coeffs = {}
        season_months = self.SEASON_MONTHS[self.season_type]
        
        for month in season_months:
            if month in monthly_means.index:
                Cm = monthly_means[month] / season_mean if season_mean > 0 else 1.0
                monthly_coeffs[month] = float(Cm)
            else:
                # Si le mois n'a pas de données, utiliser 1.0 par défaut
                monthly_coeffs[month] = 1.0
        
        return monthly_coeffs
    
    def extract_Q_historical(self) -> float:
        """
        Calcule le débit historique moyen Q_HISTORICAL.
        
        Returns:
            Moyenne de tous les débits historiques (m³/s)
        """
        Q_hist = self.data['debits'].mean()
        return float(Q_hist)
    
    def extract_annual_coefficients(self) -> Dict[int, float]:
        """
        Calcule les coefficients annuels k(A) pour chaque année.
        
        Formule: k(A) = Q̄_année / Q̄_historique
        
        Returns:
            Dict {année: k(A)}
        """
        Q_historical = self.extract_Q_historical()
        
        # Grouper par année et calculer la moyenne
        annual_means = self.data.groupby('saison_annee')['debits'].mean()
        
        # Calculer k(A) pour chaque année
        annual_coeffs = {}
        for year, Q_mean in annual_means.items():
            k_A = Q_mean / Q_historical if Q_historical > 0 else 1.0
            # Gérer le format '2010-2011' ou 2010
            if isinstance(year, str) and '-' in year:
                # Format '2010-2011' → garder comme chaîne
                annual_coeffs[year] = float(k_A)
            else:
                # Format numérique → convertir en int
                annual_coeffs[int(year)] = float(k_A)
        
        return annual_coeffs
    
    def extract_all(self) -> Dict[str, Any]:
        """
        Extrait tous les coefficients en une seule opération.
        
        Returns:
            Dict contenant:
            - polynomial_coeffs: Coefficients du polynôme
            - monthly_coeffs: Coefficients mensuels
            - Q_historical: Débit historique moyen
            - annual_coeffs: Coefficients annuels par année
            - epsilon: Taux d'erreur optimal calculé
            - daily_diff: Écart journalier moyen optimal (pour ajustement)
            - quality_report: Rapport de qualité
        """
        # Valider la qualité des données
        is_valid, quality_report = self.validate_data_quality()
        
        # Extraire tous les coefficients
        polynomial_coeffs = self.extract_polynomial_coefficients()
        monthly_coeffs = self.extract_monthly_coefficients()
        Q_historical = self.extract_Q_historical()
        annual_coeffs = self.extract_annual_coefficients()
        epsilon = self.extract_optimal_epsilon(polynomial_coeffs)
        daily_diff = self.extract_optimal_daily_diff()
        
        # Valider le R² du polynôme
        r_squared = polynomial_coeffs['r_squared']
        poly_valid, poly_msg = self.validator.validate_polynomial_fit(r_squared)
        
        if not poly_valid:
            quality_report['warnings'].append(poly_msg)
            quality_report['recommendations'].append(
                "Les données présentent une forte variabilité. Vérifiez la qualité des mesures."
            )
        
        return {
            'polynomial_coeffs': polynomial_coeffs,
            'monthly_coeffs': monthly_coeffs,
            'Q_historical': Q_historical,
            'annual_coeffs': annual_coeffs,
            'epsilon': epsilon,
            'daily_diff': daily_diff,
            'quality_report': quality_report,
            'season_type': self.season_type
        }
    
    def extract_optimal_daily_diff(self) -> float:
        """
        Calcule l'écart journalier moyen optimal entre jours consécutifs.
        
        Cet écart est utilisé pour l'ajustement du Q_central entre jours consécutifs,
        notamment pour le premier mois de la saison (juillet pour pluies, décembre pour sèche).
        
        Returns:
            Écart journalier moyen en m³/s
        """
        # Préparer les données
        if 'jour_saison' not in self.data.columns:
            self.data['jour_saison'] = self._calculate_season_day()
        
        # Grouper par jour de saison et calculer la moyenne
        daily_means = self.data.groupby('jour_saison')['debits'].mean().sort_index()
        
        # Calculer les différences entre jours consécutifs
        daily_diffs = daily_means.diff().dropna()
        
        # Calculer la moyenne absolue des différences
        mean_daily_diff = daily_diffs.abs().mean()
        
        return float(mean_daily_diff)
    
    def extract_optimal_epsilon(self, polynomial_coeffs: Dict[str, float]) -> float:
        """
        Calcule le taux d'erreur optimal ε à partir des données historiques.
        
        Méthode: Calcule l'erreur relative moyenne entre les débits réels et 
        les débits prédits par le polynôme P(t).
        
        Args:
            polynomial_coeffs: Coefficients du polynôme déjà extraits
            
        Returns:
            Taux d'erreur ε optimal (entre 0.01 et 0.15)
        """
        # Préparer les données
        if 'jour_saison' not in self.data.columns:
            self.data['jour_saison'] = self._calculate_season_day()
        
        # Grouper par jour de saison et calculer la moyenne
        daily_means = self.data.groupby('jour_saison')['debits'].mean()
        
        # Calculer les prédictions du polynôme
        t_values = daily_means.index.values
        Q_actual = daily_means.values
        
        # Reconstruire le polynôme
        coeffs_array = np.array([
            polynomial_coeffs['t6'],
            polynomial_coeffs['t5'],
            polynomial_coeffs['t4'],
            polynomial_coeffs['t3'],
            polynomial_coeffs['t2'],
            polynomial_coeffs['t1'],
            polynomial_coeffs['t0']
        ])
        
        Q_predicted = np.polyval(coeffs_array, t_values)
        
        # Calculer l'erreur relative moyenne
        # ε = moyenne(|Q_actual - Q_predicted| / Q_actual)
        relative_errors = np.abs(Q_actual - Q_predicted) / Q_actual
        epsilon = np.mean(relative_errors)
        
        # Limiter ε entre 1% et 15%
        epsilon = max(0.01, min(0.15, epsilon))
        
        return float(epsilon)
    
    def _calculate_season_day(self) -> pd.Series:
        """
        Calcule le jour de saison à partir de la date.
        
        Returns:
            Series avec le jour de saison (1-153 ou 1-212)
        """
        dates = pd.to_datetime(self.data['date'])
        
        if self.season_type == 'rainy':
            # Saison des pluies: 1er juillet = jour 1
            # Calculer le jour depuis le 1er juillet de chaque année
            year = dates.dt.year
            season_start = pd.to_datetime(year.astype(str) + '-07-01')
            day_of_season = (dates - season_start).dt.days + 1
            
            # Gérer les dates avant le 1er juillet (année précédente)
            mask = day_of_season < 1
            if mask.any():
                season_start_prev = pd.to_datetime((year - 1).astype(str) + '-07-01')
                day_of_season[mask] = (dates[mask] - season_start_prev[mask]).dt.days + 1
        
        else:  # dry season
            # Saison sèche: 1er décembre = jour 1
            year = dates.dt.year
            season_start = pd.to_datetime(year.astype(str) + '-12-01')
            day_of_season = (dates - season_start).dt.days + 1
            
            # Gérer les dates avant le 1er décembre (année précédente)
            mask = day_of_season < 1
            if mask.any():
                season_start_prev = pd.to_datetime((year - 1).astype(str) + '-12-01')
                day_of_season[mask] = (dates[mask] - season_start_prev[mask]).dt.days + 1
        
        return day_of_season

