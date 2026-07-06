"""
PHASE 2: Analyse et Prédiction
Application pour analyser et prédire l'année suivante
"""
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit,
                             QComboBox, QSpinBox, QGroupBox, QTabWidget, QTableWidget,
                             QTableWidgetItem, QDialog, QDialogButtonBox, QFormLayout,
                             QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
import sys
import os
import pandas as pd

from backend.data_processing.seasonal_transformer import SeasonalTransformer
from backend.analysis.flow_analyzer import FlowAnalyzer
from backend.models.flow_predictor import FlowPredictor
from backend.models.climate_analyzer import ClimateAnalyzer
from backend.export.report_generator import ReportGenerator
from backend.core.application_controller import ApplicationController


# Grilles de paramètres par modèle
PARAM_GRIDS = {
    'Random Forest': {
        'n_estimators': [50, 100, 200],
        'max_depth': [10, 20, 30, None],
        'min_samples_split': [2, 5, 10]
    },
    'XGBoost': {
        'n_estimators': [50, 100, 200],
        'max_depth': [3, 5, 7],
        'learning_rate': [0.01, 0.1, 0.3]
    },
    'Régression Linéaire': {
        'fit_intercept': [True, False]
    },
    'AdaBoost': {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.5, 1.0, 1.5]
    },
    'SARIMA': {
        'order': [(1, 1, 1), (2, 1, 1)],
        'seasonal_order': [(1, 1, 1, 12), (2, 1, 1, 12)]
    }
}


class ParameterSelectionDialog(QDialog):
    """Dialogue pour la sélection manuelle des paramètres à tester"""
    
    def __init__(self, model_name, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        self.param_widgets = {}
        self.max_iterations = 50
        
        self.setWindowTitle(f"Configuration des paramètres - {model_name}")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel(f"Sélectionnez les paramètres à tester pour {self.model_name}")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 10px;")
        layout.addWidget(title)
        
        # Formulaire de paramètres
        form_layout = QFormLayout()
        
        if self.model_name in PARAM_GRIDS:
            param_grid = PARAM_GRIDS[self.model_name]
            
            for param_name, param_values in param_grid.items():
                # Créer un groupe de checkboxes pour chaque paramètre
                param_group = QWidget()
                param_layout = QVBoxLayout(param_group)
                param_layout.setContentsMargins(0, 0, 0, 0)
                
                checkboxes = []
                for value in param_values:
                    cb = QCheckBox(str(value))
                    cb.setChecked(True)  # Sélectionné par défaut
                    checkboxes.append(cb)
                    param_layout.addWidget(cb)
                
                self.param_widgets[param_name] = checkboxes
                form_layout.addRow(f"{param_name}:", param_group)
        
        layout.addLayout(form_layout)
        
        # Nombre maximum d'itérations
        iter_layout = QHBoxLayout()
        iter_layout.addWidget(QLabel("Nombre maximum d'itérations:"))
        self.spin_max_iter = QSpinBox()
        self.spin_max_iter.setMinimum(1)
        self.spin_max_iter.setMaximum(1000)
        self.spin_max_iter.setValue(50)
        iter_layout.addWidget(self.spin_max_iter)
        layout.addLayout(iter_layout)
        
        # Boutons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_param_grid(self):
        """Retourne la grille de paramètres sélectionnée"""
        param_grid = {}
        
        if self.model_name in PARAM_GRIDS:
            original_grid = PARAM_GRIDS[self.model_name]
            
            for param_name, checkboxes in self.param_widgets.items():
                selected_values = []
                original_values = original_grid[param_name]
                
                for i, cb in enumerate(checkboxes):
                    if cb.isChecked():
                        value = original_values[i]
                        selected_values.append(value)
                
                if selected_values:
                    param_grid[param_name] = selected_values
        
        return param_grid
    
    def get_max_iterations(self):
        """Retourne le nombre maximum d'itérations"""
        return self.spin_max_iter.value()


class TrainingWorker(QThread):
    """Worker thread pour l'entraînement non-bloquant du modèle"""
    
    # Signaux
    progress_update = pyqtSignal(int, int, dict, float)  # iteration, total, metrics, best_r2
    training_complete = pyqtSignal(dict)  # optimization_results
    training_error = pyqtSignal(str)  # error_message
    
    def __init__(self, predictor, X_train, y_train, X_test, y_test, param_grid, max_iterations):
        super().__init__()
        self.predictor = predictor
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.param_grid = param_grid
        self.max_iterations = max_iterations
    
    def run(self):
        """Exécute l'optimisation dans un thread séparé"""
        try:
            # Callback pour les mises à jour de progression
            def progress_callback(iteration, total, metrics, best_r2):
                self.progress_update.emit(iteration, total, metrics, best_r2)
            
            # Lancer l'optimisation
            optimization_results = self.predictor.optimize(
                self.X_train,
                self.y_train,
                self.X_test,
                self.y_test,
                self.param_grid,
                self.max_iterations,
                progress_callback
            )
            
            # Émettre le signal de complétion
            self.training_complete.emit(optimization_results)
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.training_error.emit(error_msg)


class ProgressDialog(QDialog):
    """Dialogue pour afficher la progression de l'entraînement"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Entraînement en cours...")
        self.setModal(True)
        self.setMinimumWidth(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🎯 Optimisation du modèle en cours")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Labels d'information
        info_group = QGroupBox("Informations")
        info_layout = QFormLayout(info_group)
        
        self.label_iteration = QLabel("0 / 0")
        self.label_current_r2 = QLabel("N/A")
        self.label_best_r2 = QLabel("N/A")
        self.label_current_rmse = QLabel("N/A")
        self.label_current_mae = QLabel("N/A")
        
        info_layout.addRow("Itération:", self.label_iteration)
        info_layout.addRow("R² actuel:", self.label_current_r2)
        info_layout.addRow("Meilleur R²:", self.label_best_r2)
        info_layout.addRow("RMSE actuel:", self.label_current_rmse)
        info_layout.addRow("MAE actuel:", self.label_current_mae)
        
        layout.addWidget(info_group)
        
        # Bouton Annuler
        self.btn_cancel = QPushButton("Annuler")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        layout.addWidget(self.btn_cancel)
    
    def update_progress(self, iteration, total, metrics, best_r2):
        """Met à jour l'affichage de la progression"""
        # Mettre à jour la barre de progression
        progress_percent = int((iteration / total) * 100)
        self.progress_bar.setValue(progress_percent)
        
        # Mettre à jour les labels
        self.label_iteration.setText(f"{iteration} / {total}")
        self.label_current_r2.setText(f"{metrics.get('test_r2', 0):.4f}")
        self.label_best_r2.setText(f"{best_r2:.4f}")
        self.label_current_rmse.setText(f"{metrics.get('test_rmse', 0):.4f}")
        self.label_current_mae.setText(f"{metrics.get('test_mae', 0):.4f}")


class SeasonSelectionDialog(QDialog):
    """Dialogue pour choisir entre Saison Sèche et Saison des Pluies"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_season = None
        self.setWindowTitle("Sélection de la Saison")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Titre principal
        title = QLabel("🌍 Sélection de la Saison")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Choisissez la saison pour laquelle vous souhaitez générer des prédictions")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setStyleSheet("color: #666; padding-bottom: 20px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Conteneur pour les boutons de saisons
        seasons_widget = QWidget()
        seasons_layout = QVBoxLayout(seasons_widget)
        seasons_layout.setSpacing(15)
        
        # Bouton Saison Sèche
        btn_dry = QPushButton("🌵 SAISON SÈCHE\n\nDécembre → Juin (212 jours)\nR² = 0.994")
        btn_dry.setMinimumHeight(120)
        btn_dry.setFont(QFont("Arial", 13, QFont.Bold))
        btn_dry.setStyleSheet("""
            QPushButton {
                background-color: #d97706;
                color: white;
                border: none;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ea580c;
                border: 3px solid #1f4788;
            }
            QPushButton:pressed {
                background-color: #c2410c;
            }
        """)
        btn_dry.clicked.connect(lambda: self.select_season('dry'))
        seasons_layout.addWidget(btn_dry)
        
        # Bouton Saison des Pluies
        btn_rainy = QPushButton("🌧️ SAISON DES PLUIES\n\nJuillet → Novembre (153 jours)\nR² = 0.988")
        btn_rainy.setMinimumHeight(120)
        btn_rainy.setFont(QFont("Arial", 13, QFont.Bold))
        btn_rainy.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 20px;
                text-align: center;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
                border: 3px solid #1f4788;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)
        btn_rainy.clicked.connect(lambda: self.select_season('rainy'))
        seasons_layout.addWidget(btn_rainy)
        
        layout.addWidget(seasons_widget)
        
        # Bouton Annuler
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
    
    def select_season(self, season):
        """Sélectionne une saison et ferme le dialogue"""
        self.selected_season = season
        self.accept()
    
    def get_selected_season(self):
        """Retourne la saison sélectionnée ('dry' ou 'rainy') ou None si annulé"""
        return self.selected_season


class PhaseSelectionDialog(QDialog):
    """Dialogue de sélection des 5 phases de prédiction"""
    
    def __init__(self, parent=None, season='rainy'):
        super().__init__(parent)
        self.selected_phase = None
        self.season = season
        season_name = "SAISON SÈCHE" if season == 'dry' else "SAISON DES PLUIES"
        season_icon = "🌵" if season == 'dry' else "🌧️"
        
        self.setWindowTitle(f"Formule de Prédiction - {season_name}")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface du dialogue"""
        layout = QVBoxLayout(self)
        
        # Afficher la saison sélectionnée
        season_name = "SAISON SÈCHE" if self.season == 'dry' else "SAISON DES PLUIES"
        season_icon = "🌵" if self.season == 'dry' else "🌧️"
        season_color = "#d97706" if self.season == 'dry' else "#2563eb"
        
        season_label = QLabel(f"{season_icon} {season_name}")
        season_label.setFont(QFont("Arial", 14, QFont.Bold))
        season_label.setStyleSheet(f"color: {season_color}; padding: 10px; background-color: rgba(255,255,255,0.8); border-radius: 5px;")
        season_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(season_label)
        
        # Titre principal
        title = QLabel("🔮 Formule de Prédiction à 5 Phases")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 15px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sous-titre
        subtitle = QLabel("Sélectionnez une phase pour commencer")
        subtitle.setFont(QFont("Arial", 11))
        subtitle.setStyleSheet("color: #666; padding-bottom: 10px;")
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        # Conteneur pour les boutons de phases
        phases_widget = QWidget()
        phases_layout = QVBoxLayout(phases_widget)
        phases_layout.setSpacing(10)
        
        # Définir les phases avec leurs descriptions
        phases = [
            {
                'number': 1,
                'title': 'Phase 1: Formule Maîtresse',
                'description': 'Calculer Q(t,A) avec le polynôme d\'ordre 6',
                'icon': '📐',
                'color': '#007bff'
            },
            {
                'number': 2,
                'title': 'Phase 2: Coefficients',
                'description': 'Afficher les tableaux des coefficients annuels et mensuels',
                'icon': '📊',
                'color': '#28a745'
            },
            {
                'number': 3,
                'title': 'Phase 3: Calculateur',
                'description': 'Calculer le débit pour un jour spécifique',
                'icon': '🧮',
                'color': '#17a2b8'
            },
            {
                'number': 4,
                'title': 'Phase 4: Tableau Complet',
                'description': 'Générer le tableau de 153 jours avec export Excel/PDF',
                'icon': '📋',
                'color': '#6f42c1'
            },
            {
                'number': 5,
                'title': 'Phase 5: Analyse Comparative',
                'description': 'Classements annuels et mensuels',
                'icon': '📈',
                'color': '#fd7e14'
            }
        ]
        
        # Créer un bouton pour chaque phase
        for phase in phases:
            # Conteneur horizontal pour le bouton et l'aide
            phase_container = QWidget()
            phase_layout = QHBoxLayout(phase_container)
            phase_layout.setContentsMargins(0, 0, 0, 0)
            phase_layout.setSpacing(5)
            
            btn = QPushButton(f"{phase['icon']} {phase['title']}")
            btn.setMinimumHeight(70)
            btn.setFont(QFont("Arial", 11, QFont.Bold))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {phase['color']};
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: {phase['color']}dd;
                    border: 2px solid #1f4788;
                }}
                QPushButton:pressed {{
                    background-color: {phase['color']}aa;
                }}
            """)
            btn.setToolTip(phase['description'])
            btn.clicked.connect(lambda checked, p=phase['number']: self.select_phase(p))
            phase_layout.addWidget(btn, stretch=10)
            
            # Bouton d'aide
            btn_help = QPushButton("?")
            btn_help.setFixedSize(70, 70)
            btn_help.setFont(QFont("Arial", 16, QFont.Bold))
            btn_help.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    border: none;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
            """)
            btn_help.setToolTip("Afficher l'aide pour cette phase")
            btn_help.clicked.connect(lambda checked, p=phase['number']: self.show_help(p))
            phase_layout.addWidget(btn_help, stretch=1)
            
            phases_layout.addWidget(phase_container)
        
        layout.addWidget(phases_widget)
        
        # Bouton Annuler
        btn_cancel = QPushButton("❌ Annuler")
        btn_cancel.setMinimumHeight(40)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        layout.addWidget(btn_cancel)
    
    def select_phase(self, phase_number):
        """Sélectionne une phase et ferme le dialogue"""
        self.selected_phase = phase_number
        self.accept()
    
    def show_help(self, phase_number):
        """Affiche l'aide pour une phase spécifique"""
        from backend.formula.help_texts import get_help_text
        from PyQt5.QtWidgets import QTextBrowser
        
        help_data = get_help_text(phase_number)
        if not help_data:
            QMessageBox.warning(self, "Erreur", f"Aide non disponible pour la phase {phase_number}")
            return
        
        # Créer un dialogue d'aide
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle(help_data['title'])
        help_dialog.setModal(True)
        help_dialog.setMinimumWidth(700)
        help_dialog.setMinimumHeight(600)
        
        layout = QVBoxLayout(help_dialog)
        
        # Navigateur de texte pour afficher le HTML
        browser = QTextBrowser()
        browser.setHtml(help_data['content'])
        browser.setOpenExternalLinks(True)
        layout.addWidget(browser)
        
        # Bouton Fermer
        btn_close = QPushButton("Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_close.clicked.connect(help_dialog.close)
        layout.addWidget(btn_close)
        
        help_dialog.exec_()
    
    def get_selected_phase(self):
        """Retourne la phase sélectionnée (1-5) ou None si annulé"""
        return self.selected_phase


class PredictionWindow(QMainWindow):
    """Fenêtre de prédiction Phase 2"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 2 - Analyse et Prédiction")
        self.setGeometry(100, 100, 1200, 800)
        
        self.data = None
        self.years = []
        self.predictor = None
        self.future_predictions = None  # Stockage des prédictions futures
        self.report_gen = ReportGenerator()
        self.selected_formula_season = 'rainy'  # Saison par défaut pour les formules
        self.controller = ApplicationController()  # Contrôleur pour extraction des coefficients
        
        # Suivi des phases visitées pour activer le rapport final
        self.phases_visited = {
            'phase2': False,  # Analyse des données
            'phase4': False,  # Prédictions formule
            'phase5': False   # Analyse comparative
        }
        
        self.init_ui()
    
    def check_and_enable_final_report(self):
        """Vérifie si toutes les phases sont visitées et active le bouton rapport final"""
        if all(self.phases_visited.values()):
            self.btn_export_report.setEnabled(True)
            self.status_label.setText("✅ Toutes les phases visitées - Rapport final disponible!")
            QMessageBox.information(
                self, 
                "Rapport Final Disponible", 
                "🎉 Vous avez visité toutes les phases nécessaires!\n\n"
                "Le bouton 'Exporter Rapport Final' est maintenant activé.\n"
                "Cliquez dessus pour générer votre rapport PDF complet."
            )
    
    def init_ui(self):
        """Initialise l'interface"""
        # Définir l'image de fond avec opacité
        self.set_background_image()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Titre
        title = QLabel("🎯 Analyse et Prédiction de l'Année Suivante")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1f4788; padding: 20px;")
        main_layout.addWidget(title)
        
        # Panneau de contrôle
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_info_tab(), "📊 Informations")
        self.tabs.addTab(self.create_analysis_tab(), "📈 Analyse")
        self.tabs.addTab(self.create_prediction_tab(), "🎯 Prédiction")
        self.tabs.addTab(self.create_climate_tab(), "🌧️ Climat")
        main_layout.addWidget(self.tabs)
        
        # Statut
        self.status_label = QLabel("En attente du fichier saisonnier...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-style: italic;")
        main_layout.addWidget(self.status_label)
        
        # Bouton de navigation vers Phase 1
        self.btn_goto_phase1 = QPushButton("⬅️ Retour à Phase 1 (Transformation)")
        self.btn_goto_phase1.setStyleSheet(self.get_button_style("#ff6b6b"))
        self.btn_goto_phase1.clicked.connect(self.goto_phase1)
        main_layout.addWidget(self.btn_goto_phase1)
    
    def create_control_panel(self):
        """Crée le panneau de contrôle"""
        panel = QGroupBox("Contrôles")
        layout = QVBoxLayout(panel)
        
        # Ligne 1: Chargement
        row1 = QHBoxLayout()
        self.btn_load = QPushButton("📁 Charger Fichier Saisonnier")
        self.btn_load.clicked.connect(self.load_seasonal_file)
        self.btn_load.setStyleSheet(self.get_button_style("#1f4788"))
        row1.addWidget(self.btn_load)
        layout.addLayout(row1)
        
        # Ligne 2: Actions
        row2 = QHBoxLayout()
        
        self.btn_analyze = QPushButton("🔍 Analyser")
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_analyze.setStyleSheet(self.get_button_style("#28a745"))
        row2.addWidget(self.btn_analyze)
        
        self.btn_generate_predictions_formula = QPushButton("🔮 Générer Prédictions (Formule)")
        self.btn_generate_predictions_formula.setEnabled(False)
        self.btn_generate_predictions_formula.clicked.connect(self.generate_predictions_formula)
        self.btn_generate_predictions_formula.setStyleSheet(self.get_button_style("#6f42c1"))
        self.btn_generate_predictions_formula.setToolTip("Générer prédictions avec formule mathématique (pas besoin d'entraînement)")
        row2.addWidget(self.btn_generate_predictions_formula)
        
        self.btn_export_report = QPushButton("📈 Exporter Rapport Final")
        self.btn_export_report.setEnabled(False)
        self.btn_export_report.clicked.connect(self.export_final_report)
        self.btn_export_report.setStyleSheet(self.get_button_style("#28a745"))
        row2.addWidget(self.btn_export_report)
        
        layout.addLayout(row2)
        
        # Ligne 5: Save/Load Model
        row5 = QHBoxLayout()
        
        self.btn_save_model = QPushButton("💾 Sauvegarder Modèle")
        self.btn_save_model.setEnabled(False)
        self.btn_save_model.clicked.connect(self.save_model)
        self.btn_save_model.setStyleSheet(self.get_button_style("#6c757d"))
        row5.addWidget(self.btn_save_model)
        
        self.btn_load_model = QPushButton("📂 Charger Modèle")
        self.btn_load_model.setEnabled(True)
        self.btn_load_model.clicked.connect(self.load_model)
        self.btn_load_model.setStyleSheet(self.get_button_style("#6c757d"))
        row5.addWidget(self.btn_load_model)
        
        layout.addLayout(row5)
        
        return panel
    
    def create_info_tab(self):
        """Onglet informations"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        return tab
    
    def create_analysis_tab(self):
        """Onglet analyse"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        self.analysis_text.setStyleSheet("font-family: Consolas;")
        layout.addWidget(self.analysis_text)
        return tab
    
    def create_prediction_tab(self):
        """Onglet prédiction"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.prediction_text = QTextEdit()
        self.prediction_text.setReadOnly(True)
        self.prediction_text.setStyleSheet("font-family: Consolas;")
        layout.addWidget(self.prediction_text)
        return tab
    
    def create_climate_tab(self):
        """Onglet climat"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.climate_text = QTextEdit()
        self.climate_text.setReadOnly(True)
        self.climate_text.setStyleSheet("font-family: Consolas;")
        layout.addWidget(self.climate_text)
        return tab
    
    def get_button_style(self, color):
        """Style des boutons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """
    
    def load_seasonal_file(self):
        """Charge le fichier saisonnier"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier saisonnier", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                self.data = pd.read_excel(file_path)
                self.data.columns = self.data.columns.str.strip().str.lower()
                
                # Normaliser le nom de la colonne debit → debits
                if 'debit' in self.data.columns and 'debits' not in self.data.columns:
                    self.data['debits'] = self.data['debit']
                
                # Convertir les colonnes numériques
                numeric_cols = ['debits', 'pluie', 'tmax', 'tmin', 'etp']
                for col in numeric_cols:
                    if col in self.data.columns:
                        self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
                
                # Convertir la date
                if 'date' in self.data.columns:
                    self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')
                
                # NOUVEAU: Charger les données via le contrôleur pour extraire les coefficients
                # Utiliser load_seasonal_data_direct car c'est un fichier déjà transformé
                try:
                    result = self.controller.load_seasonal_data_direct(self.data)
                    if result and result.get('success'):
                        print("✅ Coefficients extraits via ApplicationController")
                        
                        # Afficher les résultats de l'extraction
                        extraction = result.get('extraction', {})
                        if extraction:
                            rainy_result = extraction.get('rainy')
                            dry_result = extraction.get('dry')
                            
                            if rainy_result and rainy_result.get('success'):
                                print(f"   ✓ Saison pluvieuse: Score qualité = {rainy_result['quality_score']}/100")
                            if dry_result and dry_result.get('success'):
                                print(f"   ✓ Saison sèche: Score qualité = {dry_result['quality_score']}/100")
                    else:
                        msg = result.get('message', 'Erreur inconnue') if result else 'Aucun résultat'
                        print(f"⚠️ Extraction des coefficients échouée: {msg}")
                except Exception as e:
                    print(f"⚠️ Extraction des coefficients échouée: {e}")
                    import traceback
                    traceback.print_exc()
                    # Continuer même si l'extraction échoue (utilise Mbakaou par défaut)
                
                # Identifier les années
                if 'saison_annee' in self.data.columns:
                    self.years = sorted(self.data['saison_annee'].unique())
                    
                    # Afficher les informations
                    info = f"""
