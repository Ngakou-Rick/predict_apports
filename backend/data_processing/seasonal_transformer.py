"""
Module de transformation des données en années hydrologiques saisonnières
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Tuple, Dict


class SeasonalTransformer:
    """Transforme les données en saisons hydrologiques"""
    
    def __init__(self):
        self.dry_season_data = None
        self.rainy_season_data = None
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Charge les données depuis un fichier Excel avec nettoyage automatique
        
        Nettoyage appliqué:
        - Normalisation des noms de colonnes (minuscules, espaces supprimés)
        - Remplacement des valeurs non-numériques ('-', 'N/A', etc.) par NaN
        - Conversion des colonnes numériques
        - Suppression des lignes avec valeurs manquantes critiques
        """
        try:
            df = pd.read_excel(file_path)
            
            # 1. Normaliser les noms de colonnes
            df.columns = df.columns.str.strip().str.lower()
            
            # 2. Identifier et nettoyer la colonne de débit
            debit_col = None
            for col in df.columns:
                if 'debit' in col or 'débit' in col:
                    debit_col = col
                    break
            
            if debit_col:
                # Remplacer les valeurs non-numériques par NaN
                df[debit_col] = df[debit_col].replace(['-', '--', '---', 'N/A', 'NA', '', ' '], np.nan)
                # Convertir en numérique
                df[debit_col] = pd.to_numeric(df[debit_col], errors='coerce')
                # Créer/renommer la colonne 'debits' (format standard)
                df['debits'] = df[debit_col]
            
            # 3. Identifier la colonne de date
            date_col = None
            for col in df.columns:
                if 'date' in col or 'jour' in col:
                    date_col = col
                    break
            
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df = df.rename(columns={date_col: 'date'})
            else:
                raise ValueError("Aucune colonne de date trouvée")
            
            # 4. Supprimer les lignes avec date ou débit manquant
            df = df.dropna(subset=['date'])
            if 'debits' in df.columns:
                df = df.dropna(subset=['debits'])
            
            # 5. Trier par date
            df = df.sort_values('date').reset_index(drop=True)
            
            return df
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du fichier: {str(e)}")
    
    def split_by_season(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Sépare les données en saison sèche et saison des pluies
        
        Saison sèche: 1er décembre (année n) au 30 juin (année n+1)
        Saison des pluies: 1er juillet (année n) au 30 novembre (année n)
        """
        df = df.copy()
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Créer l'année hydrologique pour chaque saison
        def get_dry_season_year(row):
            """Année hydrologique pour saison sèche (commence en décembre)"""
            if row['month'] >= 12:
                return f"{row['year']}-{row['year']+1}"
            elif row['month'] <= 6:
                return f"{row['year']-1}-{row['year']}"
            return None
        
        def get_rainy_season_year(row):
            """Année hydrologique pour saison des pluies (juillet à novembre)"""
            if 7 <= row['month'] <= 11:
                return str(row['year'])
            return None
        
        # Saison sèche: décembre à juin
        dry_mask = (df['month'] >= 12) | (df['month'] <= 6)
        dry_season = df[dry_mask].copy()
        dry_season['saison_annee'] = dry_season.apply(get_dry_season_year, axis=1)
        dry_season['saison'] = 'Sèche'
        
        # Saison des pluies: juillet à novembre
        rainy_mask = (df['month'] >= 7) & (df['month'] <= 11)
        rainy_season = df[rainy_mask].copy()
        rainy_season['saison_annee'] = rainy_season.apply(get_rainy_season_year, axis=1)
        rainy_season['saison'] = 'Pluies'
        
        # Nettoyer les données
        dry_season = dry_season.dropna(subset=['saison_annee'])
        rainy_season = rainy_season.dropna(subset=['saison_annee'])
        
        self.dry_season_data = dry_season
        self.rainy_season_data = rainy_season
        
        return dry_season, rainy_season
    
    def get_season_years(self, season_type: str) -> list:
        """Retourne la liste des années de saison disponibles"""
        if season_type == 'dry':
            if self.dry_season_data is not None:
                return sorted(self.dry_season_data['saison_annee'].unique())
        elif season_type == 'rainy':
            if self.rainy_season_data is not None:
                return sorted(self.rainy_season_data['saison_annee'].unique())
        return []
    
    def get_season_data(self, season_type: str, year: str = None) -> pd.DataFrame:
        """Retourne les données pour une saison spécifique"""
        if season_type == 'dry':
            data = self.dry_season_data
        elif season_type == 'rainy':
            data = self.rainy_season_data
        else:
            return None
        
        if data is None:
            return None
        
        if year:
            return data[data['saison_annee'] == year].copy()
        return data.copy()
    
    def export_season_data(self, season_type: str, output_path: str):
        """Export les données de saison vers Excel"""
        data = self.get_season_data(season_type)
        if data is not None:
            data.to_excel(output_path, index=False)
            return True
        return False
    
    def get_statistics(self, season_type: str) -> Dict:
        """Retourne des statistiques sur les données de saison"""
        data = self.get_season_data(season_type)
        if data is None:
            return {}
        
        stats = {
            'nombre_annees': len(data['saison_annee'].unique()),
            'annees': list(data['saison_annee'].unique()),
            'date_debut': data['date'].min(),
            'date_fin': data['date'].max(),
            'nombre_observations': len(data)
        }
        
        return stats
