"""
Module de formule de prédiction pour les saisons des pluies et sèche.

SAISON DES PLUIES : Juillet → Novembre (153 jours)
SAISON SECHE : Décembre → Juin (212 jours)
"""

# Modules SAISON DES PLUIES
from backend.formula.formula_module import FormulaModule
from backend.formula.coefficients_module import CoefficientsModule
from backend.formula.calculator_module import CalculatorModule
from backend.formula.generator_module import GeneratorModule
from backend.formula.analyzer_module import AnalyzerModule

# Modules SAISON SECHE
from backend.formula.formula_module_seche import FormulaModuleSeche
from backend.formula.coefficients_module_seche import CoefficientsModuleSeche
from backend.formula.calculator_module_seche import CalculatorModuleSeche
from backend.formula.generator_module_seche import GeneratorModuleSeche
from backend.formula.analyzer_module_seche import AnalyzerModuleSeche

# Modules communs
from backend.formula.export_manager import ExportManager
from backend.formula.coefficient_extractor import CoefficientExtractor
from backend.formula.data_quality_validator import DataQualityValidator
from backend.formula.exceptions import (
    FormulaError,
    InvalidDayError,
    InvalidCoefficientError,
    InvalidEpsilonError,
    MissingDataError,
    ExportError,
    ValidationError,
    CalculationError
)

__all__ = [
    # Saison des pluies
    'FormulaModule',
    'CoefficientsModule',
    'CalculatorModule',
    'GeneratorModule',
    'AnalyzerModule',
    # Saison sèche
    'FormulaModuleSeche',
    'CoefficientsModuleSeche',
    'CalculatorModuleSeche',
    'GeneratorModuleSeche',
    'AnalyzerModuleSeche',
    # Modules communs
    'ExportManager',
    'CoefficientExtractor',
    'DataQualityValidator',
    # Exceptions
    'FormulaError',
    'InvalidDayError',
    'InvalidCoefficientError',
    'InvalidEpsilonError',
    'MissingDataError',
    'ExportError',
    'ValidationError',
    'CalculationError'
]
