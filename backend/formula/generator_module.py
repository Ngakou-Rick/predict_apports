"""
Module de génération du tableau complet de 153 jours.

Ce module génère les prédictions pour toute la saison des pluies
avec calculs vectorisés pour optimiser les performances.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from backend.formula.formula_module import FormulaModule


class GeneratorModule:
    """Module de génération du tableau complet"""
    
    def __init__(self, formula_module: FormulaModule = None):
        """
        Initialise le générateur
        
        Args:
            formula_module: Instance de FormulaModule (créée si None)
        """
        self.formula = formula_module if formula_module else FormulaModule()
        self.cache = {}
    
    def generate_full_table(self, k_A: float, epsilon: float, year: int = None, start_date: datetime = None) -> pd.DataFrame:
        """
        Génère le tableau complet de 153 jours
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur (%)
            year: Année de prédiction (optionnel, défaut: année courante)
            start_date: Date de début (optionnel, si fourni, remplace year)
            
        Returns:
            DataFrame avec colonnes:
            - t
            - Date
            - Mois
            - P(t)
            - Q centrale
            - Q min (-8%)
            - Q max (+19%)
            - Q réelle
            - Écart %
            - Statut
        """
        # Valider k(A) uniquement (epsilon ignoré, bornes fixes -8%/+19%)
        is_valid, error_msg = self.formula.validate_inputs(1, k_A)
        if not is_valid:
            raise ValueError(error_msg)
        
        if start_date is None and year is None:
            year = datetime.now().year
        
        # Générer les jours de saison (1-153)
        t_values = np.arange(1, 154)
        
        # Calculer les dates
        if start_date is not None:
            dates = [start_date + timedelta(days=i) for i in range(153)]
        else:
            dates = self.calculate_dates(year)
        
        # Calculer tous les résultats en utilisant calculate_Q pour chaque jour
        # Cela permet d'appliquer les ajustements spécifiques (comme celui de juillet)
        results = [self.formula.calculate_Q(t, k_A, epsilon) for t in t_values]
        
        # Extraire les valeurs
        P_t_values = np.array([r['P_t'] for r in results])
        Q_central = np.array([r['Q_central'] for r in results])
        Q_min = np.array([r['Q_inf'] for r in results])
        Q_max = np.array([r['Q_sup'] for r in results])
        months = [r['month'] for r in results]
        month_names = [self._get_month_name(m) for m in months]
        
        # Assigner les statuts
        statuts = [self.assign_status(q) for q in Q_central]
        
        # Créer le DataFrame
        df = pd.DataFrame({
            't': t_values,
            'Date': dates,
            'Mois': month_names,
            'P(t)': np.round(P_t_values, 2),
            'Q centrale': np.round(Q_central, 2),
            'Q min (-8%)': np.round(Q_min, 2),
            'Q max (+19%)': np.round(Q_max, 2),
            'Q réelle': [None] * 153,
            'Écart %': [None] * 153,
            'Statut': statuts
        })
        
        return df
    
    def assign_status(self, Q_central: float) -> str:
        """
        Assigne le statut basé sur Q centrale
        
        Règles:
        - 🚨 Dangereux: >1200
        - 🔔 Élevé: 900-1200
        - ✅ Normal: 600-900
        - 🌤️ Modéré: 400-600
        - ℹ️ Bas: <400
        
        Args:
            Q_central: Débit central (m³/s)
            
        Returns:
            Statut avec icône
        """
        if Q_central > 1200:
            return "🚨 Dangereux"
        elif Q_central >= 900:
            return "🔔 Élevé"
        elif Q_central >= 600:
            return "✅ Normal"
        elif Q_central >= 400:
            return "🌤️ Modéré"
        else:
            return "ℹ️ Bas"
    
    def calculate_dates(self, year: int) -> list:
        """
        Calcule les dates du 1er juillet au 30 novembre
        
        Args:
            year: Année
            
        Returns:
            Liste de 153 dates
        """
        start_date = datetime(year, 7, 1)
        dates = [start_date + timedelta(days=i) for i in range(153)]
        return dates
    
    def update_real_flow(self, df: pd.DataFrame, t: int, Q_real: float) -> pd.DataFrame:
        """
        Met à jour le débit réel et calcule l'écart
        
        Args:
            df: DataFrame généré par generate_full_table
            t: Jour de saison
            Q_real: Débit réel mesuré
            
        Returns:
            DataFrame mis à jour
        """
        # Trouver la ligne correspondante
        idx = df[df['t'] == t].index
        
        if len(idx) == 0:
            raise ValueError(f"Jour {t} non trouvé dans le tableau")
        
        idx = idx[0]
        
        # Mettre à jour Q réelle
        df.at[idx, 'Q réelle'] = Q_real
        
        # Calculer l'écart %
        Q_central = df.at[idx, 'Q centrale']
        ecart = ((Q_real - Q_central) / Q_central) * 100
        df.at[idx, 'Écart %'] = round(ecart, 2)
        
        return df
    
    def _get_month_name(self, month: int) -> str:
        """
        Retourne le nom du mois
        
        Args:
            month: Numéro du mois (7-11)
            
        Returns:
            Nom du mois
        """
        month_names = {
            7: 'Juillet',
            8: 'Août',
            9: 'Septembre',
            10: 'Octobre',
            11: 'Novembre'
        }
        return month_names.get(month, 'Inconnu')
