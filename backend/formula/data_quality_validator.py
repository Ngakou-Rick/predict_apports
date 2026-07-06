"""
Module de validation de la qualité des données historiques.

Ce module valide que les données historiques sont suffisantes et de qualité
pour extraire des coefficients fiables.
"""

import pandas as pd
from typing import Tuple, Dict, Any


class DataQualityValidator:
    """
    Validateur de qualité des données historiques.
    
    Vérifie:
    - Nombre d'années (minimum 10 ans recommandé)
    - Pourcentage de valeurs manquantes (maximum 15%)
    - Qualité de l'ajustement polynomial (R² >= 0.90)
    """
    
    MIN_YEARS = 10
    MAX_MISSING_PERCENTAGE = 15.0
    MIN_R_SQUARED = 0.90
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialise le validateur.
        
        Args:
            data: DataFrame avec colonnes ['date', 'debits', 'saison_annee']
        """
        self.data = data
        self.years_count = 0
        self.missing_percentage = 0.0
        self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calcule les métriques de base."""
        if self.data is not None and not self.data.empty:
            # Nombre d'années uniques
            if 'saison_annee' in self.data.columns:
                self.years_count = self.data['saison_annee'].nunique()
            
            # Pourcentage de valeurs manquantes
            if 'debits' in self.data.columns:
                total = len(self.data)
                missing = self.data['debits'].isna().sum()
                self.missing_percentage = (missing / total * 100) if total > 0 else 0.0
    
    def validate_years_count(self) -> Tuple[bool, str]:
        """
        Vérifie que les données couvrent au moins 10 ans.
        
        Returns:
            Tuple (is_valid, message)
        """
        is_valid = self.years_count >= self.MIN_YEARS
        
        if is_valid:
            message = f"✓ Données couvrent {self.years_count} années (>= {self.MIN_YEARS} requis)"
        else:
            message = f"⚠ Données couvrent seulement {self.years_count} années (minimum {self.MIN_YEARS} recommandé)"
        
        return (is_valid, message)
    
    def validate_missing_values(self) -> Tuple[bool, str]:
        """
        Vérifie que le % de valeurs manquantes est < 15%.
        
        Returns:
            Tuple (is_valid, message)
        """
        is_valid = self.missing_percentage <= self.MAX_MISSING_PERCENTAGE
        
        if is_valid:
            message = f"✓ Valeurs manquantes: {self.missing_percentage:.1f}% (<= {self.MAX_MISSING_PERCENTAGE}%)"
        else:
            message = f"⚠ Valeurs manquantes: {self.missing_percentage:.1f}% (maximum {self.MAX_MISSING_PERCENTAGE}% recommandé)"
        
        return (is_valid, message)
    
    def validate_polynomial_fit(self, r_squared: float) -> Tuple[bool, str]:
        """
        Vérifie que le R² du polynôme est >= 0.90.
        
        Args:
            r_squared: Coefficient de détermination
            
        Returns:
            Tuple (is_valid, message)
        """
        is_valid = r_squared >= self.MIN_R_SQUARED
        
        if is_valid:
            message = f"✓ Qualité ajustement polynomial: R² = {r_squared:.3f} (>= {self.MIN_R_SQUARED})"
        else:
            message = f"⚠ Qualité ajustement polynomial: R² = {r_squared:.3f} (minimum {self.MIN_R_SQUARED} recommandé)"
        
        return (is_valid, message)
    
    def calculate_quality_score(self) -> int:
        """
        Calcule un score de qualité global (0-100).
        
        Pondération:
        - Années: 40 points (10+ ans = 40, 5-9 ans = 20, <5 ans = 0)
        - Valeurs manquantes: 30 points (0-5% = 30, 5-15% = 15, >15% = 0)
        - Complétude: 30 points (basé sur continuité temporelle)
        
        Returns:
            Score entre 0 et 100
        """
        score = 0
        
        # Score années (40 points max)
        if self.years_count >= 10:
            score += 40
        elif self.years_count >= 5:
            score += 20
        
        # Score valeurs manquantes (30 points max)
        if self.missing_percentage <= 5.0:
            score += 30
        elif self.missing_percentage <= 15.0:
            score += 15
        
        # Score complétude (30 points max)
        # Basé sur la continuité des données
        if self.data is not None and not self.data.empty:
            if 'date' in self.data.columns:
                # Vérifier la continuité temporelle
                dates = pd.to_datetime(self.data['date'])
                date_range = (dates.max() - dates.min()).days
                expected_days = self.years_count * 365
                continuity_ratio = min(len(dates) / expected_days, 1.0) if expected_days > 0 else 0
                score += int(continuity_ratio * 30)
            else:
                score += 15  # Score partiel si pas de colonne date
        
        return min(score, 100)
    
    def get_validation_report(self) -> Dict[str, Any]:
        """
        Génère un rapport de validation complet.
        
        Returns:
            Dict contenant:
            - is_valid: bool
            - quality_score: int (0-100)
            - years_count: int
            - missing_percentage: float
            - warnings: List[str]
            - recommendations: List[str]
        """
        warnings = []
        recommendations = []
        
        # Validation années
        years_valid, years_msg = self.validate_years_count()
        if not years_valid:
            warnings.append(years_msg)
            recommendations.append("Ajoutez plus d'années de données historiques (minimum 10 ans recommandé)")
        
        # Validation valeurs manquantes
        missing_valid, missing_msg = self.validate_missing_values()
        if not missing_valid:
            warnings.append(missing_msg)
            recommendations.append("Complétez les valeurs manquantes ou utilisez une période différente")
        
        # Score de qualité
        quality_score = self.calculate_quality_score()
        
        # Validation globale
        is_valid = years_valid and missing_valid and quality_score >= 70
        
        return {
            'is_valid': is_valid,
            'quality_score': quality_score,
            'years_count': self.years_count,
            'missing_percentage': round(self.missing_percentage, 2),
            'warnings': warnings,
            'recommendations': recommendations
        }

