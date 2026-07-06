"""
Module de génération de table journalière complète - SAISON SECHE.

Ce module génère les prédictions pour tous les jours de la saison sèche (212 jours)
avec 3 scénarios : pessimiste, central, optimiste.

SAISON SECHE : 1er Décembre → 30 Juin (212 jours)
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
from backend.formula.formula_module_seche import FormulaModuleSeche


class GeneratorModuleSeche:
    """Module de génération de table journalière complète - SAISON SECHE"""
    
    def __init__(self, formula_module: FormulaModuleSeche = None):
        """
        Initialise le générateur
        
        Args:
            formula_module: Instance de FormulaModuleSeche (créée si None)
        """
        self.formula = formula_module if formula_module else FormulaModuleSeche()
    
    def generate_full_table(self, k_A: float, epsilon: float, year: int = None, start_date: datetime = None) -> pd.DataFrame:
        """
        Génère la table journalière complète pour toute la saison sèche (212 jours)
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur (0.01-0.08)
            year: Année de début (année du 1er décembre)
            start_date: Date de début (optionnel, si fourni, remplace year)
            
        Returns:
            DataFrame avec colonnes:
            - t: Jour de saison (1-212)
            - Date: Date calendaire
            - Mois: Nom du mois
            - P(t): Valeur du polynôme
            - Cm: Coefficient mensuel
            - Q_central: Débit central
            - Q_min: Débit minimum (-80%)
            - Q_max: Débit maximum (+8%)
            
        Raises:
            ValueError: Si les paramètres sont invalides
        """
        if start_date is None and year is None:
            year = datetime.now().year
        
        # Valider k_A et epsilon
        is_valid, error_msg = self.formula.validate_inputs(1, k_A, epsilon)
        if not is_valid:
            raise ValueError(error_msg)
        
        # Générer les données pour tous les jours
        data = []
        
        for t in range(1, 213):  # 1 à 212
            # Calculer les débits
            result = self.formula.calculate_Q(t, k_A, epsilon)
            
            # Calculer la date
            if start_date is not None:
                date = start_date + timedelta(days=t - 1)
            else:
                date = self._calculate_date(t, year)
            
            # Obtenir le nom du mois
            month_names = {
                12: 'Décembre',
                1: 'Janvier',
                2: 'Février',
                3: 'Mars',
                4: 'Avril',
                5: 'Mai',
                6: 'Juin'
            }
            month_name = month_names[result['month']]
            
            data.append({
                't': t,
                'Date': date.strftime('%d/%m/%Y'),
                'Mois': month_name,
                'P(t)': result['P_t'],
                'Q centrale': result['Q_central'],
                'Q min (-80%)': result['Q_inf'],
                'Q max (+8%)': result['Q_sup']
            })
        
        df = pd.DataFrame(data)
        return df
    
    def generate_full_season(self, k_A: float, epsilon: float, year: int = None, start_date: datetime = None) -> pd.DataFrame:
        """
        Alias pour generate_full_table() - pour compatibilité
        """
        return self.generate_full_table(k_A, epsilon, year, start_date)
    
    def generate_monthly_summary(self, k_A: float, epsilon: float, year: int = None) -> pd.DataFrame:
        """
        Génère un résumé mensuel des prédictions - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            year: Année de début
            
        Returns:
            DataFrame avec colonnes:
            - Mois: Nom du mois
            - Jours: Nombre de jours
            - Q_moy: Débit moyen du mois
            - Q_min: Débit minimum du mois
            - Q_max: Débit maximum du mois
            - Cm: Coefficient mensuel
        """
        # Générer la table complète
        full_table = self.generate_full_table(k_A, epsilon, year)
        
        # Grouper par mois
        monthly_summary = full_table.groupby('Mois').agg({
            't': 'count',
            'Q centrale': 'mean',
            'Q min (-80%)': 'min',
            'Q max (+8%)': 'max'
        }).reset_index()
        
        # Renommer les colonnes
        monthly_summary.columns = ['Mois', 'Jours', 'Q_moy', 'Q_min', 'Q_max']
        
        # Arrondir les valeurs
        monthly_summary['Q_moy'] = monthly_summary['Q_moy'].round(2)
        monthly_summary['Q_min'] = monthly_summary['Q_min'].round(2)
        monthly_summary['Q_max'] = monthly_summary['Q_max'].round(2)
        
        # Ordonner les mois correctement
        month_order = ['Décembre', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin']
        monthly_summary['Mois'] = pd.Categorical(monthly_summary['Mois'], categories=month_order, ordered=True)
        monthly_summary = monthly_summary.sort_values('Mois')
        
        return monthly_summary
    
    def export_to_excel(self, k_A: float, epsilon: float, year: int, filename: str) -> str:
        """
        Exporte la table journalière complète vers Excel - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            year: Année de début
            filename: Nom du fichier (sans extension)
            
        Returns:
            Chemin du fichier créé
        """
        # Générer les tables
        full_table = self.generate_full_season(k_A, epsilon, year)
        monthly_summary = self.generate_monthly_summary(k_A, epsilon, year)
        
        # Créer le nom de fichier avec timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = f"exports/{filename}_saison_seche_{timestamp}.xlsx"
        
        # Exporter vers Excel avec plusieurs feuilles
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            full_table.to_excel(writer, sheet_name='Table journalière', index=False)
            monthly_summary.to_excel(writer, sheet_name='Résumé mensuel', index=False)
            
            # Ajouter une feuille avec les paramètres
            params_df = pd.DataFrame({
                'Paramètre': ['Coefficient annuel k(A)', 'Taux erreur ε (%)', 'Année début', 'Saison', 'Durée (jours)'],
                'Valeur': [k_A, epsilon * 100, year, 'Sèche', 212]
            })
            params_df.to_excel(writer, sheet_name='Paramètres', index=False)
        
        return filepath
    
    def _calculate_date(self, t: int, year: int) -> datetime:
        """
        Calcule la date à partir du jour de saison - SAISON SECHE
        
        Args:
            t: Jour de saison (1-212)
            year: Année de début (année du 1er décembre)
            
        Returns:
            Date correspondante
        """
        # 1er décembre = jour 1
        start_date = datetime(year, 12, 1)
        date = start_date + timedelta(days=t - 1)
        return date
    
    def get_statistics(self, k_A: float, epsilon: float) -> Dict:
        """
        Calcule les statistiques globales de la saison - SAISON SECHE
        
        Args:
            k_A: Coefficient annuel
            epsilon: Taux d'erreur
            
        Returns:
            Dictionnaire avec statistiques:
            - Q_mean: Débit moyen de la saison
            - Q_min: Débit minimum de la saison
            - Q_max: Débit maximum de la saison
            - Q_std: Écart-type
            - duration_days: Durée en jours
        """
        # Générer la table complète
        full_table = self.generate_full_table(k_A, epsilon)
        
        return {
            'Q_mean': round(full_table['Q centrale'].mean(), 2),
            'Q_min': round(full_table['Q min (-80%)'].min(), 2),
            'Q_max': round(full_table['Q max (+8%)'].max(), 2),
            'Q_std': round(full_table['Q centrale'].std(), 2),
            'duration_days': 212
        }
