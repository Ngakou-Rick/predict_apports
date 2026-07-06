"""
Module d'analyse et modélisation climatique
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple


class ClimateAnalyzer:
    """Analyse des variables climatiques et leur relation avec les débits"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self._identify_columns()
        self._convert_to_numeric()
    
    def _convert_to_numeric(self):
        """Convertit les colonnes en numérique"""
        cols_to_convert = [
            self.debit_col, self.pluie_col, self.etp_col, 
            self.tmax_col, self.tmin_col
        ]
        
        for col in cols_to_convert:
            if col and col in self.data.columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
        
    def _identify_columns(self):
        """Identifie les colonnes climatiques"""
        self.debit_col = None
        self.pluie_col = None
        self.etp_col = None
        self.tmax_col = None
        self.tmin_col = None
        
        for col in self.data.columns:
            col_lower = col.lower()
            if 'debit' in col_lower or col_lower == 'q':
                self.debit_col = col
            elif 'pluie' in col_lower or 'precip' in col_lower:
                self.pluie_col = col
            elif 'etp' in col_lower or 'evapotranspiration' in col_lower:
                self.etp_col = col
            elif 'tmax' in col_lower or 'temp' in col_lower and 'max' in col_lower:
                self.tmax_col = col
            elif 'tmin' in col_lower or 'temp' in col_lower and 'min' in col_lower:
                self.tmin_col = col
    
    def calculate_derived_variables(self) -> pd.DataFrame:
        """Calcule les variables dérivées"""
        df = self.data.copy()
        
        # Amplitude thermique
        if self.tmax_col and self.tmin_col:
            # Convertir en numérique
            tmax = pd.to_numeric(df[self.tmax_col], errors='coerce')
            tmin = pd.to_numeric(df[self.tmin_col], errors='coerce')
            df['amplitude_thermique'] = tmax - tmin
        
        # Bilan hydrique
        if self.pluie_col and self.etp_col:
            # Convertir en numérique
            pluie = pd.to_numeric(df[self.pluie_col], errors='coerce')
            etp = pd.to_numeric(df[self.etp_col], errors='coerce')
            df['bilan_hydrique'] = pluie - etp
        
        return df
    
    def correlation_analysis(self) -> Dict:
        """Analyse des corrélations entre débits et variables climatiques"""
        df = self.calculate_derived_variables()
        
        if self.debit_col is None:
            return {}
        
        correlations = {}
        climate_vars = []
        
        # Variables à analyser
        if self.pluie_col:
            climate_vars.append(('Pluie', self.pluie_col))
        if self.etp_col:
            climate_vars.append(('ETP', self.etp_col))
        if 'amplitude_thermique' in df.columns:
            climate_vars.append(('Amplitude thermique', 'amplitude_thermique'))
        if 'bilan_hydrique' in df.columns:
            climate_vars.append(('Bilan hydrique', 'bilan_hydrique'))
        
        # Calculer les corrélations
        for var_name, var_col in climate_vars:
            if var_col in df.columns:
                # Créer un dataframe propre sans NaN
                clean_df = df[[self.debit_col, var_col]].dropna()
                
                if len(clean_df) > 0:
                    # Corrélation de Pearson
                    pearson_corr, pearson_p = stats.pearsonr(
                        clean_df[self.debit_col],
                        clean_df[var_col]
                    )
                    
                    # Corrélation de Spearman
                    spearman_corr, spearman_p = stats.spearmanr(
                        clean_df[self.debit_col],
                        clean_df[var_col]
                    )
                    
                    correlations[var_name] = {
                        'pearson': {'correlation': pearson_corr, 'p_value': pearson_p},
                        'spearman': {'correlation': spearman_corr, 'p_value': spearman_p}
                    }
        
        return correlations
    
    def rainfall_distribution(self) -> Dict:
        """Analyse de la distribution des pluies"""
        if self.pluie_col is None:
            return {}
        
        pluie = self.data[self.pluie_col].dropna()
        
        distribution = {
            'moyenne': pluie.mean(),
            'mediane': pluie.median(),
            'ecart_type': pluie.std(),
            'min': pluie.min(),
            'max': pluie.max(),
            'total': pluie.sum(),
            'jours_pluie': (pluie > 0).sum(),
            'jours_sans_pluie': (pluie == 0).sum(),
            'percentiles': {
                '25': pluie.quantile(0.25),
                '50': pluie.quantile(0.50),
                '75': pluie.quantile(0.75),
                '90': pluie.quantile(0.90),
                '95': pluie.quantile(0.95)
            }
        }
        
        return distribution
    
    def monthly_climate_analysis(self) -> pd.DataFrame:
        """Analyse climatique mensuelle"""
        if 'date' not in self.data.columns:
            return pd.DataFrame()
        
        df = self.calculate_derived_variables()
        df['mois'] = df['date'].dt.month
        
        agg_dict = {}
        
        if self.pluie_col:
            agg_dict[self.pluie_col] = ['mean', 'sum', 'std']
        if self.etp_col:
            agg_dict[self.etp_col] = ['mean', 'sum', 'std']
        if 'amplitude_thermique' in df.columns:
            agg_dict['amplitude_thermique'] = ['mean', 'std']
        if 'bilan_hydrique' in df.columns:
            agg_dict['bilan_hydrique'] = ['mean', 'sum']
        
        if not agg_dict:
            return pd.DataFrame()
        
        monthly_stats = df.groupby('mois').agg(agg_dict).reset_index()
        monthly_stats.columns = ['_'.join(col).strip('_') for col in monthly_stats.columns.values]
        
        return monthly_stats
    
    def predict_climate_from_flow(self, predicted_flows: pd.Series) -> Dict:
        """Prédit les variables climatiques à partir des débits prévus"""
        df = self.calculate_derived_variables()
        
        if self.debit_col is None:
            return {}
        
        predictions = {}
        
        # Modèles de régression simples pour chaque variable
        climate_vars = []
        if self.pluie_col:
            climate_vars.append(('Pluie', self.pluie_col))
        if self.etp_col:
            climate_vars.append(('ETP', self.etp_col))
        if 'amplitude_thermique' in df.columns:
            climate_vars.append(('Amplitude thermique', 'amplitude_thermique'))
        if 'bilan_hydrique' in df.columns:
            climate_vars.append(('Bilan hydrique', 'bilan_hydrique'))
        
        for var_name, var_col in climate_vars:
            if var_col in df.columns:
                # Régression linéaire simple
                clean_data = df[[self.debit_col, var_col]].dropna()
                
                if len(clean_data) > 0:
                    slope, intercept, r_value, p_value, std_err = stats.linregress(
                        clean_data[self.debit_col],
                        clean_data[var_col]
                    )
                    
                    # Prédiction
                    predicted_values = slope * predicted_flows + intercept
                    
                    predictions[var_name] = {
                        'values': predicted_values.tolist(),
                        'r2': r_value**2,
                        'equation': f'y = {slope:.4f}x + {intercept:.4f}'
                    }
        
        return predictions
    
    def get_complete_analysis(self) -> Dict:
        """Retourne l'analyse climatique complète"""
        return {
            'correlations': self.correlation_analysis(),
            'rainfall_distribution': self.rainfall_distribution(),
            'monthly_analysis': self.monthly_climate_analysis().to_dict(),
            'variables_disponibles': {
                'pluie': self.pluie_col is not None,
                'etp': self.etp_col is not None,
                'temperature': self.tmax_col is not None and self.tmin_col is not None
            }
        }
