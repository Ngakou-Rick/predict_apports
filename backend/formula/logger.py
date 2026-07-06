"""
Module de logging pour la formule de prédiction
"""
import logging
import os
from datetime import datetime


def setup_logger():
    """Configure le logger pour la formule de prédiction"""
    # Créer le dossier logs s'il n'existe pas
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Créer le logger
    logger = logging.getLogger('formula_predictions')
    logger.setLevel(logging.DEBUG)
    
    # Éviter les doublons de handlers
    if logger.handlers:
        return logger
    
    # Handler pour fichier
    log_filename = f'logs/formula_predictions_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Handler pour console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Format des logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Ajouter les handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
formula_logger = setup_logger()


def log_error(error_type, error_message, context=None):
    """
    Log une erreur avec contexte
    
    Args:
        error_type: Type d'erreur (validation, calcul, export, etc.)
        error_message: Message d'erreur
        context: Contexte additionnel (dict)
    """
    log_msg = f"[{error_type}] {error_message}"
    if context:
        log_msg += f" | Context: {context}"
    formula_logger.error(log_msg)


def log_warning(warning_type, warning_message, context=None):
    """
    Log un avertissement avec contexte
    
    Args:
        warning_type: Type d'avertissement
        warning_message: Message d'avertissement
        context: Contexte additionnel (dict)
    """
    log_msg = f"[{warning_type}] {warning_message}"
    if context:
        log_msg += f" | Context: {context}"
    formula_logger.warning(log_msg)


def log_info(info_type, info_message, context=None):
    """
    Log une information avec contexte
    
    Args:
        info_type: Type d'information
        info_message: Message d'information
        context: Contexte additionnel (dict)
    """
    log_msg = f"[{info_type}] {info_message}"
    if context:
        log_msg += f" | Context: {context}"
    formula_logger.info(log_msg)
