"""
Module d'analyse hydrologique des débits
"""
import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Tuple


class FlowAnalyzer:
    """Analyse hydrologique des débits"""
    
    def __init__(self, data: pd.DataFrame):
        self.data = data.copy()
        self.debit_col = self._find_debit_column()
        
        # Convertir la colonne débit en numérique
        if self.debit_col and self.debit_col in self.data.columns:
            self.data[self.debit_col] = pd.to_numeric(self.data[self.debit_col], errors='coerce')
        
    def _find_debit_column(self) -> str:
        """Identifie la colonne des débits"""
        for col in self.data.columns:
            if 'debit' in col.lower() or 'q' == col.lower():
                return col
        return None
    
    def temporal_analysis(self) -> Dict:
        """Analyse temporelle des débits"""
        if self.debit_col is None:
            return {}
        
        debits = self.data[self.debit_col].dropna()
        
        analysis = {
            'moyenne': debits.mean(),
            'mediane': debits.median(),
            'ecart_type': debits.std(),
            'min': debits.min(),
            'max': debits.max(),
            'coefficient_variation': (debits.std() / debits.mean()) * 100 if debits.mean() != 0 else 0,
            'tendance': self._calculate_trend(debits),
            'anomalies': self._detect_anomalies(debits)
        }
        
        return analysis
    
    def _calculate_trend(self, series: pd.Series) -> Dict:
        """Calcule la tendance des débits"""
        x = np.arange(len(series))
        y = series.values
        
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        return {
            'pente': slope,
            'r2': r_value**2,
            'p_value': p_value,
            'tendance_type': 'croissante' if slope > 0 else 'décroissante'
        }
    
    def _detect_anomalies(self, series: pd.Series, threshold: float = 3.0) -> Dict:
        """Détecte les anomalies (valeurs aberrantes)"""
        mean = series.mean()
        std = series.std()
        
        z_scores = np.abs((series - mean) / std)
        anomalies = series[z_scores > threshold]
        
        return {
            'nombre': len(anomalies),
            'indices': anomalies.index.tolist(),
            'valeurs': anomalies.tolist()
        }
    
    def monthly_analysis(self) -> pd.DataFrame:
        """Analyse mensuelle des débits"""
        if self.debit_col is None or 'date' not in self.data.columns:
            return pd.DataFrame()
        
        df = self.data.copy()
        df['mois'] = df['date'].dt.month
        
        monthly_stats = df.groupby('mois')[self.debit_col].agg([
            ('moyenne', 'mean'),
            ('min', 'min'),
            ('max', 'max'),
            ('percentile_5', lambda x: x.quantile(0.05)),
            ('mediane', 'median'),
            ('percentile_95', lambda x: x.quantile(0.95)),
            ('ecart_type', 'std')
        ]).reset_index()
        
        return monthly_stats
    
    def lag_analysis(self, max_lag: int = 7) -> Dict:
        """Analyse des dépendances temporelles (autocorrélation et lag features)"""
        if self.debit_col is None:
            return {}
        
        debits = self.data[self.debit_col].dropna()
        
        # Autocorrélation
        autocorr = {}
        for lag in range(1, max_lag + 1):
            autocorr[f'lag_{lag}'] = debits.autocorr(lag=lag)
        
        # Créer les lag features
        lag_features = pd.DataFrame()
        for lag in range(1, max_lag + 1):
            lag_features[f'Q_t+{lag}'] = debits.shift(-lag)
        
        # Corrélations entre Q(t) et Q(t+i)
        correlations = {}
        for col in lag_features.columns:
            correlations[col] = debits.corr(lag_features[col])
        
        return {
            'autocorrelation': autocorr,
            'lag_correlations': correlations,
            'lag_features_sample': lag_features.head(10).to_dict()
        }
    
    def get_complete_analysis(self) -> Dict:
        """Retourne l'analyse complète"""
        return {
            'temporelle': self.temporal_analysis(),
            'mensuelle': self.monthly_analysis().to_dict(),
            'dynamique': self.lag_analysis()
        }