Fichier chargé: {os.path.basename(file_path)}
Total observations: {len(self.data)}
Nombre d'années: {len(self.years)}

Années disponibles:
{', '.join(str(y) for y in self.years)}

Dernière année dans le fichier: {self.years[-1]}
Année à prédire: [Année suivante]
                    """
                    self.info_text.setText(info)
                    
                    self.btn_analyze.setEnabled(True)
                    self.btn_generate_predictions_formula.setEnabled(True)  # Formule toujours disponible après chargement
                    self.status_label.setText("✅ Fichier chargé - Prêt pour l'analyse")
                    
                    # Marquer Phase 2 comme visitée
                    self.phases_visited['phase2'] = True
                    self.check_and_enable_final_report()
                    
                    QMessageBox.information(self, "Succès", "Fichier saisonnier chargé avec succès!")
                else:
                    raise ValueError("Colonne 'saison_annee' non trouvée. Utilisez un fichier exporté de la Phase 1.")
                    
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
                self.status_label.setText("❌ Erreur de chargement")
    
    def run_analysis(self):
        """Lance l'analyse sur toutes les années"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger un fichier")
            return
        
        try:
            self.status_label.setText("Analyse en cours...")
            
            # Analyse des débits (colonnes essentielles: date et debit)
            analyzer = FlowAnalyzer(self.data)
            analysis = analyzer.get_complete_analysis()
            
            # Formater les résultats
            text = f"""
ANALYSE HYDROLOGIQUE (Toutes les années)
{'='*60}

ANALYSE TEMPORELLE
Moyenne: {analysis['temporelle']['moyenne']:.2f} m³/s
Médiane: {analysis['temporelle']['mediane']:.2f} m³/s
Écart-type: {analysis['temporelle']['ecart_type']:.2f} m³/s
Min: {analysis['temporelle']['min']:.2f} m³/s
Max: {analysis['temporelle']['max']:.2f} m³/s

TENDANCE
Type: {analysis['temporelle']['tendance']['tendance_type']}
R²: {analysis['temporelle']['tendance']['r2']:.4f}

ANOMALIES
Nombre: {analysis['temporelle']['anomalies']['nombre']}
            """
            self.analysis_text.setText(text)
            
            # Analyse climatique (optionnelle - seulement si colonnes disponibles)
            try:
                climate_analyzer = ClimateAnalyzer(self.data)
                climate = climate_analyzer.get_complete_analysis()
                
                climate_text = "ANALYSE CLIMATIQUE\n" + "="*60 + "\n\n"
                if climate['correlations']:
                    climate_text += "CORRÉLATIONS DÉBITS-CLIMAT:\n"
                    for var, corr in climate['correlations'].items():
                        climate_text += f"{var}: r={corr['pearson']['correlation']:.4f}\n"
                else:
                    climate_text += "Aucune variable climatique disponible.\n"
                
                self.climate_text.setText(climate_text)
            except:
                self.climate_text.setText("Analyse climatique non disponible (colonnes manquantes).")
            
            self.tabs.setCurrentIndex(1)
            self.status_label.setText("✅ Analyse terminée")
            QMessageBox.information(self, "Succès", "Analyse terminée!")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'analyse:\n{str(e)}")
            self.status_label.setText("❌ Erreur d'analyse")
    
    def run_prediction(self):
        """Lance l'entraînement optimisé du modèle"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger un fichier")
            return
        
        try:
            # Récupérer le modèle sélectionné
            model_name = self.combo_model.currentText()
            
            # Afficher le dialogue de sélection de paramètres
            param_dialog = ParameterSelectionDialog(model_name, self)
            if param_dialog.exec_() != QDialog.Accepted:
                return  # L'utilisateur a annulé
            
            # Récupérer les paramètres sélectionnés
            param_grid = param_dialog.get_param_grid()
            max_iterations = param_dialog.get_max_iterations()
            
            if not param_grid:
                QMessageBox.warning(self, "Attention", "Veuillez sélectionner au moins un paramètre")
                return
            
            self.status_label.setText("Préparation de l'entraînement...")
            
            # Récupérer les indices
            train_start = self.spin_train_start.value() - 1
            train_end = self.spin_train_end.value()
            test_start = self.spin_test_start.value() - 1
            test_end = self.spin_test_end.value()
            
            # Séparer les données
            self.train_years = self.years[train_start:train_end]
            self.test_years = self.years[test_start:test_end]
            
            train_data = self.data[self.data['saison_annee'].isin(self.train_years)]
            test_data = self.data[self.data['saison_annee'].isin(self.test_years)]
            
            # Créer le modèle
            self.predictor = FlowPredictor(model_name)
            
            # Préparer les features
            X_train, y_train = self.predictor.prepare_features(train_data)
            X_test, y_test = self.predictor.prepare_features(test_data)
            
            # ✅ SAUVEGARDER LES NOMS DES FEATURES pour la prédiction future
            # Cela garantit que les prédictions futures utilisent EXACTEMENT les mêmes colonnes
            self.predictor.feature_names = X_train.columns.tolist()
            
            # Créer le worker thread
            self.training_worker = TrainingWorker(
                self.predictor,
                X_train, y_train,
                X_test, y_test,
                param_grid,
                max_iterations
            )
            
            # Créer le dialogue de progression
            self.progress_dialog = ProgressDialog(self)
            
            # Connecter les signaux
            self.training_worker.progress_update.connect(self.progress_dialog.update_progress)
            self.training_worker.training_complete.connect(self.handle_training_complete)
            self.training_worker.training_error.connect(self.handle_training_error)
            self.progress_dialog.btn_cancel.clicked.connect(self.training_worker.terminate)
            
            # Démarrer l'entraînement
            self.training_worker.start()
            self.progress_dialog.exec_()
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de la préparation:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur de préparation")
    
    def handle_training_error(self, error_msg):
        """Gère les erreurs d'entraînement"""
        self.progress_dialog.close()
        QMessageBox.critical(self, "Erreur d'entraînement", error_msg)
        self.status_label.setText("❌ Erreur d'entraînement")
    
    def handle_training_complete(self, optimization_results):
        """Gère la complétion de l'entraînement"""
        from datetime import datetime
        
        # Fermer le dialogue de progression
        self.progress_dialog.close()
        
        try:
            # Extraire les résultats
            best_params = optimization_results['best_params']
            best_r2 = optimization_results['best_r2']
            total_iterations = optimization_results['total_iterations']
            history = optimization_results['history']
            
            # Préparer les informations de saison
            season_info = {
                'saison': 'Saison',  # Peut être extrait des données si disponible
                'train_period': f'{self.train_years[0]} - {self.train_years[-1]}',
                'test_period': f'{self.test_years[0]} - {self.test_years[-1]}'
            }
            
            # Générer le rapport PDF
            report_filename = f'training_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            report_path = os.path.join('exports', report_filename)
            
            self.report_gen.generate_training_report(
                optimization_results,
                self.combo_model.currentText(),
                season_info,
                report_path
            )
            
            # Afficher les résultats dans l'onglet prédiction
            text = f"""
ENTRAÎNEMENT OPTIMISÉ TERMINÉ
{'='*60}

MODÈLE: {self.combo_model.currentText()}

CONFIGURATION:
Entraînement: {self.train_years[0]} à {self.train_years[-1]} ({len(self.train_years)} années)
Test: {self.test_years[0]} à {self.test_years[-1]} ({len(self.test_years)} années)

OPTIMISATION:
Nombre d'itérations: {total_iterations}
Meilleur R² trouvé: {best_r2:.4f}

MEILLEURS PARAMÈTRES:
"""
            for param, value in best_params.items():
                text += f"  {param}: {value}\n"
            
            text += f"""

INTERPRÉTATION:
"""
            if best_r2 > 0.8:
                text += "✅ Excellent modèle (R² > 0.8)\n"
            elif best_r2 > 0.6:
                text += "✅ Bon modèle (R² > 0.6)\n"
            elif best_r2 > 0.4:
                text += "⚠️ Modèle acceptable (R² > 0.4)\n"
            else:
                text += "❌ Modèle à améliorer (R² < 0.4)\n"
            
            text += f"""

RAPPORT PDF:
{report_path}

Utilisez "Générer Prédictions" pour créer les prédictions futures.
Utilisez "Exporter Rapport Final" pour le rapport complet.
            """
            
            self.prediction_text.setText(text)
            
            # Activer les boutons
            self.btn_export_report.setEnabled(True)
            if hasattr(self, 'btn_save_model'):
                self.btn_save_model.setEnabled(True)
            
            # Afficher l'onglet prédiction
            self.tabs.setCurrentIndex(2)
            
            # Mettre à jour le statut
            self.status_label.setText("✅ Entraînement terminé")
            
            # Message de succès
            QMessageBox.information(
                self,
                "Succès",
                f"Entraînement terminé!\n\n"
                f"Meilleur R²: {best_r2:.4f}\n"
                f"Itérations: {total_iterations}\n\n"
                f"Rapport PDF: {report_filename}\n\n"
                f"Cliquez sur 'Générer Prédictions' pour créer les prédictions futures."
            )
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de la génération du rapport:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur de génération du rapport")
    
    def generate_predictions_formula(self):
        """Affiche le dialogue de sélection de saison puis des 5 phases de prédiction"""
        if self.data is None:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger un fichier")
            return
        
        try:
            # ÉTAPE 1: Choisir la saison (Sèche ou Pluies)
            season_dialog = SeasonSelectionDialog(self)
            season_result = season_dialog.exec_()
            
            if season_result != QDialog.Accepted:
                return
            
            selected_season = season_dialog.get_selected_season()
            if selected_season is None:
                return
            
            # VÉRIFIER SI LA SAISON SÉLECTIONNÉE A DES DONNÉES
            # Vérifier via le contrôleur si les coefficients ont été extraits
            if selected_season == 'dry':
                has_data = self.controller.dry_coefficients is not None
                season_name = "saison sèche"
            else:
                has_data = self.controller.rainy_coefficients is not None
                season_name = "saison des pluies"
            
            if not has_data:
                QMessageBox.warning(
                    self, 
                    "Données manquantes", 
                    f"❌ Aucune donnée de {season_name} dans le fichier chargé.\n\n"
                    f"Le fichier actuel ne contient pas assez de données pour la {season_name} "
                    f"(minimum 10 années hydrologiques requises).\n\n"
                    f"Veuillez charger un fichier contenant des données de {season_name}."
                )
                return
            
            # Stocker la saison sélectionnée pour les phases suivantes
            self.selected_formula_season = selected_season
            
            # ÉTAPE 2: Afficher le dialogue de sélection de phase
            self.show_phase_selection_dialog(selected_season)
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'ouverture du dialogue:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur d'ouverture du dialogue")
    
    def show_phase_selection_dialog(self, selected_season):
        """Affiche le dialogue de sélection des 5 phases"""
        dialog = PhaseSelectionDialog(self, selected_season)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            phase = dialog.get_selected_phase()
            
            if phase is None:
                return
            
            # Router vers la méthode appropriée selon la phase sélectionnée
            if phase == 1:
                self.show_phase1_formula_master(selected_season)
            elif phase == 2:
                self.show_phase2_coefficients(selected_season)
            elif phase == 3:
                self.show_phase3_calculator(selected_season)
            elif phase == 4:
                self.show_phase4_full_table(selected_season)
            elif phase == 5:
                self.show_phase5_comparative_analysis(selected_season)
            else:
                QMessageBox.warning(self, "Erreur", f"Phase {phase} non reconnue")
    
    def show_phase1_formula_master(self, season='rainy'):
        """Phase 1: Formule Maîtresse - Saisir k(A) et ε pour calculer Q(t,A)"""
        # Obtenir le module de formule avec coefficients extraits du contrôleur
        if season == 'dry':
            formula = self.controller.get_formula_module_dry()
            season_name = "SAISON SÈCHE"
            season_icon = "🌵"
            duration = 212
        else:
            formula = self.controller.get_formula_module_rainy()
            season_name = "SAISON DES PLUIES"
            season_icon = "🌧️"
            duration = 153
        
        # Obtenir les informations sur les coefficients
        coeffs_info = self.controller.get_coefficients_info('dry' if season == 'dry' else 'rainy')
        
        # Créer un dialogue pour saisir k(A) et ε
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Phase 1: Formule Maîtresse - {season_name}")
        dialog.setModal(True)
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout(dialog)
        
        # Titre
        title = QLabel(f"{season_icon} Phase 1: Formule Maîtresse - {season_name}")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Calculer Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]")
        desc.setStyleSheet("color: #666; padding: 5px;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Champ k(A)
        from PyQt5.QtWidgets import QDoubleSpinBox
        spin_k_A = QDoubleSpinBox()
        spin_k_A.setMinimum(0.01)
        spin_k_A.setMaximum(3.0)
        spin_k_A.setValue(1.0)
        spin_k_A.setDecimals(3)
        spin_k_A.setSingleStep(0.1)
        spin_k_A.setToolTip("Coefficient annuel k(A) = Q̄_année / 739\nValeurs typiques: 0.8 (sec) à 1.2 (humide)")
        form_layout.addRow("Coefficient annuel k(A):", spin_k_A)
        
        # Champ ε
        spin_epsilon = QDoubleSpinBox()
        spin_epsilon.setMinimum(0.01)
        spin_epsilon.setMaximum(0.08)
        spin_epsilon.setValue(0.05)
        spin_epsilon.setDecimals(2)
        spin_epsilon.setSingleStep(0.01)
        spin_epsilon.setSuffix(" (5%)")
        spin_epsilon.setToolTip("Taux d'erreur ε entre 1% et 8%\nValeur recommandée: 5%")
        form_layout.addRow("Taux d'erreur ε:", spin_epsilon)
        
        layout.addLayout(form_layout)
        
        # Zone d'affichage des résultats
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setMinimumHeight(300)
        result_text.setStyleSheet("font-family: Consolas; font-size: 10pt;")
        layout.addWidget(result_text)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_calculate = QPushButton("🧮 Calculer")
        btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        
        btn_close = QPushButton("❌ Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_close.clicked.connect(dialog.close)
        
        btn_layout.addWidget(btn_calculate)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        # Fonction de calcul
        def calculate():
            try:
                k_A = spin_k_A.value()
                epsilon = spin_epsilon.value()
                
                # Valider les entrées
                is_valid, error_msg = formula.validate_inputs(1, k_A, epsilon)
                if not is_valid:
                    QMessageBox.warning(dialog, "Erreur de validation", error_msg)
                    return
                
                # Obtenir les coefficients réels du module
                poly_coeffs = formula.POLY_COEFFS
                monthly_coeffs = formula.MONTHLY_COEFFS
                Q_hist = formula.Q_HISTORICAL
                r2_value = coeffs_info['r_squared']
                
                # Construire le texte du polynôme
                poly_formula = f"""P(t) = {poly_coeffs['t6']:.3e}·t⁶ + {poly_coeffs['t5']:.3e}·t⁵ + {poly_coeffs['t4']:.3e}·t⁴
       + {poly_coeffs['t3']:.3e}·t³ + {poly_coeffs['t2']:.3e}·t² + {poly_coeffs['t1']:.3e}·t + {poly_coeffs['t0']:.3e}"""
                
                # Construire le texte des coefficients mensuels
                monthly_coeffs_text = ""
                month_names_fr = {
                    1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin",
                    7: "Juillet", 8: "Août", 9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
                }
                for month in sorted(monthly_coeffs.keys()):
                    monthly_coeffs_text += f"- {month_names_fr[month]:10s}: {monthly_coeffs[month]:.4f}\n"
                
                # Afficher les informations de la formule
                text = f"""
FORMULE MAÎTRESSE DE PRÉDICTION - {season_name}
{'='*60}

Q(t,A) = P(t) × k(A) × Cm(mois) × [1 ± ε]

🔧 SOURCE DES COEFFICIENTS:
{'='*60}
Source:               {coeffs_info['source']}
Q historique:         {coeffs_info['Q_historical']:.2f} m³/s
R²:                   {coeffs_info['r_squared']:.3f}
"""
                
                # Ajouter les avertissements si présents
                if 'warnings' in coeffs_info and coeffs_info['warnings']:
                    text += f"\n⚠️ AVERTISSEMENTS:\n"
                    for warning in coeffs_info['warnings']:
                        text += f"- {warning}\n"
                    text += "\n"
                
                text += f"""
PARAMÈTRES SAISIS:
- Coefficient annuel k(A): {k_A:.3f}
- Taux d'erreur ε: {epsilon:.2f} ({epsilon*100:.0f}%)

POLYNÔME P(t) D'ORDRE 6:
{poly_formula}

R² = {r2_value:.3f}

COEFFICIENTS MENSUELS (Cm):
{monthly_coeffs_text}

DÉBIT HISTORIQUE DE RÉFÉRENCE:
Q̄_historique = {Q_hist:.2f} m³/s

BORNES DE CALCUL:
Q_inf = P(t) × k(A) × Cm × {1-epsilon:.2f}  (borne inférieure -{epsilon*100:.0f}%)
Q_sup = P(t) × k(A) × Cm × {1+epsilon:.2f}  (borne supérieure +{epsilon*100:.0f}%)

EXEMPLES DE CALCUL:
"""
                
                # Définir les noms de mois selon la saison
                if season == 'dry':
                    month_names = {
                        12: "Décembre", 1: "Janvier", 2: "Février", 
                        3: "Mars", 4: "Avril", 5: "Mai", 6: "Juin"
                    }
                    examples = [
                        (1, "1er décembre"),
                        (31, "31 décembre"),
                        (110, "Mi-mars (étiage)"),
                        (182, "31 mai"),
                        (212, "30 juin")
                    ]
                else:
                    month_names = {
                        7: "Juillet", 8: "Août", 9: "Septembre", 
                        10: "Octobre", 11: "Novembre"
                    }
                    examples = [
                        (1, "1er juillet"),
                        (31, "31 juillet"),
                        (77, "Milieu de saison"),
                        (123, "31 octobre"),
                        (153, "30 novembre")
                    ]
                
                # Calculer quelques exemples
                for t, label in examples:
                    result = formula.calculate_Q(t, k_A, epsilon)
                    month_name = month_names[result['month']]
                    
                    text += f"\nJour t={t} ({label}) - {month_name}:\n"
                    text += f"  P(t) = {result['P_t']:.2f} m³/s\n"
                    text += f"  Cm = {result['Cm']:.3f}\n"
                    text += f"  Q centrale = {result['Q_central']:.2f} m³/s\n"
                    text += f"  Q min (-{epsilon*100:.0f}%) = {result['Q_inf']:.2f} m³/s\n"
                    text += f"  Q max (+{epsilon*100:.0f}%) = {result['Q_sup']:.2f} m³/s\n"
                
                text += f"\n{'='*60}\n"
                text += f"Utilisez Phase 3 (Calculateur) pour calculer un jour spécifique.\n"
                text += f"Utilisez Phase 4 (Tableau Complet) pour générer les {duration} jours.\n"
                
                result_text.setText(text)
                self.status_label.setText("✅ Phase 1: Formule calculée")
                
            except Exception as e:
                import traceback
                error_msg = f"Erreur lors du calcul:\n{str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(dialog, "Erreur", error_msg)
        
        btn_calculate.clicked.connect(calculate)
        
        # Bouton Retour
        btn_back = QPushButton("⬅️ Retour au menu des phases")
        btn_back.setStyleSheet(self.get_button_style("#6c757d"))
        btn_back.clicked.connect(lambda: self.return_to_phase_menu(dialog, season))
        layout.addWidget(btn_back)
        
        # Calculer automatiquement au démarrage
        calculate()
        
        # Afficher le dialogue
        dialog.exec_()
    
    def return_to_phase_menu(self, current_dialog, season):
        """Ferme le dialogue actuel et rouvre le menu de sélection des phases"""
        current_dialog.close()
        self.show_phase_selection_dialog(season)
    
    def show_phase2_coefficients(self, season='rainy'):
        """Phase 2: Coefficients - Afficher les tableaux A, B, C"""
        # Importer le bon module selon la saison
        if season == 'dry':
            from backend.formula.coefficients_module_seche import CoefficientsModuleSeche as CoefficientsModule
            season_name = "SAISON SÈCHE"
            season_icon = "🌵"
        else:
            from backend.formula.coefficients_module import CoefficientsModule
            season_name = "SAISON DES PLUIES"
            season_icon = "🌧️"
        
        try:
            # Vérifier que les données sont chargées
            if self.data is None or self.data.empty:
                QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger un fichier saisonnier.")
                return
            
            # S'assurer que la colonne 'debits' existe
            if 'debit' in self.data.columns and 'debits' not in self.data.columns:
                self.data['debits'] = self.data['debit']
            
            if 'debits' not in self.data.columns:
                QMessageBox.warning(self, "Erreur", "La colonne 'debits' est manquante dans les données.")
                return
            
            # Créer un dialogue pour afficher les tableaux
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Phase 2: Coefficients - {season_name}")
            dialog.setModal(True)
            dialog.setMinimumWidth(900)
            dialog.setMinimumHeight(700)
            
            layout = QVBoxLayout(dialog)
            
            # Titre
            title = QLabel(f"{season_icon} Phase 2: Coefficients - {season_name}")
            title.setFont(QFont("Arial", 14, QFont.Bold))
            title.setStyleSheet("color: #1f4788; padding: 10px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Créer le module de coefficients avec les données historiques
            self.status_label.setText("Calcul des coefficients...")
            coeffs = CoefficientsModule(self.data)
            
            # Créer des onglets pour les 3 tableaux
            tabs = QTabWidget()
            
            # Tableau A: Coefficients annuels
            tab_a = QWidget()
            layout_a = QVBoxLayout(tab_a)
            
            label_a = QLabel("Tableau A: Coefficients Annuels k(A)")
            label_a.setFont(QFont("Arial", 12, QFont.Bold))
            layout_a.addWidget(label_a)
            
            table_a = QTableWidget()
            df_a = coeffs.calculate_annual_coefficients()
            table_a.setRowCount(len(df_a))
            table_a.setColumnCount(len(df_a.columns))
            table_a.setHorizontalHeaderLabels(df_a.columns.tolist())
            
            for i, row in df_a.iterrows():
                for j, col in enumerate(df_a.columns):
                    item = QTableWidgetItem(str(row[col]))
                    table_a.setItem(i, j, item)
            
            table_a.resizeColumnsToContents()
            layout_a.addWidget(table_a)
            tabs.addTab(tab_a, "📊 Tableau A")
            
            # Tableau B: Coefficients mensuels
            tab_b = QWidget()
            layout_b = QVBoxLayout(tab_b)
            
            label_b = QLabel("Tableau B: Coefficients Mensuels Cm")
            label_b.setFont(QFont("Arial", 12, QFont.Bold))
            layout_b.addWidget(label_b)
            
            table_b = QTableWidget()
            df_b = coeffs.calculate_monthly_statistics()
            table_b.setRowCount(len(df_b))
            table_b.setColumnCount(len(df_b.columns))
            table_b.setHorizontalHeaderLabels(df_b.columns.tolist())
            
            for i, row in df_b.iterrows():
                for j, col in enumerate(df_b.columns):
                    item = QTableWidgetItem(str(row[col]))
                    table_b.setItem(i, j, item)
            
            table_b.resizeColumnsToContents()
            layout_b.addWidget(table_b)
            tabs.addTab(tab_b, "📅 Tableau B")
            
            # Tableau C: Coefficients du polynôme
            tab_c = QWidget()
            layout_c = QVBoxLayout(tab_c)
            
            label_c = QLabel("Tableau C: Coefficients du Polynôme P(t)")
            label_c.setFont(QFont("Arial", 12, QFont.Bold))
            layout_c.addWidget(label_c)
            
            table_c = QTableWidget()
            df_c = coeffs.get_polynomial_table()
            table_c.setRowCount(len(df_c))
            table_c.setColumnCount(len(df_c.columns))
            table_c.setHorizontalHeaderLabels(df_c.columns.tolist())
            
            for i, row in df_c.iterrows():
                for j, col in enumerate(df_c.columns):
                    item = QTableWidgetItem(str(row[col]))
                    table_c.setItem(i, j, item)
            
            table_c.resizeColumnsToContents()
            layout_c.addWidget(table_c)
            
            # Ajouter R² en bas
            r2_label = QLabel("R² = 0.988")
            r2_label.setFont(QFont("Arial", 11, QFont.Bold))
            r2_label.setStyleSheet("color: #28a745; padding: 10px;")
            layout_c.addWidget(r2_label)
            
            tabs.addTab(tab_c, "📐 Tableau C")
            
            layout.addWidget(tabs)
            
            # Boutons
            btn_layout = QHBoxLayout()
            
            btn_export = QPushButton("📊 Exporter en Excel")
            btn_export.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
            def export_coefficients():
                try:
                    from backend.formula.export_manager import ExportManager
                    from datetime import datetime
                    
                    export_mgr = ExportManager()
                    filename = f"coefficients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    # Créer un dictionnaire avec les 3 tableaux
                    data_dict = {
                        'Tableau A - Annuels': df_a,
                        'Tableau B - Mensuels': df_b,
                        'Tableau C - Polynome': df_c
                    }
                    
                    metadata = {
                        'generation_date': datetime.now(),
                        'R2': 0.988
                    }
                    
                    export_mgr.export_coefficients_to_excel(data_dict, filename, metadata)
                    
                    QMessageBox.information(dialog, "Succès", f"Coefficients exportés:\n{filename}")
                    self.status_label.setText(f"✅ Coefficients exportés: {filename}")
                    
                except Exception as e:
                    import traceback
                    error_msg = f"Erreur lors de l'export:\n{str(e)}\n\n{traceback.format_exc()}"
                    QMessageBox.critical(dialog, "Erreur", error_msg)
            
            btn_export.clicked.connect(export_coefficients)
            
            btn_close = QPushButton("❌ Fermer")
            btn_close.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            btn_close.clicked.connect(dialog.close)
            
            btn_layout.addWidget(btn_export)
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            # Bouton Retour
            btn_back = QPushButton("⬅️ Retour au menu des phases")
            btn_back.setStyleSheet(self.get_button_style("#6c757d"))
            btn_back.clicked.connect(lambda: self.return_to_phase_menu(dialog, season))
            layout.addWidget(btn_back)
            
            self.status_label.setText("✅ Phase 2: Coefficients affichés")
            
            # Afficher le dialogue
            dialog.exec_()
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'affichage des coefficients:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur Phase 2")
    
    def show_phase3_calculator(self, season='rainy'):
        """Phase 3: Calculateur - Calculer le débit pour un jour spécifique"""
        # Obtenir le module de formule avec coefficients extraits du contrôleur
        if season == 'dry':
            from backend.formula.calculator_module_seche import CalculatorModuleSeche as CalculatorModule
            formula = self.controller.get_formula_module_dry()
            season_name = "SAISON SÈCHE"
            season_icon = "🌵"
            max_day = 212
        else:
            from backend.formula.calculator_module import CalculatorModule
            formula = self.controller.get_formula_module_rainy()
            season_name = "SAISON DES PLUIES"
            season_icon = "🌧️"
            max_day = 153
        
        # Obtenir les informations sur les coefficients
        coeffs_info = self.controller.get_coefficients_info('dry' if season == 'dry' else 'rainy')
        from PyQt5.QtWidgets import QDoubleSpinBox
        
        # Créer un dialogue pour le calculateur
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Phase 3: Calculateur - {season_name}")
        dialog.setModal(True)
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout(dialog)
        
        # Titre
        title = QLabel(f"{season_icon} Phase 3: Calculateur - {season_name}")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Calculer P(t), Q centrale, Q min, Q max pour un jour spécifique")
        desc.setStyleSheet("color: #666; padding: 5px;")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Formulaire
        form_layout = QFormLayout()
        
        # Champ t (jour de saison) - adapté selon la saison
        spin_t = QSpinBox()
        spin_t.setMinimum(1)
        spin_t.setMaximum(max_day)
        spin_t.setValue(1)
        if season == 'dry':
            spin_t.setToolTip(f"Jour de saison (1-{max_day})\n1 = 1er décembre, {max_day} = 30 juin")
        else:
            spin_t.setToolTip(f"Jour de saison (1-{max_day})\n1 = 1er juillet, {max_day} = 30 novembre")
        form_layout.addRow("Jour de saison t:", spin_t)
        
        # Champ k(A)
        spin_k_A = QDoubleSpinBox()
        spin_k_A.setMinimum(0.01)
        spin_k_A.setMaximum(3.0)
        spin_k_A.setValue(1.0)
        spin_k_A.setDecimals(3)
        spin_k_A.setSingleStep(0.1)
        spin_k_A.setToolTip("Coefficient annuel k(A) = Q̄_année / 739")
        form_layout.addRow("Coefficient annuel k(A):", spin_k_A)
        
        # Champ ε
        spin_epsilon = QDoubleSpinBox()
        spin_epsilon.setMinimum(0.01)
        spin_epsilon.setMaximum(0.08)
        spin_epsilon.setValue(0.05)
        spin_epsilon.setDecimals(2)
        spin_epsilon.setSingleStep(0.01)
        spin_epsilon.setSuffix(" (5%)")
        spin_epsilon.setToolTip("Taux d'erreur ε entre 1% et 8%")
        form_layout.addRow("Taux d'erreur ε:", spin_epsilon)
        
        layout.addLayout(form_layout)
        
        # Zone d'affichage des résultats
        result_text = QTextEdit()
        result_text.setReadOnly(True)
        result_text.setMinimumHeight(350)
        result_text.setStyleSheet("font-family: Consolas; font-size: 11pt;")
        layout.addWidget(result_text)
        
        # Boutons
        btn_layout = QHBoxLayout()
        
        btn_calculate = QPushButton("🧮 Calculer")
        btn_calculate.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        
        btn_close = QPushButton("❌ Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_close.clicked.connect(dialog.close)
        
        btn_layout.addWidget(btn_calculate)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        # Fonction de calcul
        def calculate():
            try:
                t = spin_t.value()
                k_A = spin_k_A.value()
                epsilon = spin_epsilon.value()
                
                # Utiliser le module de formule avec coefficients extraits
                calculator = CalculatorModule(formula)
                
                # Calculer
                result = calculator.calculate_single_day(t, k_A, epsilon)
                
                # Le mois est déjà en français dans result['month']
                month_name = result['month']
                
                text = f"""
RÉSULTATS DU CALCUL
{'='*60}

PARAMÈTRES:
- Jour de saison t: {t}
- Date: {result['date'].strftime('%d/%m/%Y')}
- Mois: {month_name}
- Coefficient annuel k(A): {k_A:.3f}
- Taux d'erreur ε: {epsilon:.2f} ({epsilon*100:.0f}%)

🔧 SOURCE DES COEFFICIENTS:
{'='*60}
Source:               {coeffs_info['source']}
Q historique:         {coeffs_info['Q_historical']:.2f} m³/s
R²:                   {coeffs_info['r_squared']:.3f}
"""
                
                # Ajouter les avertissements si présents
                if 'warnings' in coeffs_info and coeffs_info['warnings']:
                    text += f"\n⚠️ AVERTISSEMENTS:\n"
                    for warning in coeffs_info['warnings']:
                        text += f"- {warning}\n"
                    text += "\n"
                
                text += f"""
COEFFICIENTS APPLIQUÉS:
- Coefficient mensuel Cm: {result['Cm']:.3f}

RÉSULTATS:
- P(t) (polynôme): {result['P_t']:.2f} m³/s
- Q centrale: {result['Q_central']:.2f} m³/s
- Q min (-8%): {result['Q_min']:.2f} m³/s
- Q max (+19%): {result['Q_max']:.2f} m³/s

FORMULE APPLIQUÉE:
Q(t,A) = P(t) × k(A) × Cm × [1 ± ε]
Q(t,A) = {result['P_t']:.2f} × {k_A:.3f} × {result['Cm']:.3f} × [1 ± {epsilon:.2f}]
Q(t,A) = {result['Q_central']:.2f} m³/s

INTERPRÉTATION:
"""
                
                # Ajouter le statut
                Q = result['Q_central']
                if Q > 1200:
                    text += "🚨 DANGEREUX: Débit très élevé (>1200 m³/s)\n"
                elif Q >= 900:
                    text += "🔔 ÉLEVÉ: Débit élevé (900-1200 m³/s)\n"
                elif Q >= 600:
                    text += "✅ NORMAL: Débit normal (600-900 m³/s)\n"
                elif Q >= 400:
                    text += "🌤️ MODÉRÉ: Débit modéré (400-600 m³/s)\n"
                else:
                    text += "ℹ️ BAS: Débit bas (<400 m³/s)\n"
                
                text += f"\n{'='*60}\n"
                text += "Temps de calcul: < 100 ms\n"
                
                result_text.setText(text)
                self.status_label.setText(f"✅ Phase 3: Jour {t} calculé")
                
            except Exception as e:
                import traceback
                error_msg = f"Erreur lors du calcul:\n{str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(dialog, "Erreur", error_msg)
        
        btn_calculate.clicked.connect(calculate)
        
        # Bouton Retour
        btn_back = QPushButton("⬅️ Retour au menu des phases")
        btn_back.setStyleSheet(self.get_button_style("#6c757d"))
        btn_back.clicked.connect(lambda: self.return_to_phase_menu(dialog, season))
        layout.addWidget(btn_back)
        
        # Calculer automatiquement au démarrage
        calculate()
        
        # Afficher le dialogue
        dialog.exec_()
    
    def show_phase4_full_table(self, season='rainy'):
        """Phase 4: Tableau Complet - Générer le tableau de 153/212 jours avec export"""
        # Marquer Phase 4 comme visitée
        self.phases_visited['phase4'] = True
        self.check_and_enable_final_report()
        
        # Importer le bon module selon la saison
        if season == 'dry':
            from backend.formula.generator_module_seche import GeneratorModuleSeche as GeneratorModule
            season_name = "SAISON SÈCHE"
            season_icon = "🌵"
            duration = 212
        else:
            from backend.formula.generator_module import GeneratorModule
            season_name = "SAISON DES PLUIES"
            season_icon = "🌧️"
            duration = 153
        from backend.formula.export_manager import ExportManager
        from PyQt5.QtWidgets import QDoubleSpinBox
        from datetime import datetime
        
        # Obtenir le module de formule avec coefficients extraits du contrôleur
        if season == 'dry':
            formula = self.controller.get_formula_module_dry()
        else:
            formula = self.controller.get_formula_module_rainy()
        
        # Obtenir les informations sur les coefficients
        coeffs_info = self.controller.get_coefficients_info('dry' if season == 'dry' else 'rainy')
        
        # Créer un dialogue pour le tableau complet
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Phase 4: Tableau Complet - {season_name}")
        dialog.setModal(True)
        dialog.setMinimumWidth(1000)
        dialog.setMinimumHeight(700)
        
        layout = QVBoxLayout(dialog)
        
        # Titre
        title = QLabel(f"{season_icon} Phase 4: Tableau Complet - {season_name} ({duration} jours)")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setStyleSheet("color: #1f4788; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Afficher la source des coefficients
        source_label = QLabel(f"🔧 Source: {coeffs_info['source']} | Q̄: {coeffs_info['Q_historical']:.2f} m³/s | R²: {coeffs_info['r_squared']:.3f}")
        source_label.setFont(QFont("Arial", 10))
        source_label.setStyleSheet("color: #28a745; padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        source_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(source_label)
        
        # Formulaire de paramètres
        form_widget = QWidget()
        form_layout = QHBoxLayout(form_widget)
        
        form_layout.addWidget(QLabel("k(A):"))
        spin_k_A = QDoubleSpinBox()
        spin_k_A.setMinimum(0.01)
        spin_k_A.setMaximum(3.0)
        spin_k_A.setValue(1.0)
        spin_k_A.setDecimals(3)
        spin_k_A.setSingleStep(0.1)
        form_layout.addWidget(spin_k_A)
        
        form_layout.addWidget(QLabel("ε:"))
        spin_epsilon = QDoubleSpinBox()
        spin_epsilon.setMinimum(0.01)
        spin_epsilon.setMaximum(0.08)
        spin_epsilon.setValue(0.05)
        spin_epsilon.setDecimals(2)
        spin_epsilon.setSingleStep(0.01)
        form_layout.addWidget(spin_epsilon)
        
        form_layout.addWidget(QLabel("Année:"))
        spin_year = QSpinBox()
        spin_year.setMinimum(2000)
        spin_year.setMaximum(2100)
        spin_year.setValue(datetime.now().year)
        form_layout.addWidget(spin_year)
        
        btn_generate = QPushButton("🔄 Générer")
        btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #6f42c1;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a32a3;
            }
        """)
        form_layout.addWidget(btn_generate)
        
        form_layout.addStretch()
        layout.addWidget(form_widget)
        
        # Tableau
        table = QTableWidget()
        table.setMinimumHeight(500)
        layout.addWidget(table)
        
        # Variable pour stocker le DataFrame
        current_df = [None]
        
        # Fonction de génération
        def generate_table():
            try:
                k_A = spin_k_A.value()
                epsilon = spin_epsilon.value()
                year = spin_year.value()
                
                self.status_label.setText(f"Génération du tableau de {duration} jours...")
                
                # Créer le générateur avec le module de formule (coefficients extraits ou Mbakaou)
                generator = GeneratorModule(formula)
                
                # Générer le tableau
                df = generator.generate_full_table(k_A, epsilon, year)
                current_df[0] = df
                
                # Afficher dans le tableau
                table.setRowCount(len(df))
                table.setColumnCount(len(df.columns))
                table.setHorizontalHeaderLabels(df.columns.tolist())
                
                for i, row in df.iterrows():
                    for j, col in enumerate(df.columns):
                        value = row[col]
                        if isinstance(value, float):
                            item = QTableWidgetItem(f"{value:.2f}")
                        else:
                            item = QTableWidgetItem(str(value))
                        table.setItem(i, j, item)
                
                table.resizeColumnsToContents()
                
                # Statistiques
                Q_mean = df['Q centrale'].mean()
                Q_min = df['Q centrale'].min()
                Q_max = df['Q centrale'].max()
                
                self.status_label.setText(
                    f"✅ Phase 4: {duration} jours générés | "
                    f"Q moy: {Q_mean:.2f} m³/s | "
                    f"Q min: {Q_min:.2f} m³/s | "
                    f"Q max: {Q_max:.2f} m³/s"
                )
                
                QMessageBox.information(
                    dialog,
                    "Succès",
                    f"Tableau de {duration} jours généré!\n\n"
                    f"Année: {year}\n"
                    f"k(A): {k_A:.3f}\n"
                    f"ε: {epsilon:.2f}\n\n"
                    f"Q moyen: {Q_mean:.2f} m³/s"
                )
                
            except Exception as e:
                import traceback
                error_msg = f"Erreur lors de la génération:\n{str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(dialog, "Erreur", error_msg)
        
        btn_generate.clicked.connect(generate_table)
        
        # Boutons d'export
        btn_layout = QHBoxLayout()
        
        btn_export_excel = QPushButton("📊 Exporter Excel")
        btn_export_excel.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        
        def export_excel():
            if current_df[0] is None:
                QMessageBox.warning(dialog, "Attention", "Veuillez d'abord générer le tableau")
                return
            
            try:
                export_mgr = ExportManager()
                filename = f"predictions_formule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                
                metadata = {
                    'k_A': spin_k_A.value(),
                    'epsilon': spin_epsilon.value(),
                    'generation_date': datetime.now(),
                    'year': spin_year.value()
                }
                
                export_mgr.export_to_excel(current_df[0], filename, metadata)
                
                QMessageBox.information(dialog, "Succès", f"Tableau exporté:\n{filename}")
                self.status_label.setText(f"✅ Exporté: {filename}")
                
            except Exception as e:
                import traceback
                error_msg = f"Erreur lors de l'export Excel:\n{str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(dialog, "Erreur", error_msg)
        
        btn_export_excel.clicked.connect(export_excel)
        
        btn_export_pdf = QPushButton("📄 Exporter PDF")
        btn_export_pdf.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        
        def export_pdf():
            if current_df[0] is None:
                QMessageBox.warning(dialog, "Attention", "Veuillez d'abord générer le tableau")
                return
            
            try:
                export_mgr = ExportManager()
                filename = f"predictions_formule_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                
                metadata = {
                    'k_A': spin_k_A.value(),
                    'epsilon': spin_epsilon.value(),
                    'generation_date': datetime.now(),
                    'year': spin_year.value()
                }
                
                export_mgr.export_to_pdf(current_df[0], filename, metadata)
                
                QMessageBox.information(dialog, "Succès", f"Tableau exporté:\n{filename}")
                self.status_label.setText(f"✅ Exporté: {filename}")
                
            except Exception as e:
                import traceback
                error_msg = f"Erreur lors de l'export PDF:\n{str(e)}\n\n{traceback.format_exc()}"
                QMessageBox.critical(dialog, "Erreur", error_msg)
        
        btn_export_pdf.clicked.connect(export_pdf)
        
        btn_close = QPushButton("❌ Fermer")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        btn_close.clicked.connect(dialog.close)
        
        btn_layout.addWidget(btn_export_excel)
        btn_layout.addWidget(btn_export_pdf)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        
        # Bouton Retour
        btn_back = QPushButton("⬅️ Retour au menu des phases")
        btn_back.setStyleSheet(self.get_button_style("#6c757d"))
        btn_back.clicked.connect(lambda: self.return_to_phase_menu(dialog, season))
        layout.addWidget(btn_back)
        
        # Générer automatiquement au démarrage
        generate_table()
        
        # Afficher le dialogue
        dialog.exec_()
    
    def show_phase5_comparative_analysis(self, season='rainy'):
        """Phase 5: Analyse Comparative - Classements annuels et mensuels"""
        # Marquer Phase 5 comme visitée
        self.phases_visited['phase5'] = True
        self.check_and_enable_final_report()
        
        # Importer le bon module selon la saison
        if season == 'dry':
            from backend.formula.analyzer_module_seche import AnalyzerModuleSeche as AnalyzerModule
            season_name = "SAISON SÈCHE"
            season_icon = "🌵"
        else:
            from backend.formula.analyzer_module import AnalyzerModule
            season_name = "SAISON DES PLUIES"
            season_icon = "🌧️"
        from backend.formula.coefficients_module import CoefficientsModule
        from backend.formula.export_manager import ExportManager
        from datetime import datetime
        
        # Obtenir les informations sur les coefficients
        coeffs_info = self.controller.get_coefficients_info('dry' if season == 'dry' else 'rainy')
        
        try:
            # Vérifier que les données sont chargées
            if self.data is None or self.data.empty:
                QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger un fichier saisonnier.")
                return
            
            # S'assurer que la colonne 'debits' existe
            if 'debit' in self.data.columns and 'debits' not in self.data.columns:
                self.data['debits'] = self.data['debit']
            
            if 'debits' not in self.data.columns:
                QMessageBox.warning(self, "Erreur", "La colonne 'debits' est manquante dans les données.")
                return
            
            # Créer un dialogue pour l'analyse comparative
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Phase 5: Analyse Comparative - {season_name}")
            dialog.setModal(True)
            dialog.setMinimumWidth(900)
            dialog.setMinimumHeight(700)
            
            layout = QVBoxLayout(dialog)
            
            # Titre
            title = QLabel(f"{season_icon} Phase 5: Analyse Comparative - {season_name}")
            title.setFont(QFont("Arial", 14, QFont.Bold))
            title.setStyleSheet("color: #1f4788; padding: 10px;")
            title.setAlignment(Qt.AlignCenter)
            layout.addWidget(title)
            
            # Afficher la source des coefficients
            source_label = QLabel(f"🔧 Source: {coeffs_info['source']} | Q̄: {coeffs_info['Q_historical']:.2f} m³/s | R²: {coeffs_info['r_squared']:.3f}")
            source_label.setFont(QFont("Arial", 10))
            source_label.setStyleSheet("color: #28a745; padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
            source_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(source_label)
            
            # Créer les modules
            self.status_label.setText("Génération des classements...")
            coeffs = CoefficientsModule(self.data)
            analyzer = AnalyzerModule(coeffs)
            
            # Créer des onglets pour les 2 classements
            tabs = QTabWidget()
            
            # Classement annuel
            tab_annual = QWidget()
            layout_annual = QVBoxLayout(tab_annual)
            
            label_annual = QLabel("Classement Annuel par k(A)")
            label_annual.setFont(QFont("Arial", 12, QFont.Bold))
            layout_annual.addWidget(label_annual)
            
            table_annual = QTableWidget()
            df_annual = analyzer.generate_annual_ranking()
            table_annual.setRowCount(len(df_annual))
            table_annual.setColumnCount(len(df_annual.columns))
            table_annual.setHorizontalHeaderLabels(df_annual.columns.tolist())
            
            for i, row in df_annual.iterrows():
                for j, col in enumerate(df_annual.columns):
                    value = row[col]
                    if isinstance(value, float):
                        item = QTableWidgetItem(f"{value:.3f}")
                    else:
                        item = QTableWidgetItem(str(value))
                    table_annual.setItem(i, j, item)
            
            table_annual.resizeColumnsToContents()
            layout_annual.addWidget(table_annual)
            
            # Légende des qualifications
            legend_annual = QLabel(
                "Qualifications: Très humide (k(A)>1.2) | Humide (1.1-1.2) | "
                "Normal (0.9-1.1) | Sec (0.8-0.9) | Très sec (<0.8)"
            )
            legend_annual.setStyleSheet("color: #666; padding: 5px; font-size: 9pt;")
            legend_annual.setWordWrap(True)
            layout_annual.addWidget(legend_annual)
            
            tabs.addTab(tab_annual, "📊 Classement Annuel")
            
            # Classement mensuel
            tab_monthly = QWidget()
            layout_monthly = QVBoxLayout(tab_monthly)
            
            label_monthly = QLabel("Classement Mensuel par Q moyen")
            label_monthly.setFont(QFont("Arial", 12, QFont.Bold))
            layout_monthly.addWidget(label_monthly)
            
            table_monthly = QTableWidget()
            df_monthly = analyzer.generate_monthly_ranking()
            table_monthly.setRowCount(len(df_monthly))
            table_monthly.setColumnCount(len(df_monthly.columns))
            table_monthly.setHorizontalHeaderLabels(df_monthly.columns.tolist())
            
            for i, row in df_monthly.iterrows():
                for j, col in enumerate(df_monthly.columns):
                    value = row[col]
                    if isinstance(value, float):
                        item = QTableWidgetItem(f"{value:.3f}")
                    else:
                        item = QTableWidgetItem(str(value))
                    table_monthly.setItem(i, j, item)
            
            table_monthly.resizeColumnsToContents()
            layout_monthly.addWidget(table_monthly)
            
            # Légende des mois - adaptée selon la saison
            if season == 'dry':
                legend_text = "Mois de la saison sèche: Décembre, Janvier, Février, Mars, Avril, Mai, Juin (212 jours)"
            else:
                legend_text = "Mois de la saison des pluies: Juillet, Août, Septembre, Octobre, Novembre (153 jours)"
            
            legend_monthly = QLabel(legend_text)
            legend_monthly.setStyleSheet("color: #666; padding: 5px; font-size: 9pt;")
            layout_monthly.addWidget(legend_monthly)
            
            tabs.addTab(tab_monthly, "📅 Classement Mensuel")
            
            layout.addWidget(tabs)
            
            # Boutons
            btn_layout = QHBoxLayout()
            
            btn_export = QPushButton("📊 Exporter en Excel")
            btn_export.setStyleSheet("""
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
            """)
            
            def export_rankings():
                try:
                    export_mgr = ExportManager()
                    filename = f"classements_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    
                    # Créer un dictionnaire avec les 2 classements
                    data_dict = {
                        'Classement Annuel': df_annual,
                        'Classement Mensuel': df_monthly
                    }
                    
                    metadata = {
                        'generation_date': datetime.now(),
                        'description': 'Classements annuels et mensuels pour la saison des pluies'
                    }
                    
                    export_mgr.export_coefficients_to_excel(data_dict, filename, metadata)
                    
                    QMessageBox.information(dialog, "Succès", f"Classements exportés:\n{filename}")
                    self.status_label.setText(f"✅ Classements exportés: {filename}")
                    
                except Exception as e:
                    import traceback
                    error_msg = f"Erreur lors de l'export:\n{str(e)}\n\n{traceback.format_exc()}"
                    QMessageBox.critical(dialog, "Erreur", error_msg)
            
            btn_export.clicked.connect(export_rankings)
            
            btn_close = QPushButton("❌ Fermer")
            btn_close.setStyleSheet("""
                QPushButton {
                    background-color: #6c757d;
                    color: white;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5a6268;
                }
            """)
            btn_close.clicked.connect(dialog.close)
            
            btn_layout.addWidget(btn_export)
            btn_layout.addStretch()
            btn_layout.addWidget(btn_close)
            layout.addLayout(btn_layout)
            
            # Bouton Retour
            btn_back = QPushButton("⬅️ Retour au menu des phases")
            btn_back.setStyleSheet(self.get_button_style("#6c757d"))
            btn_back.clicked.connect(lambda: self.return_to_phase_menu(dialog, season))
            layout.addWidget(btn_back)
            
            self.status_label.setText("✅ Phase 5: Classements affichés")
            
            # Afficher le dialogue
            dialog.exec_()
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'analyse comparative:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur Phase 5")
    
    def generate_predictions_ml(self):
        """Génère les prédictions futures avec le modèle ML (nécessite entraînement)"""
        if self.predictor is None or self.predictor.model is None:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord entraîner un modèle")
            return
        
        try:
            self.status_label.setText("Génération des prédictions avec modèle ML...")
            
            # Générer les prédictions avec la méthode "Modèle ML"
            self.future_predictions = self._generate_future_predictions(method="Modèle ML")
            
            # Afficher les résultats
            method_details = self.future_predictions['method_details']
            
            text = f"""
PRÉDICTIONS FUTURES GÉNÉRÉES (MODÈLE ML)
{'='*60}

Année prédite: {self.future_predictions['year']}
Type de saison: {self.future_predictions['season_type'].capitalize()}
Nombre de jours: {len(self.future_predictions['predictions'])}
Période: {self.future_predictions['dates'][0].strftime('%d/%m/%Y')} au {self.future_predictions['dates'][-1].strftime('%d/%m/%Y')}

MÉTHODE DE PRÉDICTION:
{method_details['method_name']}
Formule: {method_details['formula']}
"""
            
            # Ajouter les détails spécifiques
            if 'r2_used' in method_details:
                text += f"R² du modèle: {method_details['r2_used']:.4f}\n"
            if 'coefficient_info' in method_details:
                text += f"{method_details['coefficient_info']}\n"
            if 'validation' in method_details:
                text += f"Validation: {method_details['validation']}\n"
            
            text += f"""
Années utilisées pour moyennes: {self.future_predictions['num_years_used']} dernières années hydrologiques

STATISTIQUES DES PRÉDICTIONS:
Débit moyen prédit: {sum(self.future_predictions['predictions'])/len(self.future_predictions['predictions']):.2f} m³/s
Débit min prédit: {min(self.future_predictions['predictions']):.2f} m³/s
Débit max prédit: {max(self.future_predictions['predictions']):.2f} m³/s

Utilisez "Exporter Prédictions" pour télécharger les prédictions.
            """
            
            self.prediction_text.setText(text)
            
            # Afficher l'onglet prédiction
            self.tabs.setCurrentIndex(2)
            
            self.status_label.setText("✅ Prédictions générées (ML)")
            QMessageBox.information(
                self,
                "Succès",
                f"Prédictions générées avec modèle ML!\n\n"
                f"Méthode: {method_details['method_name']}\n"
                f"Nombre de jours: {len(self.future_predictions['predictions'])}"
            )
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de la génération des prédictions:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur de génération")
    
    def export_predictions(self):
        """Exporte les prédictions de l'année future"""
        if self.future_predictions is None:
            QMessageBox.warning(
                self, 
                "Attention", 
                "Aucune prédiction disponible.\nVeuillez d'abord générer les prédictions."
            )
            return
        
        try:
            # Dialogue de choix du format
            format_dialog = QMessageBox(self)
            format_dialog.setWindowTitle("Choisir le format d'export")
            format_dialog.setText("Dans quel format voulez-vous exporter les prédictions?")
            btn_excel = format_dialog.addButton("📊 Excel", QMessageBox.AcceptRole)
            btn_pdf = format_dialog.addButton("📄 PDF", QMessageBox.AcceptRole)
            format_dialog.addButton("Annuler", QMessageBox.RejectRole)
            format_dialog.exec_()
            
            clicked_button = format_dialog.clickedButton()
            
            if clicked_button == btn_excel:
                self._export_predictions_excel()
            elif clicked_button == btn_pdf:
                self._export_predictions_pdf()
                
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'export:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
    
    def _export_predictions_excel(self):
        """Exporte les prédictions en Excel"""
        from datetime import datetime
        import pandas as pd
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer les prédictions", 
            f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.setText("Export des prédictions en cours...")
            
            # Utiliser les prédictions déjà générées
            predictions_df = pd.DataFrame({
                'Date': self.future_predictions['dates'],
                'Débit Prédit (m³/s)': self.future_predictions['predictions']
            })
            
            # Créer le fichier Excel avec plusieurs feuilles
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Feuille 1: Prédictions
                predictions_df.to_excel(writer, sheet_name='Prédictions', index=False)
                
                # Feuille 2: Métriques du modèle
                if self.predictor.metrics:
                    metrics_data = {
                        'Métrique': ['RMSE', 'MAE', 'R²'],
                        'Entraînement': [
                            self.predictor.metrics['train']['RMSE'],
                            self.predictor.metrics['train']['MAE'],
                            self.predictor.metrics['train']['R2']
                        ],
                        'Test': [
                            self.predictor.metrics['test']['RMSE'],
                            self.predictor.metrics['test']['MAE'],
                            self.predictor.metrics['test']['R2']
                        ]
                    }
                    metrics_df = pd.DataFrame(metrics_data)
                    metrics_df.to_excel(writer, sheet_name='Métriques', index=False)
            
            self.status_label.setText("✅ Prédictions exportées")
            QMessageBox.information(self, "Succès", f"Prédictions exportées:\n{file_path}")
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'export Excel:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur d'export")
    
    def _export_predictions_pdf(self):
        """Exporte les prédictions en PDF"""
        from datetime import datetime
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer les prédictions",
            f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            self.status_label.setText("Export des prédictions en cours...")
            
            # Créer le graphique des prédictions
            import matplotlib.pyplot as plt
            plt.figure(figsize=(12, 6))
            plt.plot(self.future_predictions['dates'], self.future_predictions['predictions'], 
                    'b-', linewidth=2, label='Prédictions')
            plt.xlabel('Date')
            plt.ylabel('Débit (m³/s)')
            plt.title(f'Prédictions pour l\'année {self.future_predictions["year"]}')
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            plot_path = os.path.join('exports', f'predictions_plot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Générer le PDF
            season_info = {
                'saison': 'Prédictions Futures',
                'annee': self.future_predictions['year'],
                'modele': self.combo_model.currentText()
            }
            
            data = {
                'season_info': season_info,
                'metrics': self.predictor.metrics,
                'plot_paths': [plot_path]
            }
            
            self.report_gen.export_to_pdf(data, os.path.basename(file_path))
            
            self.status_label.setText("✅ Prédictions exportées")
            QMessageBox.information(self, "Succès", f"Prédictions exportées:\n{file_path}")
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'export PDF:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur d'export")
    

    
    def _generate_future_predictions(self, method="Formule Mathématique"):
        """
        Génère les prédictions pour l'année future (n+1)
        
        DEUX MÉTHODES DISPONIBLES:
        1. Modèle ML: Utilise les prédictions du modèle entraîné
        2. Formule Mathématique: Formule spécifique pour saison pluies et saison sèche
        
        Args:
            method: "Modèle ML" ou "Formule Mathématique"
        """
        from datetime import datetime
        import pandas as pd
        import numpy as np
        
        # ✅ RÉCUPÉRER LE R² DU MODÈLE (pour formule saison sèche)
        r2 = self.predictor.metrics['test']['R2']
        
        # ✅ UTILISER LES 5 DERNIÈRES ANNÉES POUR LE CALCUL DES MOYENNES
        num_years = 5
        
        # ✅ DÉTECTER LA DERNIÈRE ANNÉE HYDROLOGIQUE ET SON TYPE
        last_year = self.years[-1]
        
        # Détecter si c'est saison sèche ou saison pluies
        if '-' in str(last_year):
            # SAISON SÈCHE : Format "2020-2021"
            season_type = "sèche"
            year_parts = str(last_year).split('-')
            end_year = int(year_parts[1])
            next_year = end_year + 1
            
            # Dates de prédiction pour saison sèche (Déc-Juin)
            start_date = datetime(end_year, 12, 1)
            end_date = datetime(next_year, 6, 30)
            
        else:
            # SAISON DES PLUIES : Format "2021"
            season_type = "pluies"
            year = int(last_year)
            next_year = year + 1
            
            # Dates de prédiction pour saison pluies (Juil-Nov)
            start_date = datetime(next_year, 7, 1)
            end_date = datetime(next_year, 11, 30)
        
        # Générer les dates futures
        future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # ✅ IDENTIFIER LES X DERNIÈRES ANNÉES HYDROLOGIQUES
        if len(self.years) >= num_years:
            last_n_years = self.years[-num_years:]
        else:
            last_n_years = self.years
        
        # ✅ CALCULER LES MOYENNES PAR JOUR CALENDAIRE SUR LES X DERNIÈRES ANNÉES
        if 'date' in self.data.columns and 'saison_annee' in self.data.columns:
            data_last_n_years = self.data[self.data['saison_annee'].isin(last_n_years)].copy()
            debit_col = [col for col in data_last_n_years.columns if 'debit' in col.lower()][0]
            
            data_last_n_years['mois'] = data_last_n_years['date'].dt.month
            data_last_n_years['jour_mois'] = data_last_n_years['date'].dt.day
            
            # Moyennes journalières
            daily_averages = data_last_n_years.groupby(['mois', 'jour_mois'])[debit_col].mean().to_dict()
            global_avg = data_last_n_years[debit_col].mean()
        else:
            debit_col = [col for col in self.data.columns if 'debit' in col.lower()][0]
            global_avg = self.data[debit_col].mean()
            daily_averages = {}
        
        # ✅ GÉNÉRER LES PRÉDICTIONS SELON LA MÉTHODE CHOISIE
        predictions = []
        method_details = {}
        
        if method == "Modèle ML":
            # MÉTHODE 1: Utiliser le modèle ML (ancienne méthode)
            for date in future_dates:
                key = (date.month, date.day)
                avg = daily_averages.get(key, global_avg)
                pred = r2 * avg
                predictions.append(pred)
            
            method_details = {
                'method_name': 'Modèle ML',
                'formula': 'R² × Moyenne historique',
                'r2_used': r2
            }
            
        else:  # Formule Mathématique
            
            if season_type == "pluies":
                # ============================================================
                # FORMULE SAISON PLUIES - ESPACE POUR NOUVELLE FORMULE
                # ============================================================
                debit_col = [col for col in self.data.columns if 'debit' in col.lower()][0]
                
                # TODO: Votre formule complète ici
                
                for date in future_dates:
                    pred = 0  # Placeholder
                    predictions.append(pred)
                
                method_details = {
                    'method_name': 'Formule Mathématique (Saison Pluies)',
                    'formula': 'À définir',
                    'coefficient_info': 'À définir',
                    'validation': 'À définir'
                }
                
            else:  # saison sèche
                # FORMULE SAISON SÈCHE: Q = R² × Q̄_jour (ancienne formule)
                for date in future_dates:
                    key = (date.month, date.day)
                    Q_jour_a = daily_averages.get(key, global_avg)
                    pred = r2 * Q_jour_a
                    predictions.append(pred)
                
                method_details = {
                    'method_name': 'Formule Mathématique (Saison Sèche)',
                    'formula': 'R² × Moyenne historique',
                    'r2_used': r2
                }
        
        return {
            'dates': future_dates,
            'predictions': predictions,
            'year': start_date.year,
            'num_years_used': len(last_n_years),
            'season_type': season_type,
            'method_details': method_details
        }
    
    def export_final_report(self):
        """Exporte le rapport final complet avec Phase 2, 4 et 5"""
        from datetime import datetime
        
        try:
            # Demander le nom du rapport à l'utilisateur
            from PyQt5.QtWidgets import QInputDialog
            report_name, ok = QInputDialog.getText(
                self, 
                "Nom du rapport", 
                "Entrez le nom du rapport:",
                text=f"Rapport_Hydrologique_{datetime.now().strftime('%Y%m%d')}"
            )
            
            if not ok or not report_name:
                return
            
            # Demander la saison pour les prédictions
            season_dialog = QMessageBox(self)
            season_dialog.setWindowTitle("Choisir la saison")
            season_dialog.setText("Quelle saison voulez-vous inclure dans le rapport?")
            btn_rainy = season_dialog.addButton("🌧️ Saison des Pluies", QMessageBox.AcceptRole)
            btn_dry = season_dialog.addButton("🌵 Saison Sèche", QMessageBox.AcceptRole)
            season_dialog.addButton("Annuler", QMessageBox.RejectRole)
            season_dialog.exec_()
            
            clicked_button = season_dialog.clickedButton()
            
            if clicked_button == btn_rainy:
                selected_season = 'rainy'
            elif clicked_button == btn_dry:
                selected_season = 'dry'
            else:
                return
            
            # Générer le rapport PDF complet
            self._generate_comprehensive_pdf_report(report_name, selected_season)
                
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de l'export:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
    
    def _generate_comprehensive_pdf_report(self, report_name, season):
        """Génère le rapport PDF complet avec toutes les phases"""
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
        from reportlab.lib.units import inch
        from reportlab.pdfgen import canvas
        from datetime import datetime
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        
        file_path = os.path.join('exports', f'{report_name}.pdf')
        
        try:
            self.status_label.setText("📄 Génération du rapport complet...")
            
            # Créer le document PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Style personnalisé pour le titre
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=30,
                alignment=1  # Centré
            )
            
            # Style pour les en-têtes de section
            section_style = ParagraphStyle(
                'SectionHeader',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1f4788'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # PAGE DE GARDE
            story.append(Spacer(1, 2*inch))
            story.append(Paragraph("Rapport de Prédiction Hydrologique", title_style))
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph(f"<b>{report_name}</b>", styles['Title']))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(f"Date: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
            story.append(Paragraph(f"Barrage de Mbakaou", styles['Normal']))
            story.append(PageBreak())
            
            # PHASE 2: ANALYSE DES DONNÉES
            story.append(Paragraph("PHASE 2 : ANALYSE DES DONNÉES", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Texte explicatif Phase 2
            phase2_text = f"""
            Cette section présente l'analyse statistique des données hydrologiques du barrage de Mbakaou.
            Les données couvrent {len(self.years)} années hydrologiques de {self.years[0]} à {self.years[-1]}.
            L'analyse inclut les débits moyens, minimums, maximums ainsi que les tendances observées.
            """
            story.append(Paragraph(phase2_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Tableau statistiques Phase 2
            stats_data = [['Paramètre', 'Valeur']]
            stats_data.append(['Nombre d\'années', str(len(self.years))])
            stats_data.append(['Période', f'{self.years[0]} - {self.years[-1]}'])
            stats_data.append(['Total observations', str(len(self.data))])
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(stats_table)
            story.append(PageBreak())
            
            # GRAPHIQUES DES DÉBITS PAR ANNÉE
            story.append(Paragraph("Graphiques des débits par année", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            plot_paths = []
            for year in self.years:
                year_data = self.data[self.data['saison_annee'] == year]
                
                plt.figure(figsize=(10, 6))
                plt.plot(year_data.index, year_data['debits'], linewidth=2, color='#1f4788')
                plt.xlabel('Jours', fontsize=12)
                plt.ylabel('Débit (m³/s)', fontsize=12)
                plt.title(f'Débits - Année {year}', fontsize=14, fontweight='bold')
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                
                plot_path = os.path.join('exports', f'debit_{year}_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
                plt.savefig(plot_path, dpi=150, bbox_inches='tight')
                plt.close()
                plot_paths.append(plot_path)
                
                # Ajouter le graphique au PDF
                img = Image(plot_path, width=6*inch, height=3.6*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
                story.append(PageBreak())
            
            # PHASE 4: PRÉDICTIONS (FORMULE)
            story.append(Paragraph("PHASE 4 : PRÉDICTIONS PAR FORMULE", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Générer les prédictions
            predictions_data = self._generate_formula_predictions_for_report(season)
            
            if predictions_data:
                # Texte explicatif Phase 4
                phase4_text = f"""
                Les prédictions sont générées à l'aide de la formule mathématique calibrée sur les données historiques.
                Saison: {'Sèche (Décembre-Juin)' if season == 'dry' else 'Pluies (Juillet-Novembre)'}.
                La formule prend en compte les coefficients mensuels et le coefficient annuel k(A).
                """
                story.append(Paragraph(phase4_text, styles['Normal']))
                story.append(Spacer(1, 0.3*inch))
                
                # Graphique des prédictions avec couleurs
                plt.figure(figsize=(12, 7))
                plt.plot(predictions_data['t'], predictions_data['Q_central'], 
                        linewidth=2.5, color='#1f4788', label='Q central', marker='o', markersize=3)
                plt.fill_between(predictions_data['t'], predictions_data['Q_min'], predictions_data['Q_max'],
                                alpha=0.3, color='#87CEEB', label='Intervalle de confiance')
                plt.plot(predictions_data['t'], predictions_data['Q_min'], 
                        linewidth=1.5, color='#DC143C', linestyle='--', label='Q min')
                plt.plot(predictions_data['t'], predictions_data['Q_max'], 
                        linewidth=1.5, color='#228B22', linestyle='--', label='Q max')
                
                plt.xlabel('Jour de saison', fontsize=12, fontweight='bold')
                plt.ylabel('Débit (m³/s)', fontsize=12, fontweight='bold')
                plt.title('Prédictions des débits - Formule mathématique', fontsize=14, fontweight='bold')
                plt.legend(loc='best', fontsize=10)
                plt.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
                plt.tight_layout()
                
                pred_plot_path = os.path.join('exports', f'predictions_{datetime.now().strftime("%Y%m%d%H%M%S")}.png')
                plt.savefig(pred_plot_path, dpi=200, bbox_inches='tight')
                plt.close()
                plot_paths.append(pred_plot_path)
                
                img_pred = Image(pred_plot_path, width=6.5*inch, height=4.5*inch)
                story.append(img_pred)
                story.append(PageBreak())
            
            # PHASE 5: ANALYSE COMPARATIVE
            story.append(Paragraph("PHASE 5 : ANALYSE COMPARATIVE", section_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Texte explicatif Phase 5
            phase5_text = """
            Cette section présente les classements annuels et mensuels basés sur les coefficients k(A) 
            et les débits moyens. Les années sont classées selon leur niveau d'humidité.
            """
            story.append(Paragraph(phase5_text, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Générer les classements
            comparative_data = self._generate_comparative_analysis_for_report(season)
            
            if comparative_data:
                # Tableau classement annuel
                story.append(Paragraph("Classement Annuel", styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                annual_table_data = [['Rang', 'Année', 'k(A)', 'Q moy', 'Statut']]
                for _, row in comparative_data['annual'].head(10).iterrows():
                    annual_table_data.append([
                        str(row['Rang']),
                        str(row['Année']),
                        f"{row['k(A)']:.3f}",
                        f"{row['Q moy']:.2f}",
                        str(row['Qualif.'])
                    ])
                
                annual_table = Table(annual_table_data, colWidths=[0.8*inch, 1.2*inch, 1*inch, 1.2*inch, 1.5*inch])
                annual_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(annual_table)
                story.append(Spacer(1, 0.3*inch))
                
                # Tableau classement mensuel
                story.append(Paragraph("Classement Mensuel", styles['Heading3']))
                story.append(Spacer(1, 0.1*inch))
                
                monthly_table_data = [['Rang', 'Mois', 'Q moy', 'Cm', 'Statut']]
                for _, row in comparative_data['monthly'].iterrows():
                    monthly_table_data.append([
                        str(row['Rang']),
                        str(row['Mois']),
                        f"{row['Q moy']:.2f}",
                        f"{row['Cm']:.3f}",
                        str(row['Statut'])
                    ])
                
                monthly_table = Table(monthly_table_data, colWidths=[0.8*inch, 1.5*inch, 1.2*inch, 1*inch, 1.5*inch])
                monthly_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(monthly_table)
            
            story.append(PageBreak())
            
            # TABLE DES MATIÈRES (à la fin)
            story.append(Paragraph("TABLE DES MATIÈRES", section_style))
            story.append(Spacer(1, 0.3*inch))
            
            toc_data = [
                ['Section', 'Page'],
                ['Page de garde', '1'],
                ['Phase 2 : Analyse des données', '2'],
                [f'  - Graphiques des débits ({len(self.years)} années)', '3'],
                ['Phase 4 : Prédictions par formule', f'{3 + len(self.years)}'],
                ['Phase 5 : Analyse comparative', f'{4 + len(self.years)}'],
                ['Table des matières', f'{5 + len(self.years)}']
            ]
            
            toc_table = Table(toc_data, colWidths=[4.5*inch, 1*inch])
            toc_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            story.append(toc_table)
            
            # Construire le PDF avec en-tête personnalisé
            def add_header(canvas, doc):
                canvas.saveState()
                canvas.setFont('Helvetica-Bold', 10)
                canvas.setFillColor(colors.HexColor('#1f4788'))
                canvas.drawString(inch, A4[1] - 0.5*inch, "Rapport de Prédiction Hydrologique")
                canvas.setFont('Helvetica', 8)
                canvas.drawRightString(A4[0] - inch, A4[1] - 0.5*inch, f"Page {doc.page}")
                canvas.line(inch, A4[1] - 0.6*inch, A4[0] - inch, A4[1] - 0.6*inch)
                canvas.restoreState()
            
            doc.build(story, onFirstPage=add_header, onLaterPages=add_header)
            
            # Nettoyer les fichiers temporaires
            for plot_path in plot_paths:
                try:
                    if os.path.exists(plot_path):
                        os.remove(plot_path)
                except:
                    pass
            
            self.status_label.setText("✅ Rapport complet généré")
            QMessageBox.information(self, "Succès", f"Rapport complet exporté:\n{file_path}")
            
        except Exception as e:
            import traceback
            error_msg = f"Erreur lors de la génération du rapport:\n{str(e)}\n\n{traceback.format_exc()}"
            QMessageBox.critical(self, "Erreur", error_msg)
            self.status_label.setText("❌ Erreur de génération")
    
    def _generate_formula_predictions_for_report(self, season):
        """Génère les prédictions par formule pour le rapport"""
        try:
            if season == 'dry':
                formula = self.controller.get_formula_module_dry()
                from backend.formula.generator_module_seche import GeneratorModuleSeche
                generator = GeneratorModuleSeche(formula)
                duration = 212
            else:
                formula = self.controller.get_formula_module_rainy()
                from backend.formula.generator_module import GeneratorModule
                generator = GeneratorModule(formula)
                duration = 153
            
            # Utiliser k(A) = 1.0 et epsilon = 0.05 par défaut
            k_A = 1.0
            epsilon = 0.05
            
            full_table = generator.generate_full_season(k_A, epsilon)
            
            return {
                't': full_table['t'].values,
                'Q_central': full_table['Q centrale'].values if 'Q centrale' in full_table.columns else full_table['Q_central'].values,
                'Q_min': full_table['Q min (-80%)'].values if 'Q min (-80%)' in full_table.columns else full_table['Q_inf'].values,
                'Q_max': full_table['Q max (+8%)'].values if 'Q max (+8%)' in full_table.columns else full_table['Q_sup'].values
            }
        except Exception as e:
            print(f"Erreur génération prédictions: {e}")
            return None
    
    def _generate_comparative_analysis_for_report(self, season):
        """Génère l'analyse comparative pour le rapport"""
        try:
            if season == 'dry':
                from backend.formula.analyzer_module_seche import AnalyzerModuleSeche
                from backend.formula.coefficients_module_seche import CoefficientsModuleSeche
                coeffs = CoefficientsModuleSeche(self.data)
                analyzer = AnalyzerModuleSeche(coeffs)
            else:
                from backend.formula.analyzer_module import AnalyzerModule
                from backend.formula.coefficients_module import CoefficientsModule
                coeffs = CoefficientsModule(self.data)
                analyzer = AnalyzerModule(coeffs)
            
            annual_ranking = analyzer.generate_annual_ranking()
            monthly_ranking = analyzer.generate_monthly_ranking()
            
            return {
                'annual': annual_ranking,
                'monthly': monthly_ranking
            }
        except Exception as e:
            print(f"Erreur génération analyse comparative: {e}")
            return None

    
    def save_model(self):
        """Sauvegarde le modèle entraîné"""
        if self.predictor is None or self.predictor.model is None:
            QMessageBox.warning(self, "Attention", "Aucun modèle à sauvegarder. Veuillez d'abord entraîner un modèle.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder le modèle", "modele.pkl", "Pickle Files (*.pkl)"
        )
        
        if file_path:
            try:
                success = self.predictor.save_model(file_path)
                if success:
                    QMessageBox.information(self, "Succès", f"Modèle sauvegardé avec succès:\n{file_path}")
                    self.status_label.setText("✅ Modèle sauvegardé")
                else:
                    QMessageBox.warning(self, "Erreur", "Échec de la sauvegarde du modèle")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de la sauvegarde:\n{str(e)}")
    
    def load_model(self):
        """Charge un modèle sauvegardé"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Charger un modèle", "", "Pickle Files (*.pkl)"
        )
        
        if file_path:
            try:
                # Créer un predictor si nécessaire
                if self.predictor is None:
                    model_name = self.combo_model.currentText()
                    self.predictor = FlowPredictor(model_name)
                
                success = self.predictor.load_model(file_path)
                if success:
                    QMessageBox.information(self, "Succès", f"Modèle chargé avec succès:\n{file_path}")
                    self.status_label.setText("✅ Modèle chargé")
                    
                    # Activer les boutons
                    self.btn_export_report.setEnabled(True)
                    if hasattr(self, 'btn_save_model'):
                        self.btn_save_model.setEnabled(True)
                else:
                    QMessageBox.warning(self, "Erreur", "Échec du chargement du modèle")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
    
    def goto_phase1(self):
        """Retourne à la Phase 1"""
        from phase1_transformation import TransformationWindow
        self.phase1_window = TransformationWindow()
        self.phase1_window.show()
        self.close()
    
    def set_background_image(self):
        """Définit l'image de fond avec opacité de 95%"""
        image_path = os.path.join('image', 'mbaka.png')
        if os.path.exists(image_path):
            central_widget = self.centralWidget()
            if central_widget:
                palette = QPalette()
                pixmap = QPixmap(image_path)
                # Redimensionner l'image pour qu'elle s'adapte à la fenêtre
                scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
                central_widget.setPalette(palette)
                central_widget.setAutoFillBackground(True)
            
            # Appliquer l'opacité de 95% à la fenêtre
            self.setWindowOpacity(0.95)


def main():
    """Fonction principale Phase 2"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = PredictionWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
