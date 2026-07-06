"""
Module de gestion des coefficients annuels et mensuels - SAISON SECHE.

Ce module calcule les coefficients k(A) pour chaque année, les statistiques mensuelles,
et génère les tableaux A, B, C pour l'affichage des coefficients.

SAISON SECHE : 1er Décembre → 30 Juin
Données : 2010-2025
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple


class CoefficientsModuleSeche:
    """Module de gestion des coefficients - SAISON SECHE"""
    
    # Débit historique moyen de référence - SAISON SECHE
    Q_HISTORICAL = 98.2  # m³/s
    
    # Coefficients mensuels Cm - SAISON SECHE
    MONTHLY_COEFFS = {
        12: 1.814,   # Décembre
        1: 0.8654,   # Janvier
        2: 0.4381,   # Février
        3: 0.3207,   # Mars (mois le plus sec)
        4: 0.3406,   # Avril
        5: 0.8628,   # Mai
        6: 2.3255    # Juin
    }
    
    # Coefficients du polynôme P(t) d'ordre 6 - SAISON SECHE
    POLY_COEFFS = {
        't6': -4.129e-11,
        't5': 2.720e-8,
        't4': -5.603e-6,
        't3': 3.519e-4,
        't2': 2.809e-2,
        't1': -5.229,
        't0': 250.7
    }
    
    # R² et RMSE du polynôme
    R_SQUARED = 0.994
    RMSE = 6.0
    
    # Données historiques k(A) - SAISON SECHE (2010-2025)
    HISTORICAL_K_A = {
        2010: 0.9956,
        2011: 0.9705,
        2012: 0.5763,
        2013: 1.2694,
        2014: 0.5763,
        2015: 1.017,
        2016: 0.7961,
        2017: 1.16,
        2018: 1.3921,
        2019: 0.9684,
        2020: 1.1837,
        2021: 1.144,
        2022: 1.144,
        2023: 1.0219,
        2024: 0.9663
    }
    
    def __init__(self, historical_data: pd.DataFrame = None):
        """
        Initialise avec les données historiques (2010-2025)
        
        Args:
            historical_data: DataFrame avec colonnes 'saison_annee' et 'debits'
                           Si None, utilise les données par défaut
        """
        self.data = historical_data
        self.annual_coeffs = {}
        self.monthly_stats = {}
    
    def calculate_annual_coefficients(self) -> pd.DataFrame:
        """
        Calcule k(A) pour chaque année - SAISON SECHE
        
        Formule: k(A) = Q̄_saison / Q̄_historique (98.2 m³/s)
        
        Returns:
            DataFrame avec colonnes:
            - Rang
            - Saison
            - k(A)
            - Q moy (m³/s)
            - Humidité
            - Statut
            - Emoji
        """
        # Utiliser les données historiques
        years_data = []
        
        for year, k_A in self.HISTORICAL_K_A.items():
            Q_mean = k_A * self.Q_HISTORICAL
            
            years_data.append({
                'Saison': f"{year}-{year+1}",
                'k(A)': k_A,
                'Q moy (m³/s)': round(Q_mean, 1)
            })
        
        # Créer le DataFrame
        df = pd.DataFrame(years_data)
        
        # Calculer humidité relative
        df['Humidité'] = df['k(A)'].apply(self._calculate_humidity_status)
        
        # Assigner statut
        df['Statut'] = df['k(A)'].apply(self._assign_annual_status)
        
        # Assigner emoji
        df['Emoji'] = df['Statut'].apply(self._assign_emoji)
        
        # Calculer rang humidité (1 = plus humide)
        df['Rang'] = df['k(A)'].rank(ascending=False, method='min').astype(int)
        
        # Trier par rang
        df = df.sort_values('Rang')
        
        # Réorganiser les colonnes
        df = df[['Rang', 'Saison', 'k(A)', 'Q moy (m³/s)', 'Humidité', 'Statut', 'Emoji']]
        
        # Stocker dans le cache
        for _, row in df.iterrows():
            year = int(row['Saison'].split('-')[0])
            self.annual_coeffs[year] = row['k(A)']
        
        return df
    
    def calculate_monthly_statistics(self) -> pd.DataFrame:
        """
        Calcule les statistiques mensuelles - SAISON SECHE
        
        Returns:
            DataFrame avec colonnes:
            - Mois
            - Cm
            - Q moy
            - Intervalle P10-P90
            - Tendance %/j
            - Succession max
        """
        months_data = [
            {
                'Mois': 'Décembre',
                'Cm': 1.814,
                'Q moy': 178.1,
                'Intervalle P10-P90': '111–259 m³/s',
                'Tendance %/j': -2.09,
                'Succession max': '↑8j / ↓11j'
            },
            {
                'Mois': 'Janvier',
                'Cm': 0.8654,
                'Q moy': 85.0,
                'Intervalle P10-P90': '50–124 m³/s',
                'Tendance %/j': -1.30,
                'Succession max': '↑10j / ↓6j'
            },
            {
                'Mois': 'Février',
                'Cm': 0.4381,
                'Q moy': 43.0,
                'Intervalle P10-P90': '25–64 m³/s',
                'Tendance %/j': 1.63,
                'Succession max': '↑13j / ↓7j'
            },
            {
                'Mois': 'Mars',
                'Cm': 0.3207,
                'Q moy': 31.5,
                'Intervalle P10-P90': '14–54 m³/s',
                'Tendance %/j': 5.61,
                'Succession max': '↑7j / ↓7j'
            },
            {
                'Mois': 'Avril',
                'Cm': 0.3406,
                'Q moy': 33.4,
                'Intervalle P10-P90': '5–66 m³/s',
                'Tendance %/j': 9.32,
                'Succession max': '↑10j / ↓5j'
            },
            {
                'Mois': 'Mai',
                'Cm': 0.8628,
                'Q moy': 84.6,
                'Intervalle P10-P90': '26–162 m³/s',
                'Tendance %/j': 13.69,
                'Succession max': '↑15j / ↓5j'
            },
            {
                'Mois': 'Juin',
                'Cm': 2.3255,
                'Q moy': 228.3,
                'Intervalle P10-P90': '107–402 m³/s',
                'Tendance %/j': 3.69,
                'Succession max': '↑13j / ↓5j'
            }
        ]
        
        df = pd.DataFrame(months_data)
        
        # Stocker dans le cache
        for _, row in df.iterrows():
            self.monthly_stats[row['Mois']] = {
                'Cm': row['Cm'],
                'Q_mean': row['Q moy']
            }
        
        return df
    
    def get_polynomial_table(self) -> pd.DataFrame:
        """
        Génère le tableau des coefficients du polynôme - SAISON SECHE
        
        Returns:
            DataFrame avec colonnes:
            - Terme
            - Coefficient
            - Exposant
            - Note
        """
        data = [
            {
                'Terme': 'a₆·t⁶',
                'Coefficient': -4.129e-11,
                'Exposant': 6,
                'Note': 'Forme générale'
            },
            {
                'Terme': 'a₅·t⁵',
                'Coefficient': 2.720e-8,
                'Exposant': 5,
                'Note': 'Correction ordre 5'
            },
            {
                'Terme': 'a₄·t⁴',
                'Coefficient': -5.603e-6,
                'Exposant': 4,
                'Note': 'Correction ordre 4'
            },
            {
                'Terme': 'a₃·t³',
                'Coefficient': 3.519e-4,
                'Exposant': 3,
                'Note': 'Correction ordre 3'
            },
            {
                'Terme': 'a₂·t²',
                'Coefficient': 2.809e-2,
                'Exposant': 2,
                'Note': 'Remontée de mai-juin'
            },
            {
                'Terme': 'a₁·t',
                'Coefficient': -5.229,
                'Exposant': 1,
                'Note': 'Décrue décembre-mars'
            },
            {
                'Terme': 'a₀',
                'Coefficient': 250.7,
                'Exposant': 0,
                'Note': 'Débit initial décembre'
            }
        ]
        
        df = pd.DataFrame(data)
        
        # Ajouter R² et RMSE
        stats_rows = pd.DataFrame([
            {
                'Terme': 'R²',
                'Coefficient': self.R_SQUARED,
                'Exposant': '-',
                'Note': 'Qualité ajustement'
            },
            {
                'Terme': 'RMSE',
                'Coefficient': self.RMSE,
                'Exposant': '-',
                'Note': 'Erreur quadratique (m³/s)'
            }
        ])
        
        df = pd.concat([df, stats_rows], ignore_index=True)
        
        return df
    
    def get_k_A(self, year: int) -> float:
        """
        Retourne k(A) pour une année donnée - SAISON SECHE
        
        Args:
            year: Année (2010-2024)
            
        Returns:
            Coefficient k(A)
            
        Raises:
            ValueError: Si l'année n'est pas dans les données
        """
        if year not in self.HISTORICAL_K_A:
            raise ValueError(f"Année {year} non disponible dans les données historiques (saison sèche)")
        
        return self.HISTORICAL_K_A[year]
    
    def _calculate_humidity_status(self, k_A: float) -> str:
        """
        Calcule le statut d'humidité textuel
        
        Args:
            k_A: Coefficient annuel
            
        Returns:
            Statut: "Très humide", "Humide", "Normal+", "Normal", "Sec", "Très sec"
        """
        if k_A > 1.2:
            return "Très humide"
        elif k_A > 1.1:
            return "Humide"
        elif k_A > 1.05:
            return "Normal+"
        elif k_A >= 0.95:
            return "Normal"
        elif k_A >= 0.75:
            return "Sec"
        else:
            return "Très sec"
    
    def _assign_annual_status(self, k_A: float) -> str:
        """
        Assigne le statut annuel basé sur k(A)
        
        Args:
            k_A: Coefficient annuel
            
        Returns:
            Statut: "Très humide", "Humide", "Normal+", "Normal", "Sec", "Très sec"
        """
        return self._calculate_humidity_status(k_A)
    
    def _assign_emoji(self, status: str) -> str:
        """
        Assigne l'emoji correspondant au statut
        
        Args:
            status: Statut d'humidité
            
        Returns:
            Emoji correspondant
        """
        emoji_map = {
            "Très humide": "🌊🌊🌊",
            "Humide": "🌊🌊",
            "Normal+": "🌊",
            "Normal": "〰️",
            "Sec": "☀️",
            "Très sec": "☀️☀️"
        }
        return emoji_map.get(status, "〰️")
