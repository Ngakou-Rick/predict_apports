"""
Module de modélisation et prédiction des débits
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor
from statsmodels.tsa.statespace.sarimax import SARIMAX
from typing import Dict, Tuple, List
import warnings
import joblib
import time
warnings.filterwarnings('ignore')


class FlowPredictor:
    """Modélisation et prédiction des débits"""
    
    MODELS = {
        'Random Forest': RandomForestRegressor,
        'Régression Linéaire': LinearRegression,
        'AdaBoost': AdaBoostRegressor,
        'XGBoost': XGBRegressor,
        'SARIMA': 'sarima'
    }
    
    def __init__(self, model_name: str = 'Random Forest'):
        self.model_name = model_name
        self.model = None
        self.feature_importance = None
        self.predictions = None
        self.metrics = None
        
        # Initialiser le modèle (sauf SARIMA qui nécessite les données)
        if model_name != 'SARIMA':
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialise le modèle ML"""
        model_class = self.MODELS[self.model_name]
        
        if self.model_name == 'Random Forest':
            self.model = model_class(n_estimators=100, random_state=42, n_jobs=-1)
        elif self.model_name == 'XGBoost':
            self.model = model_class(n_estimators=100, random_state=42, n_jobs=-1)
        elif self.model_name == 'AdaBoost':
            self.model = model_class(n_estimators=100, random_state=42)
        else:
            self.model = model_class()
        
    def prepare_features(self, df: pd.DataFrame, lag_days: int = 7) -> Tuple[pd.DataFrame, pd.Series]:
        """Prépare les features pour la modélisation"""
        data = df.copy()
        
        # Identifier la colonne débit
        debit_col = None
        for col in data.columns:
            if 'debit' in col.lower() or 'q' == col.lower():
                debit_col = col
                break
        
        if debit_col is None:
            raise ValueError("Colonne débit non trouvée")
        
        # Créer les lag features
        for i in range(1, lag_days + 1):
            data[f'debit_lag_{i}'] = data[debit_col].shift(i)
        
        # Features temporelles
        if 'date' in data.columns:
            data['jour_annee'] = data['date'].dt.dayofyear
            data['mois'] = data['date'].dt.month
            data['jour_mois'] = data['date'].dt.day
        
        # Features climatiques si disponibles
        climate_features = []
        for col in data.columns:
            if any(x in col.lower() for x in ['pluie', 'etp', 'temp', 'temperature']):
                climate_features.append(col)
        
        # Supprimer les lignes avec NaN
        data = data.dropna()
        
        # Séparer features et target
        feature_cols = [f'debit_lag_{i}' for i in range(1, lag_days + 1)]
        feature_cols += ['jour_annee', 'mois', 'jour_mois'] if 'date' in df.columns else []
        feature_cols += climate_features
        
        X = data[feature_cols]
        y = data[debit_col]
        
        return X, y
    
    def train(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2) -> Dict:
        """Entraîne le modèle"""
        if test_size > 0:
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, shuffle=False
            )
        else:
            X_train, y_train = X, y
            X_test, y_test = X, y
        
        if self.model_name == 'SARIMA':
            return self._train_sarima(y_train, y_test)
        
        # Modèles ML - le modèle est déjà initialisé
        if self.model is None:
            self._initialize_model()
        
        self.model.fit(X_train, y_train)
        
        # Prédictions
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        
        # Métriques
        self.metrics = {
            'train': {
                'RMSE': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                'MAE': mean_absolute_error(y_train, y_pred_train),
                'R2': r2_score(y_train, y_pred_train)
            },
            'test': {
                'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                'MAE': mean_absolute_error(y_test, y_pred_test),
                'R2': r2_score(y_test, y_pred_test)
            }
        }
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.DataFrame({
                'feature': X.columns,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
        
        # Stocker les prédictions
        self.predictions = {
            'train': {'actual': y_train, 'predicted': y_pred_train},
            'test': {'actual': y_test, 'predicted': y_pred_test}
        }
        
        return self.metrics
    
    def _train_sarima(self, y_train: pd.Series, y_test: pd.Series) -> Dict:
        """Entraîne un modèle SARIMA"""
        try:
            self.model = SARIMAX(
                y_train,
                order=(1, 1, 1),
                seasonal_order=(1, 1, 1, 12),
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            self.model = self.model.fit(disp=False)
            
            # Prédictions
            y_pred_train = self.model.fittedvalues
            y_pred_test = self.model.forecast(steps=len(y_test))
            
            # Métriques
            self.metrics = {
                'train': {
                    'RMSE': np.sqrt(mean_squared_error(y_train, y_pred_train)),
                    'MAE': mean_absolute_error(y_train, y_pred_train),
                    'R2': r2_score(y_train, y_pred_train)
                },
                'test': {
                    'RMSE': np.sqrt(mean_squared_error(y_test, y_pred_test)),
                    'MAE': mean_absolute_error(y_test, y_pred_test),
                    'R2': r2_score(y_test, y_pred_test)
                }
            }
            
            self.predictions = {
                'train': {'actual': y_train, 'predicted': y_pred_train},
                'test': {'actual': y_test, 'predicted': y_pred_test}
            }
            
            return self.metrics
        except Exception as e:
            raise Exception(f"Erreur SARIMA: {str(e)}")
    
    def predict_future(self, X_future: pd.DataFrame) -> np.ndarray:
        """Prédit les débits futurs"""
        if self.model is None:
            raise ValueError("Le modèle doit être entraîné d'abord")
        
        if self.model_name == 'SARIMA':
            return self.model.forecast(steps=len(X_future))
        
        return self.model.predict(X_future)
    
    def get_results(self) -> Dict:
        """Retourne tous les résultats"""
        return {
            'model_name': self.model_name,
            'metrics': self.metrics,
            'feature_importance': self.feature_importance.to_dict() if self.feature_importance is not None else None,
            'predictions': self.predictions
        }
    
    def optimize(self, X_train: pd.DataFrame, y_train: pd.Series, 
                 X_test: pd.DataFrame, y_test: pd.Series,
                 param_grid: Dict, max_iterations: int = 50,
                 progress_callback=None) -> Dict:
        """
        Optimise le modèle en testant différentes configurations
        
        Args:
            X_train, y_train: Données d'entraînement
            X_test, y_test: Données de test
            param_grid: Dictionnaire des paramètres à tester
            max_iterations: Nombre maximum d'itérations
            progress_callback: Fonction appelée à chaque itération
        
        Returns:
            Dictionnaire avec historique et meilleure configuration
        """
        history = []
        best_r2 = -float('inf')
        best_params = None
        best_model = None
        
        # Générer toutes les combinaisons de paramètres
        param_combinations = self._generate_param_combinations(param_grid)
        total_iterations = min(len(param_combinations), max_iterations)
        
        for iteration, params in enumerate(param_combinations[:max_iterations], 1):
            start_time = time.time()
            
            try:
                # Créer et entraîner le modèle avec ces paramètres
                if self.model_name == 'SARIMA':
                    # SARIMA nécessite un traitement spécial
                    continue
                
                # Créer le modèle avec les paramètres
                model = self._create_model_with_params(params)
                model.fit(X_train, y_train)
                
                # Prédictions
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
                
                # Métriques
                train_r2 = r2_score(y_train, y_pred_train)
                train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
                train_mae = mean_absolute_error(y_train, y_pred_train)
                
                test_r2 = r2_score(y_test, y_pred_test)
                test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
                test_mae = mean_absolute_error(y_test, y_pred_test)
                
                elapsed_time = time.time() - start_time
                
                # Enregistrer l'itération
                iteration_result = {
                    'iteration': iteration,
                    'params': params.copy(),
                    'train_r2': train_r2,
                    'train_rmse': train_rmse,
                    'train_mae': train_mae,
                    'test_r2': test_r2,
                    'test_rmse': test_rmse,
                    'test_mae': test_mae,
                    'time': elapsed_time
                }
                history.append(iteration_result)
                
                # Mettre à jour le meilleur modèle
                if test_r2 > best_r2:
                    best_r2 = test_r2
                    best_params = params.copy()
                    best_model = model
                    iteration_result['is_best'] = True
                else:
                    iteration_result['is_best'] = False
                
                # Callback pour mise à jour interface
                if progress_callback:
                    progress_callback(iteration, total_iterations, iteration_result, best_r2)
                
            except Exception as e:
                print(f"Erreur itération {iteration}: {e}")
                continue
        
        # Sauvegarder le meilleur modèle
        self.model = best_model
        self.metrics = {
            'train': {
                'R2': history[-1]['train_r2'] if history else 0,
                'RMSE': history[-1]['train_rmse'] if history else 0,
                'MAE': history[-1]['train_mae'] if history else 0
            },
            'test': {
                'R2': best_r2,
                'RMSE': min([h['test_rmse'] for h in history if h['is_best']]) if history else 0,
                'MAE': min([h['test_mae'] for h in history if h['is_best']]) if history else 0
            }
        }
        
        return {
            'history': history,
            'best_params': best_params,
            'best_r2': best_r2,
            'total_iterations': len(history)
        }
    
    def _generate_param_combinations(self, param_grid: Dict) -> List[Dict]:
        """Génère toutes les combinaisons de paramètres"""
        import itertools
        
        keys = param_grid.keys()
        values = param_grid.values()
        combinations = []
        
        for combination in itertools.product(*values):
            combinations.append(dict(zip(keys, combination)))
        
        return combinations
    
    def _create_model_with_params(self, params: Dict):
        """Crée un modèle avec les paramètres spécifiés"""
        if self.model_name == 'Random Forest':
            return RandomForestRegressor(**params, random_state=42, n_jobs=-1)
        elif self.model_name == 'XGBoost':
            return XGBRegressor(**params, random_state=42, n_jobs=-1)
        elif self.model_name == 'AdaBoost':
            return AdaBoostRegressor(**params, random_state=42)
        elif self.model_name == 'Régression Linéaire':
            return LinearRegression(**params)
        else:
            return LinearRegression()
    
    def save_model(self, filepath: str) -> bool:
        """Sauvegarde le modèle"""
        try:
            joblib.dump(self.model, filepath)
            return True
        except Exception as e:
            print(f"Erreur sauvegarde: {e}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """Charge un modèle sauvegardé"""
        try:
            self.model = joblib.load(filepath)
            return True
        except Exception as e:
            print(f"Erreur chargement: {e}")
            return False
