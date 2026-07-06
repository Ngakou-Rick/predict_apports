"""
Exceptions personnalisées pour le module de formule.

Ce module définit la hiérarchie des exceptions pour une gestion
d'erreurs claire et structurée.
"""


class FormulaError(Exception):
    """Exception de base pour les erreurs de formule"""
    pass


class InvalidDayError(FormulaError):
    """Jour de saison invalide (hors 1-153)"""
    
    def __init__(self, day: int):
        self.day = day
        super().__init__(f"Jour invalide: {day}. Le jour de saison doit être entre 1 et 153")


class InvalidCoefficientError(FormulaError):
    """Coefficient annuel invalide (k(A) ≤ 0)"""
    
    def __init__(self, k_A: float):
        self.k_A = k_A
        super().__init__(f"Coefficient annuel invalide: {k_A}. Le coefficient doit être strictement positif (> 0)")


class InvalidEpsilonError(FormulaError):
    """Taux d'erreur invalide (hors 0.01-0.08)"""
    
    def __init__(self, epsilon: float):
        self.epsilon = epsilon
        super().__init__(f"Taux d'erreur invalide: {epsilon}. Le taux d'erreur doit être entre 0.01 et 0.08 (1% à 8%)")


class MissingDataError(FormulaError):
    """Données historiques manquantes"""
    
    def __init__(self, year: int = None, message: str = None):
        self.year = year
        if message:
            super().__init__(message)
        elif year:
            super().__init__(f"Données historiques manquantes pour l'année {year}")
        else:
            super().__init__("Données historiques manquantes")


class ExportError(Exception):
    """Erreur lors de l'export"""
    
    def __init__(self, message: str, filepath: str = None):
        self.filepath = filepath
        if filepath:
            super().__init__(f"Erreur lors de l'export vers {filepath}: {message}")
        else:
            super().__init__(f"Erreur lors de l'export: {message}")


class ValidationError(FormulaError):
    """Erreur de validation générique"""
    
    def __init__(self, message: str):
        super().__init__(f"Erreur de validation: {message}")


class CalculationError(FormulaError):
    """Erreur lors d'un calcul"""
    
    def __init__(self, message: str, details: str = None):
        self.details = details
        if details:
            super().__init__(f"Erreur de calcul: {message}. Détails: {details}")
        else:
            super().__init__(f"Erreur de calcul: {message}")
