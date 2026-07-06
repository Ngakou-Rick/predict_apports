"""
Contrôleur principal de l'application (Backend)
"""
import pandas as pd
from typing import Dict, Tuple, Optional
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.seasonal_transformer import SeasonalTransformer
from analysis.flow_analyzer import FlowAnalyzer
from models.flow_predictor import FlowPredictor
from models.climate_analyzer import ClimateAnalyzer
from export.report_generator import ReportGenerator


class ApplicationController:
    """Contrôleur principal gérant toute la logique métier"""
    
    def __init__(self):
        self.transformer = SeasonalTransformer()
        self.report_generator = ReportGenerator()
        self.current_data = None
        self.dry_season_data = None
        self.rainy_season_data = None
        self.analysis_results = {}
        self.prediction_results = {}
        self.climate_results = {}
        
        # Coefficients extraits (ajouté pour Task 10)
        self.rainy_coefficients = None
        self.dry_coefficients = None
        
    def load_and_transform_data(self, file_path: str) -> Dict:
        """Charge et transforme les données en saisons"""
        try:
            # Charger les données
            df = self.transformer.load_data(file_path)
            self.current_data = df
            
            # Séparer par saison
            dry, rainy = self.transformer.split_by_season(df)
            self.dry_season_data = dry
            self.rainy_season_data = rainy
            
            # Statistiques
            dry_stats = self.transformer.get_statistics('dry')
            rainy_stats = self.transformer.get_statistics('rainy')
            
            # Extraire les coefficients (Task 10)
            from backend.formula.coefficient_extractor import CoefficientExtractor
            
            extraction_results = {
                'rainy': None,
                'dry': None
            }
            
            # Extraction saison des pluies
            if rainy is not None and not rainy.empty:
                try:
                    extractor_rainy = CoefficientExtractor('rainy', rainy)
                    self.rainy_coefficients = extractor_rainy.extract_all()
                    extraction_results['rainy'] = {
                        'success': True,
                        'quality_score': self.rainy_coefficients['quality_report']['quality_score'],
                        'warnings': self.rainy_coefficients['quality_report']['warnings']
                    }
                except Exception as e:
                    extraction_results['rainy'] = {
                        'success': False,
                        'error': str(e)
                    }
                    self.rainy_coefficients = None
            
            # Extraction saison sèche
            if dry is not None and not dry.empty:
                try:
                    extractor_dry = CoefficientExtractor('dry', dry)
                    self.dry_coefficients = extractor_dry.extract_all()
                    extraction_results['dry'] = {
                        'success': True,
                        'quality_score': self.dry_coefficients['quality_report']['quality_score'],
                        'warnings': self.dry_coefficients['quality_report']['warnings']
                    }
                except Exception as e:
                    extraction_results['dry'] = {
                        'success': False,
                        'error': str(e)
                    }
                    self.dry_coefficients = None
            
            return {
                'success': True,
                'message': 'Données chargées et transformées avec succès',
                'dry_season': {
                    'years': self.transformer.get_season_years('dry'),
                    'stats': dry_stats
                },
                'rainy_season': {
                    'years': self.transformer.get_season_years('rainy'),
                    'stats': rainy_stats
                },
                'extraction': extraction_results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur: {str(e)}'
            }
    
    def load_seasonal_data_direct(self, seasonal_df: pd.DataFrame) -> Dict:
        """
        Charge des données saisonnières déjà transformées et extrait les coefficients.
        
        Utilisé par Phase 2 qui charge directement un fichier saisonnier.
        
        Args:
            seasonal_df: DataFrame avec colonnes ['date', 'debits', 'saison_annee', 'saison']
        
        Returns:
            Dict avec résultats de l'extraction (toujours retourne un dict, jamais None)
        """
        # Initialiser le résultat par défaut
        default_result = {
            'success': False,
            'message': 'Erreur inconnue',
            'extraction': {'rainy': None, 'dry': None}
        }
        
        try:
            # Vérifier que le DataFrame n'est pas None ou vide
            if seasonal_df is None or seasonal_df.empty:
                return {
                    'success': False,
                    'message': 'DataFrame vide ou None',
                    'extraction': {'rainy': None, 'dry': None}
                }
            
            from backend.formula.coefficient_extractor import CoefficientExtractor
            
            # Normaliser le nom de la colonne debit → debits
            df = seasonal_df.copy()
            if 'debit' in df.columns and 'debits' not in df.columns:
                df['debits'] = df['debit']
            
            # Vérifier que les colonnes nécessaires existent
            required_cols = ['date', 'debits', 'saison_annee']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {
                    'success': False,
                    'message': f'Colonnes manquantes: {missing_cols}',
                    'extraction': {'rainy': None, 'dry': None}
                }
            
            # Séparer par saison
            if 'saison' in df.columns:
                rainy = df[df['saison'].str.contains('Pluies', case=False, na=False)]
                dry = df[df['saison'].str.contains('Sèche|Seche', case=False, na=False)]
            else:
                # Fallback: utiliser les mois
                df['date'] = pd.to_datetime(df['date'])
                rainy = df[df['date'].dt.month.isin([7, 8, 9, 10, 11])]
                dry = df[~df['date'].dt.month.isin([7, 8, 9, 10, 11])]
            
            extraction_results = {
                'rainy': None,
                'dry': None
            }
            
            # Extraction saison des pluies - SEULEMENT si assez de données (min 10 ans hydrologiques)
            if not rainy.empty and 'saison_annee' in rainy.columns:
                num_years_rainy = rainy['saison_annee'].nunique()
                if num_years_rainy >= 10:
                    try:
                        extractor_rainy = CoefficientExtractor('rainy', rainy)
                        self.rainy_coefficients = extractor_rainy.extract_all()
                        extraction_results['rainy'] = {
                            'success': True,
                            'quality_score': self.rainy_coefficients['quality_report']['quality_score'],
                            'warnings': self.rainy_coefficients['quality_report']['warnings']
                        }
                    except Exception as e:
                        extraction_results['rainy'] = {
                            'success': False,
                            'error': str(e)
                        }
                        self.rainy_coefficients = None
                else:
                    extraction_results['rainy'] = {
                        'success': False,
                        'error': f'Données insuffisantes: {num_years_rainy} années (min 10 requis)'
                    }
                    self.rainy_coefficients = None
            
            # Extraction saison sèche - SEULEMENT si assez de données (min 10 ans hydrologiques)
            if not dry.empty and 'saison_annee' in dry.columns:
                num_years_dry = dry['saison_annee'].nunique()
                if num_years_dry >= 10:
                    try:
                        extractor_dry = CoefficientExtractor('dry', dry)
                        self.dry_coefficients = extractor_dry.extract_all()
                        extraction_results['dry'] = {
                            'success': True,
                            'quality_score': self.dry_coefficients['quality_report']['quality_score'],
                            'warnings': self.dry_coefficients['quality_report']['warnings']
                        }
                    except Exception as e:
                        extraction_results['dry'] = {
                            'success': False,
                            'error': str(e)
                        }
                        self.dry_coefficients = None
                else:
                    extraction_results['dry'] = {
                        'success': False,
                        'error': f'Données insuffisantes: {num_years_dry} années (min 10 requis)'
                    }
                    self.dry_coefficients = None
            
            return {
                'success': True,
                'message': 'Coefficients extraits avec succès',
                'extraction': extraction_results
            }
            
        except Exception as e:
            # En cas d'erreur, toujours retourner un dict valide
            return {
                'success': False,
                'message': f'Erreur lors de l\'extraction: {str(e)}',
                'extraction': {'rainy': None, 'dry': None}
            }
    
    def get_season_data(self, season_type: str, year: Optional[str] = None) -> pd.DataFrame:
        """Récupère les données d'une saison"""
        return self.transformer.get_season_data(season_type, year)
    
    def analyze_flows(self, season_type: str, year: Optional[str] = None) -> Dict:
        """Analyse hydrologique des débits"""
        try:
            data = self.get_season_data(season_type, year)
            
            if data is None or len(data) == 0:
                return {'success': False, 'message': 'Aucune donnée disponible'}
            
            analyzer = FlowAnalyzer(data)
            results = analyzer.get_complete_analysis()
            
            # Stocker les résultats
            key = f"{season_type}_{year if year else 'all'}"
            self.analysis_results[key] = results
            
            return {
                'success': True,
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur analyse: {str(e)}'
            }
    
    def predict_flows(self, season_type: str, year: str, model_name: str) -> Dict:
        """Prédit les débits pour une année de saison"""
        try:
            data = self.get_season_data(season_type, year)
            
            if data is None or len(data) == 0:
                return {'success': False, 'message': 'Aucune donnée disponible'}
            
            # Créer et entraîner le modèle
            predictor = FlowPredictor(model_name)
            X, y = predictor.prepare_features(data)
            
            metrics = predictor.train(X, y)
            results = predictor.get_results()
            
            # Stocker les résultats
            key = f"{season_type}_{year}_{model_name}"
            self.prediction_results[key] = results
            
            return {
                'success': True,
                'results': results,
                'metrics': metrics
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur prédiction: {str(e)}'
            }
    
    def analyze_climate(self, season_type: str, year: Optional[str] = None, 
                       predicted_flows: Optional[pd.Series] = None) -> Dict:
        """Analyse climatique"""
        try:
            data = self.get_season_data(season_type, year)
            
            if data is None or len(data) == 0:
                return {'success': False, 'message': 'Aucune donnée disponible'}
            
            analyzer = ClimateAnalyzer(data)
            results = analyzer.get_complete_analysis()
            
            # Prédictions climatiques si débits prévus fournis
            if predicted_flows is not None:
                climate_predictions = analyzer.predict_climate_from_flow(predicted_flows)
                results['predictions'] = climate_predictions
            
            # Stocker les résultats
            key = f"{season_type}_{year if year else 'all'}"
            self.climate_results[key] = results
            
            return {
                'success': True,
                'results': results
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur analyse climat: {str(e)}'
            }
    
    def export_season_to_excel(self, season_type: str, output_path: str) -> bool:
        """Exporte les données de saison vers Excel"""
        return self.transformer.export_season_data(season_type, output_path)
    
    def export_predictions_excel(self, season_type: str, year: str, model_name: str, 
                                output_path: str) -> Dict:
        """Exporte les prédictions vers Excel"""
        try:
            key = f"{season_type}_{year}_{model_name}"
            
            if key not in self.prediction_results:
                return {'success': False, 'message': 'Aucune prédiction disponible'}
            
            results = self.prediction_results[key]
            
            # Préparer les données pour l'export
            export_data = {
                'predictions': pd.DataFrame({
                    'Réel': results['predictions']['test']['actual'],
                    'Prédit': results['predictions']['test']['predicted']
                }),
                'metrics': pd.DataFrame([results['metrics']['test']])
            }
            
            if results['feature_importance'] is not None:
                export_data['feature_importance'] = pd.DataFrame(results['feature_importance'])
            
            filepath = self.report_generator.export_to_excel(export_data, output_path)
            
            return {
                'success': True,
                'filepath': filepath
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur export: {str(e)}'
            }
    
    def export_complete_report_pdf(self, season_type: str, year: str, model_name: str,
                                   output_path: str) -> Dict:
        """Génère un rapport PDF complet"""
        try:
            key = f"{season_type}_{year}_{model_name}"
            
            if key not in self.prediction_results:
                return {'success': False, 'message': 'Aucune prédiction disponible'}
            
            results = self.prediction_results[key]
            
            # Créer les graphiques
            plot_paths = []
            
            # Graphique prédiction
            pred_plot = self.report_generator.create_prediction_plot(
                results['predictions']['test']['actual'],
                results['predictions']['test']['predicted'],
                f"Prédictions - {model_name}"
            )
            plot_paths.append(pred_plot)
            
            # Graphique corrélations si disponible
            climate_key = f"{season_type}_{year}"
            if climate_key in self.climate_results:
                corr_plot = self.report_generator.create_correlation_heatmap(
                    self.climate_results[climate_key]['correlations'],
                    "Corrélations Climat-Débits"
                )
                if corr_plot:
                    plot_paths.append(corr_plot)
            
            # Préparer les données pour le PDF
            pdf_data = {
                'season_info': {
                    'saison': 'Sèche' if season_type == 'dry' else 'Pluies',
                    'annee': year,
                    'modele': model_name
                },
                'metrics': results['metrics'],
                'plot_paths': plot_paths
            }
            
            filepath = self.report_generator.export_to_pdf(pdf_data, output_path)
            
            return {
                'success': True,
                'filepath': filepath
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Erreur export PDF: {str(e)}'
            }
    
    def get_available_years(self, season_type: str) -> list:
        """Retourne les années disponibles pour une saison"""
        return self.transformer.get_season_years(season_type)

    # Méthodes pour obtenir les modules de formules avec coefficients extraits (Task 11)
    
    def get_formula_module_rainy(self):
        """
        Retourne FormulaModule avec coefficients extraits ou par défaut.
        
        Returns:
            FormulaModule configuré avec les bons coefficients
        """
        from backend.formula.formula_module import FormulaModule
        
        if self.rainy_coefficients is not None:
            # Utiliser les coefficients extraits
            poly_coeffs = self.rainy_coefficients['polynomial_coeffs']
            # Retirer r_squared du dict pour ne garder que les coefficients
            poly_coeffs_clean = {k: v for k, v in poly_coeffs.items() if k != 'r_squared'}
            
            return FormulaModule(
                poly_coeffs=poly_coeffs_clean,
                monthly_coeffs=self.rainy_coefficients['monthly_coeffs'],
                Q_historical=self.rainy_coefficients['Q_historical'],
                epsilon=self.rainy_coefficients.get('epsilon', 0.05),
                daily_diff=self.rainy_coefficients.get('daily_diff', 16.5)
            )
        else:
            # Utiliser les coefficients Mbakaou par défaut
            return FormulaModule()
    
    def get_formula_module_dry(self):
        """
        Retourne FormulaModuleSeche avec coefficients extraits ou par défaut.
        
        Returns:
            FormulaModuleSeche configuré avec les bons coefficients
        """
        from backend.formula.formula_module_seche import FormulaModuleSeche
        
        if self.dry_coefficients is not None:
            # Utiliser les coefficients extraits
            poly_coeffs = self.dry_coefficients['polynomial_coeffs']
            # Retirer r_squared du dict pour ne garder que les coefficients
            poly_coeffs_clean = {k: v for k, v in poly_coeffs.items() if k != 'r_squared'}
            
            return FormulaModuleSeche(
                poly_coeffs=poly_coeffs_clean,
                monthly_coeffs=self.dry_coefficients['monthly_coeffs'],
                Q_historical=self.dry_coefficients['Q_historical'],
                epsilon=self.dry_coefficients.get('epsilon', 0.05),
                daily_diff=self.dry_coefficients.get('daily_diff', 16.5)
            )
        else:
            # Utiliser les coefficients Mbakaou par défaut
            return FormulaModuleSeche()
    
    def get_coefficients_info(self, season_type: str) -> Dict:
        """
        Retourne les informations sur les coefficients utilisés.
        
        Args:
            season_type: 'rainy' ou 'dry'
            
        Returns:
            Dict avec informations sur les coefficients
        """
        if season_type == 'rainy':
            if self.rainy_coefficients is not None:
                return {
                    'source': 'Extraits des données',
                    'quality_score': self.rainy_coefficients['quality_report']['quality_score'],
                    'warnings': self.rainy_coefficients['quality_report']['warnings'],
                    'Q_historical': self.rainy_coefficients['Q_historical'],
                    'r_squared': self.rainy_coefficients['polynomial_coeffs']['r_squared'],
                    'epsilon': self.rainy_coefficients.get('epsilon', 0.05)
                }
            else:
                return {
                    'source': 'Mbakaou (défaut)',
                    'Q_historical': 739.0,
                    'r_squared': 0.988,
                    'epsilon': 0.05
                }
        else:  # dry
            if self.dry_coefficients is not None:
                return {
                    'source': 'Extraits des données',
                    'quality_score': self.dry_coefficients['quality_report']['quality_score'],
                    'warnings': self.dry_coefficients['quality_report']['warnings'],
                    'Q_historical': self.dry_coefficients['Q_historical'],
                    'r_squared': self.dry_coefficients['polynomial_coeffs']['r_squared'],
                    'epsilon': self.dry_coefficients.get('epsilon', 0.05)
                }
            else:
                return {
                    'source': 'Mbakaou (défaut)',
                    'Q_historical': 98.2,
                    'r_squared': 0.994,
                    'epsilon': 0.05
                }
