"""
Interface principale de l'application
"""
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QComboBox, QFileDialog, 
                             QTabWidget, QTableWidget, QTableWidgetItem, QMessageBox,
                             QProgressBar, QTextEdit, QGroupBox, QSplitter, QDialog,
                             QRadioButton, QDialogButtonBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QPalette, QBrush, QFont, QImage, QPainter
import sys
import os
import pandas as pd
from typing import Dict, Optional


class WorkerThread(QThread):
    """Thread pour les opérations longues"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prévision Hydrologique - Barrage de Mbakaou")
        self.setGeometry(100, 100, 1400, 900)
        
        # Variables
        self.data_file = None
        self.current_season = None
        self.current_model = None
        self.current_year = None
        self.current_data = None
        
        # Backend controller
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from backend.core.application_controller import ApplicationController
        self.controller = ApplicationController()
        
        # Initialiser l'interface
        self.init_ui()
        self.set_background()
        
    def set_background(self):
        """Définit l'image de fond avec transparence"""
        try:
            bg_path = os.path.join("image", "mbaka.png")
            if os.path.exists(bg_path):
                palette = QPalette()
                pixmap = QPixmap(bg_path)
                
                # Créer une version semi-transparente
                image = pixmap.toImage()
                painter = QPainter(image)
                painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
                painter.fillRect(image.rect(), Qt.transparent)
                painter.setOpacity(0.25)  # 75% de transparence = 25% d'opacité
                painter.drawPixmap(0, 0, pixmap)
                painter.end()
                
                pixmap = QPixmap.fromImage(image)
                palette.setBrush(QPalette.Background, QBrush(pixmap.scaled(
                    self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
                )))
                self.setPalette(palette)
        except Exception as e:
            print(f"Erreur chargement image: {e}")
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # En-tête
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Zone de contrôle
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Onglets principaux
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_data_tab(), "📊 Données")
        self.tabs.addTab(self.create_analysis_tab(), "📈 Analyse")
        self.tabs.addTab(self.create_prediction_tab(), "🤖 Prédiction ML")
        self.tabs.addTab(self.create_formula_dry_tab(), "🌵 Prédiction Saison Sèche")
        self.tabs.addTab(self.create_formula_rainy_tab(), "🌧️ Prédiction Saison Pluies")
        self.tabs.addTab(self.create_climate_tab(), "☁️ Climat")
        self.tabs.addTab(self.create_export_tab(), "📤 Export")
        
        main_layout.addWidget(self.tabs)
        
        # Barre de statut
        self.status_label = QLabel("Prêt")
        main_layout.addWidget(self.status_label)
    
    def create_header(self) -> QWidget:
        """Crée l'en-tête de l'application"""
        header = QWidget()
        header.setStyleSheet("background-color: rgba(31, 71, 136, 0.9); padding: 20px; border-radius: 10px;")
        layout = QVBoxLayout(header)
        
        title = QLabel("🌊 Système de Prévision Hydrologique")
        title.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        
        subtitle = QLabel("Barrage de Mbakaou - Analyse et Modélisation")
        subtitle.setStyleSheet("color: white; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(subtitle)
        
        return header
    
    def create_control_panel(self) -> QWidget:
        """Crée le panneau de contrôle"""
        panel = QGroupBox("Contrôles")
        panel.setStyleSheet("QGroupBox { background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; padding: 15px; }")
        layout = QHBoxLayout(panel)
        
        # Bouton charger fichier
        self.btn_load = QPushButton("📁 Charger Données Excel")
        self.btn_load.clicked.connect(self.load_data)
        self.btn_load.setStyleSheet(self.get_button_style())
        layout.addWidget(self.btn_load)
        
        # Sélection saison
        layout.addWidget(QLabel("Saison:"))
        self.combo_season = QComboBox()
        self.combo_season.addItems(["Saison Sèche", "Saison des Pluies"])
        self.combo_season.currentTextChanged.connect(self.on_season_changed)
        layout.addWidget(self.combo_season)
        
        # Sélection année
        layout.addWidget(QLabel("Année:"))
        self.combo_year = QComboBox()
        layout.addWidget(self.combo_year)
        
        # Sélection modèle
        layout.addWidget(QLabel("Modèle:"))
        self.combo_model = QComboBox()
        self.combo_model.addItems([
            "Random Forest",
            "Régression Linéaire",
            "SARIMA",
            "AdaBoost",
            "XGBoost"
        ])
        layout.addWidget(self.combo_model)
        
        # Bouton analyser
        self.btn_analyze = QPushButton("🔍 Analyser")
        self.btn_analyze.clicked.connect(self.run_analysis)
        self.btn_analyze.setEnabled(False)
        self.btn_analyze.setStyleSheet(self.get_button_style("#28a745"))
        layout.addWidget(self.btn_analyze)
        
        # Bouton prédire
        self.btn_predict = QPushButton("🎯 Prédire")
        self.btn_predict.clicked.connect(self.run_prediction)
        self.btn_predict.setEnabled(False)
        self.btn_predict.setStyleSheet(self.get_button_style("#007bff"))
        layout.addWidget(self.btn_predict)
        
        return panel
    
    def get_button_style(self, color: str = "#1f4788") -> str:
        """Style des boutons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
            }}
        """
    
    def create_data_tab(self) -> QWidget:
        """Onglet des données"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Informations sur les données
        self.data_info = QTextEdit()
        self.data_info.setReadOnly(True)
        self.data_info.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px;")
        layout.addWidget(QLabel("Informations sur les données:"))
        layout.addWidget(self.data_info)
        
        # Tableau de données
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet("background-color: rgba(255, 255, 255, 0.9);")
        layout.addWidget(QLabel("Aperçu des données:"))
        layout.addWidget(self.data_table)
        
        # Boutons d'export
        btn_layout = QHBoxLayout()
        btn_export_dry = QPushButton("💾 Exporter Saison Sèche")
        btn_export_dry.clicked.connect(lambda: self.export_season_data('dry'))
        btn_export_rainy = QPushButton("💾 Exporter Saison Pluies")
        btn_export_rainy.clicked.connect(lambda: self.export_season_data('rainy'))
        btn_layout.addWidget(btn_export_dry)
        btn_layout.addWidget(btn_export_rainy)
        layout.addLayout(btn_layout)
        
        return tab
    
    def create_analysis_tab(self) -> QWidget:
        """Onglet d'analyse"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.analysis_results = QTextEdit()
        self.analysis_results.setReadOnly(True)
        self.analysis_results.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px; font-family: Consolas;")
        layout.addWidget(self.analysis_results)
        
        return tab
    
    def create_prediction_tab(self) -> QWidget:
        """Onglet de prédiction"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.prediction_results = QTextEdit()
        self.prediction_results.setReadOnly(True)
        self.prediction_results.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px; font-family: Consolas;")
        layout.addWidget(self.prediction_results)
        
        # Bouton export prédictions
        btn_export = QPushButton("📥 Télécharger Prédictions (Excel/PDF)")
        btn_export.clicked.connect(self.export_predictions)
        btn_export.setStyleSheet(self.get_button_style("#17a2b8"))
        layout.addWidget(btn_export)
        
        return tab
    
    def create_formula_dry_tab(self) -> QWidget:
        """Onglet de prédiction par formule - SAISON SÈCHE"""
        from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # En-tête saison sèche
        header = QLabel("🌵 PRÉDICTION SAISON SÈCHE (Décembre → Juin)")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #d97706; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Panneau de contrôle formule
        control_group = QGroupBox("Paramètres de la Formule - Saison Sèche")
        control_group.setStyleSheet("QGroupBox { background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; padding: 15px; }")
        control_layout = QVBoxLayout(control_group)
        
        # Info saison
        info_label = QLabel("📅 Durée: 212 jours (1er décembre → 30 juin) | R² = 0.994")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        control_layout.addWidget(info_label)
        
        # Jour de saison
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Jour de saison (t):"))
        self.dry_day_spin = QSpinBox()
        self.dry_day_spin.setMinimum(1)
        self.dry_day_spin.setMaximum(212)
        self.dry_day_spin.setValue(110)  # Défaut: mi-mars (étiage)
        day_layout.addWidget(self.dry_day_spin)
        day_layout.addWidget(QLabel("(1=1er déc, 110=mi-mars étiage, 212=30 juin)"))
        control_layout.addLayout(day_layout)
        
        # Coefficient k(A)
        ka_layout = QHBoxLayout()
        ka_layout.addWidget(QLabel("Coefficient k(A):"))
        self.dry_ka_spin = QDoubleSpinBox()
        self.dry_ka_spin.setMinimum(0.1)
        self.dry_ka_spin.setMaximum(2.0)
        self.dry_ka_spin.setValue(1.0)
        self.dry_ka_spin.setSingleStep(0.1)
        self.dry_ka_spin.setDecimals(4)
        ka_layout.addWidget(self.dry_ka_spin)
        ka_layout.addWidget(QLabel("(0.58=très sec, 1.0=normal, 1.39=très humide)"))
        control_layout.addLayout(ka_layout)
        
        # Taux d'erreur epsilon
        epsilon_layout = QHBoxLayout()
        epsilon_layout.addWidget(QLabel("Taux erreur ε (%):"))
        self.dry_epsilon_spin = QDoubleSpinBox()
        self.dry_epsilon_spin.setMinimum(1.0)
        self.dry_epsilon_spin.setMaximum(8.0)
        self.dry_epsilon_spin.setValue(8.0)
        self.dry_epsilon_spin.setSingleStep(0.5)
        self.dry_epsilon_spin.setDecimals(1)
        epsilon_layout.addWidget(self.dry_epsilon_spin)
        epsilon_layout.addWidget(QLabel("(marge d'incertitude: 1-8%)"))
        control_layout.addLayout(epsilon_layout)
        
        # Année
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Année:"))
        self.dry_year_spin = QSpinBox()
        self.dry_year_spin.setMinimum(2020)
        self.dry_year_spin.setMaximum(2030)
        self.dry_year_spin.setValue(2025)
        year_layout.addWidget(self.dry_year_spin)
        control_layout.addLayout(year_layout)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        btn_calc_day = QPushButton("🔢 Calculer Jour Unique")
        btn_calc_day.clicked.connect(lambda: self.calculate_single_day_formula('dry'))
        btn_calc_day.setStyleSheet(self.get_button_style("#d97706"))
        btn_layout.addWidget(btn_calc_day)
        
        btn_gen_season = QPushButton("📊 Générer Saison Complète (212 jours)")
        btn_gen_season.clicked.connect(lambda: self.generate_full_season_formula('dry'))
        btn_gen_season.setStyleSheet(self.get_button_style("#ea580c"))
        btn_layout.addWidget(btn_gen_season)
        
        btn_export_formula = QPushButton("💾 Exporter vers Excel")
        btn_export_formula.clicked.connect(lambda: self.export_formula_results('dry'))
        btn_export_formula.setStyleSheet(self.get_button_style("#17a2b8"))
        btn_layout.addWidget(btn_export_formula)
        
        control_layout.addLayout(btn_layout)
        
        layout.addWidget(control_group)
        
        # Zone de résultats
        self.dry_results = QTextEdit()
        self.dry_results.setReadOnly(True)
        self.dry_results.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px; font-family: Consolas;")
        layout.addWidget(self.dry_results)
        
        # Stocker les résultats pour export
        self.dry_formula_df = None
        
        return tab
    
    def create_formula_rainy_tab(self) -> QWidget:
        """Onglet de prédiction par formule - SAISON PLUIES"""
        from PyQt5.QtWidgets import QDoubleSpinBox, QSpinBox
        
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # En-tête saison pluies
        header = QLabel("🌧️ PRÉDICTION SAISON PLUIES (Juillet → Novembre)")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2563eb; padding: 10px;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Panneau de contrôle formule
        control_group = QGroupBox("Paramètres de la Formule - Saison Pluies")
        control_group.setStyleSheet("QGroupBox { background-color: rgba(255, 255, 255, 0.9); border-radius: 10px; padding: 15px; }")
        control_layout = QVBoxLayout(control_group)
        
        # Info saison
        info_label = QLabel("📅 Durée: 153 jours (1er juillet → 30 novembre) | R² = 0.988")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        control_layout.addWidget(info_label)
        
        # Jour de saison
        day_layout = QHBoxLayout()
        day_layout.addWidget(QLabel("Jour de saison (t):"))
        self.rainy_day_spin = QSpinBox()
        self.rainy_day_spin.setMinimum(1)
        self.rainy_day_spin.setMaximum(153)
        self.rainy_day_spin.setValue(100)  # Défaut: mi-octobre (crue)
        day_layout.addWidget(self.rainy_day_spin)
        day_layout.addWidget(QLabel("(1=1er juil, 100=mi-oct crue, 153=30 nov)"))
        control_layout.addLayout(day_layout)
        
        # Coefficient k(A)
        ka_layout = QHBoxLayout()
        ka_layout.addWidget(QLabel("Coefficient k(A):"))
        self.rainy_ka_spin = QDoubleSpinBox()
        self.rainy_ka_spin.setMinimum(0.1)
        self.rainy_ka_spin.setMaximum(2.0)
        self.rainy_ka_spin.setValue(1.0)
        self.rainy_ka_spin.setSingleStep(0.1)
        self.rainy_ka_spin.setDecimals(4)
        ka_layout.addWidget(self.rainy_ka_spin)
        ka_layout.addWidget(QLabel("(0.8=sec, 1.0=normal, 1.2=humide)"))
        control_layout.addLayout(ka_layout)
        
        # Taux d'erreur epsilon
        epsilon_layout = QHBoxLayout()
        epsilon_layout.addWidget(QLabel("Taux erreur ε (%):"))
        self.rainy_epsilon_spin = QDoubleSpinBox()
        self.rainy_epsilon_spin.setMinimum(1.0)
        self.rainy_epsilon_spin.setMaximum(8.0)
        self.rainy_epsilon_spin.setValue(8.0)
        self.rainy_epsilon_spin.setSingleStep(0.5)
        self.rainy_epsilon_spin.setDecimals(1)
        epsilon_layout.addWidget(self.rainy_epsilon_spin)
        epsilon_layout.addWidget(QLabel("(marge d'incertitude: 1-8%)"))
        control_layout.addLayout(epsilon_layout)
        
        # Année
        year_layout = QHBoxLayout()
        year_layout.addWidget(QLabel("Année:"))
        self.rainy_year_spin = QSpinBox()
        self.rainy_year_spin.setMinimum(2020)
        self.rainy_year_spin.setMaximum(2030)
        self.rainy_year_spin.setValue(2025)
        year_layout.addWidget(self.rainy_year_spin)
        control_layout.addLayout(year_layout)
        
        # Boutons d'action
        btn_layout = QHBoxLayout()
        
        btn_calc_day = QPushButton("🔢 Calculer Jour Unique")
        btn_calc_day.clicked.connect(lambda: self.calculate_single_day_formula('rainy'))
        btn_calc_day.setStyleSheet(self.get_button_style("#2563eb"))
        btn_layout.addWidget(btn_calc_day)
        
        btn_gen_season = QPushButton("📊 Générer Saison Complète (153 jours)")
        btn_gen_season.clicked.connect(lambda: self.generate_full_season_formula('rainy'))
        btn_gen_season.setStyleSheet(self.get_button_style("#1d4ed8"))
        btn_layout.addWidget(btn_gen_season)
        
        btn_export_formula = QPushButton("💾 Exporter vers Excel")
        btn_export_formula.clicked.connect(lambda: self.export_formula_results('rainy'))
        btn_export_formula.setStyleSheet(self.get_button_style("#17a2b8"))
        btn_layout.addWidget(btn_export_formula)
        
        control_layout.addLayout(btn_layout)
        
        layout.addWidget(control_group)
        
        # Zone de résultats
        self.rainy_results = QTextEdit()
        self.rainy_results.setReadOnly(True)
        self.rainy_results.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px; font-family: Consolas;")
        layout.addWidget(self.rainy_results)
        
        # Stocker les résultats pour export
        self.rainy_formula_df = None
        
        return tab
    
    def create_climate_tab(self) -> QWidget:
        """Onglet climatique"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.climate_results = QTextEdit()
        self.climate_results.setReadOnly(True)
        self.climate_results.setStyleSheet("background-color: rgba(255, 255, 255, 0.9); border-radius: 5px; padding: 10px; font-family: Consolas;")
        layout.addWidget(self.climate_results)
        
        return tab
    
    def create_export_tab(self) -> QWidget:
        """Onglet d'export"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("Options d'export:"))
        
        btn_excel = QPushButton("📊 Exporter vers Excel")
        btn_excel.clicked.connect(lambda: self.export_report('excel'))
        btn_excel.setStyleSheet(self.get_button_style("#28a745"))
        
        btn_pdf = QPushButton("📄 Exporter vers PDF")
        btn_pdf.clicked.connect(lambda: self.export_report('pdf'))
        btn_pdf.setStyleSheet(self.get_button_style("#dc3545"))
        
        layout.addWidget(btn_excel)
        layout.addWidget(btn_pdf)
        layout.addStretch()
        
        return tab
    
    def load_data(self):
        """Charge les données depuis un fichier Excel"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier de données", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            self.data_file = file_path
            self.status_label.setText(f"Chargement: {os.path.basename(file_path)}")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Mode indéterminé
            
            # Charger via le backend
            result = self.controller.load_and_transform_data(file_path)
            
            self.progress_bar.setVisible(False)
            
            if result['success']:
                # Stocker les données chargées
                season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
                self.current_data = self.controller.get_season_data(season_type)
                
                # Mettre à jour les années disponibles
                self.update_year_combo()
                
                # Afficher les informations
                info_text = f"""
📊 DONNÉES CHARGÉES AVEC SUCCÈS

🌵 Saison Sèche:
   - Nombre d'années: {result['dry_season']['stats']['nombre_annees']}
   - Années disponibles: {', '.join(result['dry_season']['years'])}
   - Observations: {result['dry_season']['stats']['nombre_observations']}

🌧️ Saison des Pluies:
   - Nombre d'années: {result['rainy_season']['stats']['nombre_annees']}
   - Années disponibles: {', '.join(result['rainy_season']['years'])}
   - Observations: {result['rainy_season']['stats']['nombre_observations']}
                """
                self.data_info.setText(info_text)
                
                # Afficher aperçu des données
                self.display_data_preview()
                
                self.btn_analyze.setEnabled(True)
                self.status_label.setText("Données chargées - Prêt pour l'analyse")
                QMessageBox.information(self, "Succès", result['message'])
            else:
                QMessageBox.critical(self, "Erreur", result['message'])
                self.status_label.setText("Erreur de chargement")
    
    def update_year_combo(self):
        """Met à jour la liste des années disponibles"""
        season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
        years = self.controller.get_available_years(season_type)
        
        self.combo_year.clear()
        self.combo_year.addItems(years)
    
    def display_data_preview(self):
        """Affiche un aperçu des données dans le tableau"""
        season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
        data = self.controller.get_season_data(season_type)
        
        if data is not None and len(data) > 0:
            # Afficher les 100 premières lignes
            preview = data.head(100)
            
            self.data_table.setRowCount(len(preview))
            self.data_table.setColumnCount(len(preview.columns))
            self.data_table.setHorizontalHeaderLabels(preview.columns.tolist())
            
            for i in range(len(preview)):
                for j, col in enumerate(preview.columns):
                    value = str(preview.iloc[i, j])
                    self.data_table.setItem(i, j, QTableWidgetItem(value))
    
    def on_season_changed(self, season: str):
        """Gère le changement de saison"""
        self.current_season = season
        self.update_year_combo()
        if self.data_file:
            # Recharger les données pour la nouvelle saison
            season_type = 'dry' if season == "Saison Sèche" else 'rainy'
            self.current_data = self.controller.get_season_data(season_type)
            self.display_data_preview()
    
    def run_analysis(self):
        """Lance l'analyse"""
        self.status_label.setText("Analyse en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
        year = self.combo_year.currentText()
        self.current_year = year
        
        # Analyse des débits
        result = self.controller.analyze_flows(season_type, year)
        
        self.progress_bar.setVisible(False)
        
        if result['success']:
            analysis = result['results']
            
            # Formater les résultats
            text = f"""
╔══════════════════════════════════════════════════════════════╗
║           ANALYSE HYDROLOGIQUE DES DÉBITS                    ║
╚══════════════════════════════════════════════════════════════╝

📊 ANALYSE TEMPORELLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Moyenne:              {analysis['temporelle']['moyenne']:.2f} m³/s
Médiane:              {analysis['temporelle']['mediane']:.2f} m³/s
Écart-type:           {analysis['temporelle']['ecart_type']:.2f} m³/s
Minimum:              {analysis['temporelle']['min']:.2f} m³/s
Maximum:              {analysis['temporelle']['max']:.2f} m³/s
Coeff. Variation:     {analysis['temporelle']['coefficient_variation']:.2f}%

📈 TENDANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type:                 {analysis['temporelle']['tendance']['tendance_type']}
Pente:                {analysis['temporelle']['tendance']['pente']:.6f}
R²:                   {analysis['temporelle']['tendance']['r2']:.4f}
P-value:              {analysis['temporelle']['tendance']['p_value']:.6f}

⚠️ ANOMALIES DÉTECTÉES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nombre d'anomalies:   {analysis['temporelle']['anomalies']['nombre']}

🔄 AUTOCORRÉLATION (LAG ANALYSIS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            for lag, corr in analysis['dynamique']['autocorrelation'].items():
                text += f"{lag}: {corr:.4f}\n"
            
            self.analysis_results.setText(text)
            
            # Analyse climatique
            climate_result = self.controller.analyze_climate(season_type, year)
            if climate_result['success']:
                self.display_climate_analysis(climate_result['results'])
            
            self.btn_predict.setEnabled(True)
            self.status_label.setText("Analyse terminée")
            self.tabs.setCurrentIndex(1)  # Aller à l'onglet Analyse
        else:
            QMessageBox.critical(self, "Erreur", result['message'])
            self.status_label.setText("Erreur d'analyse")
    
    def run_prediction(self):
        """Lance la prédiction"""
        self.status_label.setText("Prédiction en cours...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
        year = self.combo_year.currentText()
        model_name = self.combo_model.currentText()
        
        result = self.controller.predict_flows(season_type, year, model_name)
        
        self.progress_bar.setVisible(False)
        
        if result['success']:
            metrics = result['metrics']
            
            text = f"""
╔══════════════════════════════════════════════════════════════╗
║           RÉSULTATS DE PRÉDICTION                            ║
╚══════════════════════════════════════════════════════════════╝

🤖 MODÈLE: {model_name}
📅 SAISON: {self.combo_season.currentText()} - {year}

📊 MÉTRIQUES DE PERFORMANCE (ENTRAÎNEMENT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RMSE:                 {metrics['train']['RMSE']:.4f}
MAE:                  {metrics['train']['MAE']:.4f}
R²:                   {metrics['train']['R2']:.4f}

📊 MÉTRIQUES DE PERFORMANCE (TEST)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RMSE:                 {metrics['test']['RMSE']:.4f}
MAE:                  {metrics['test']['MAE']:.4f}
R²:                   {metrics['test']['R2']:.4f}

✅ INTERPRÉTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
            r2 = metrics['test']['R2']
            if r2 > 0.9:
                text += "Excellent modèle (R² > 0.9)\n"
            elif r2 > 0.7:
                text += "Bon modèle (R² > 0.7)\n"
            elif r2 > 0.5:
                text += "Modèle acceptable (R² > 0.5)\n"
            else:
                text += "Modèle à améliorer (R² < 0.5)\n"
            
            text += f"\nErreur moyenne: {metrics['test']['MAE']:.2f} m³/s\n"
            
            # Feature importance si disponible
            if result['results']['feature_importance'] is not None:
                text += "\n🎯 IMPORTANCE DES VARIABLES (TOP 5)\n"
                text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                import pandas as pd
                fi_df = pd.DataFrame(result['results']['feature_importance'])
                for idx, row in fi_df.head(5).iterrows():
                    text += f"{row['feature']:20s}: {row['importance']:.4f}\n"
            
            self.prediction_results.setText(text)
            self.status_label.setText("Prédiction terminée")
            self.tabs.setCurrentIndex(2)  # Aller à l'onglet Prédiction
            
            QMessageBox.information(self, "Succès", "Prédiction terminée avec succès!")
        else:
            QMessageBox.critical(self, "Erreur", result['message'])
            self.status_label.setText("Erreur de prédiction")
    
    def export_season_data(self, season_type: str):
        """Exporte les données de saison"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer les données", "", "Excel Files (*.xlsx)"
        )
        if file_path:
            # Implémenter l'export
            QMessageBox.information(self, "Succès", "Données exportées!")
    
    def export_predictions(self):
        """Exporte les prédictions"""
        # Implémenter l'export des prédictions
        pass
    
    def export_report(self, format_type: str):
        """Exporte le rapport complet"""
        if format_type == 'excel':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le rapport", "", "Excel Files (*.xlsx)"
            )
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le rapport", "", "PDF Files (*.pdf)"
            )
        
        if file_path:
            # Implémenter l'export
            QMessageBox.information(self, "Succès", f"Rapport {format_type.upper()} généré!")

    
    def display_climate_analysis(self, climate_results: Dict):
        """Affiche les résultats de l'analyse climatique"""
        text = """
╔══════════════════════════════════════════════════════════════╗
║           ANALYSE CLIMATIQUE                                 ║
╚══════════════════════════════════════════════════════════════╝

"""
        
        # Corrélations
        if 'correlations' in climate_results and climate_results['correlations']:
            text += "🔗 CORRÉLATIONS DÉBITS-CLIMAT\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            
            for var, corr_data in climate_results['correlations'].items():
                pearson = corr_data['pearson']['correlation']
                p_value = corr_data['pearson']['p_value']
                
                # Interprétation
                if abs(pearson) > 0.7:
                    strength = "Forte"
                elif abs(pearson) > 0.4:
                    strength = "Modérée"
                else:
                    strength = "Faible"
                
                direction = "positive" if pearson > 0 else "négative"
                
                text += f"\n{var}:\n"
                text += f"  Corrélation Pearson: {pearson:.4f} ({strength} {direction})\n"
                text += f"  P-value: {p_value:.6f}\n"
        
        # Distribution des pluies
        if 'rainfall_distribution' in climate_results and climate_results['rainfall_distribution']:
            rd = climate_results['rainfall_distribution']
            text += "\n\n🌧️ DISTRIBUTION DES PLUIES\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            text += f"Moyenne:              {rd['moyenne']:.2f} mm\n"
            text += f"Médiane:              {rd['mediane']:.2f} mm\n"
            text += f"Total:                {rd['total']:.2f} mm\n"
            text += f"Jours de pluie:       {rd['jours_pluie']}\n"
            text += f"Jours sans pluie:     {rd['jours_sans_pluie']}\n"
        
        # Variables disponibles
        if 'variables_disponibles' in climate_results:
            text += "\n\n📋 VARIABLES DISPONIBLES\n"
            text += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            vars_disp = climate_results['variables_disponibles']
            text += f"Pluie:                {'✓' if vars_disp['pluie'] else '✗'}\n"
            text += f"ETP:                  {'✓' if vars_disp['etp'] else '✗'}\n"
            text += f"Température:          {'✓' if vars_disp['temperature'] else '✗'}\n"
        
        self.climate_results.setText(text)
    
    def export_season_data(self, season_type: str):
        """Exporte les données de saison"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer les données", 
            f"saison_{'seche' if season_type == 'dry' else 'pluies'}.xlsx",
            "Excel Files (*.xlsx)"
        )
        
        if file_path:
            success = self.controller.export_season_to_excel(season_type, file_path)
            if success:
                QMessageBox.information(self, "Succès", "Données exportées avec succès!")
            else:
                QMessageBox.critical(self, "Erreur", "Erreur lors de l'export")
    
    def export_predictions(self):
        """Exporte les prédictions"""
        if not self.current_year:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord effectuer une prédiction")
            return
        
        # Choix du format
        dialog = QDialog(self)
        dialog.setWindowTitle("Format d'export")
        layout = QVBoxLayout(dialog)
        
        radio_excel = QRadioButton("Excel (.xlsx)")
        radio_pdf = QRadioButton("PDF (.pdf)")
        radio_excel.setChecked(True)
        
        layout.addWidget(radio_excel)
        layout.addWidget(radio_pdf)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
            model_name = self.combo_model.currentText()
            
            if radio_excel.isChecked():
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Enregistrer les prédictions", 
                    f"predictions_{season_type}_{self.current_year}.xlsx",
                    "Excel Files (*.xlsx)"
                )
                
                if file_path:
                    result = self.controller.export_predictions_excel(
                        season_type, self.current_year, model_name, file_path
                    )
                    if result['success']:
                        QMessageBox.information(self, "Succès", f"Prédictions exportées:\n{result['filepath']}")
                    else:
                        QMessageBox.critical(self, "Erreur", result['message'])
            else:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Enregistrer le rapport", 
                    f"rapport_{season_type}_{self.current_year}.pdf",
                    "PDF Files (*.pdf)"
                )
                
                if file_path:
                    result = self.controller.export_complete_report_pdf(
                        season_type, self.current_year, model_name, file_path
                    )
                    if result['success']:
                        QMessageBox.information(self, "Succès", f"Rapport PDF généré:\n{result['filepath']}")
                    else:
                        QMessageBox.critical(self, "Erreur", result['message'])
    
    def export_report(self, format_type: str):
        """Exporte le rapport complet"""
        if not self.current_year:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord effectuer une analyse et prédiction")
            return
        
        season_type = 'dry' if self.combo_season.currentText() == "Saison Sèche" else 'rainy'
        model_name = self.combo_model.currentText()
        
        if format_type == 'excel':
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le rapport", 
                f"rapport_complet_{season_type}_{self.current_year}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                result = self.controller.export_predictions_excel(
                    season_type, self.current_year, model_name, file_path
                )
                if result['success']:
                    QMessageBox.information(self, "Succès", f"Rapport Excel généré:\n{result['filepath']}")
                else:
                    QMessageBox.critical(self, "Erreur", result['message'])
        else:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer le rapport", 
                f"rapport_complet_{season_type}_{self.current_year}.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                result = self.controller.export_complete_report_pdf(
                    season_type, self.current_year, model_name, file_path
                )
                if result['success']:
                    QMessageBox.information(self, "Succès", f"Rapport PDF généré:\n{result['filepath']}")
                else:
                    QMessageBox.critical(self, "Erreur", result['message'])

    
    def calculate_single_day_formula(self, season_type: str):
        """Calcule le débit pour un jour unique avec la formule"""
        try:
            is_dry = (season_type == 'dry')
            
            # Récupérer les paramètres selon la saison
            if is_dry:
                t = self.dry_day_spin.value()
                k_A = self.dry_ka_spin.value()
                epsilon = self.dry_epsilon_spin.value() / 100.0
                year = self.dry_year_spin.value()
                results_widget = self.dry_results
                season_name = "SAISON SÈCHE"
            else:
                t = self.rainy_day_spin.value()
                k_A = self.rainy_ka_spin.value()
                epsilon = self.rainy_epsilon_spin.value() / 100.0
                year = self.rainy_year_spin.value()
                results_widget = self.rainy_results
                season_name = "SAISON DES PLUIES"
            
            # Récupérer la dernière date du fichier uploadé
            start_date = None
            if self.data_file and self.current_data is not None:
                try:
                    # Trouver la colonne date
                    date_col = None
                    for col in self.current_data.columns:
                        if 'date' in col.lower():
                            date_col = col
                            break
                    
                    if date_col:
                        # Récupérer la dernière date
                        last_date = pd.to_datetime(self.current_data[date_col]).max()
                        # Ajouter 1 jour pour commencer après la dernière date
                        start_date = last_date + pd.Timedelta(days=1)
                        start_date = start_date.to_pydatetime()
                except Exception as e:
                    print(f"Impossible de récupérer la dernière date: {e}")
                    start_date = None
            
            # Obtenir le module de formule avec coefficients extraits (Task 14)
            if is_dry:
                formula_module = self.controller.get_formula_module_dry()
                from backend.formula import CalculatorModuleSeche
                calculator = CalculatorModuleSeche(formula_module=formula_module)
            else:
                formula_module = self.controller.get_formula_module_rainy()
                from backend.formula import CalculatorModule
                calculator = CalculatorModule(formula_module=formula_module)
            
            # Calculer avec start_date si disponible
            if start_date:
                result = calculator.calculate_single_day(t=t, k_A=k_A, epsilon=epsilon, start_date=start_date)
            else:
                result = calculator.calculate_single_day(t=t, k_A=k_A, epsilon=epsilon, year=year)
            
            # Obtenir la source des coefficients
            coeffs_info = self.controller.get_coefficients_info('dry' if is_dry else 'rainy')
            
            # Afficher les résultats
            text = calculator.format_results(result)
            
            # Ajouter des informations supplémentaires
            text += f"\n\n📋 PARAMÈTRES UTILISÉS\n"
            text += "=" * 60 + "\n"
            text += f"Saison:               {season_name}\n"
            text += f"Jour de saison:       {t}\n"
            text += f"Coefficient k(A):     {k_A:.4f}\n"
            text += f"Taux erreur ε:        {epsilon*100:.1f}%\n"
            text += f"Année:                {year}\n"
            text += f"\n🔧 SOURCE DES COEFFICIENTS\n"
            text += "=" * 60 + "\n"
            text += f"Source:               {coeffs_info['source']}\n"
            text += f"Q historique:         {coeffs_info['Q_historical']:.2f} m³/s\n"
            text += f"R²:                   {coeffs_info['r_squared']:.3f}\n"
            
            if 'warnings' in coeffs_info and coeffs_info['warnings']:
                text += f"\n⚠️ AVERTISSEMENTS\n"
                text += "=" * 60 + "\n"
                for warning in coeffs_info['warnings']:
                    text += f"- {warning}\n"
            
            results_widget.setText(text)
            self.status_label.setText(f"Calcul jour unique terminé ({season_name})")
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du calcul:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_full_season_formula(self, season_type: str):
        """Génère la table complète pour toute la saison"""
        try:
            is_dry = (season_type == 'dry')
            
            # Récupérer les paramètres selon la saison
            if is_dry:
                k_A = self.dry_ka_spin.value()
                epsilon = self.dry_epsilon_spin.value() / 100.0
                year = self.dry_year_spin.value()
                results_widget = self.dry_results
                season_name = "SAISON SÈCHE"
                duration = 212
            else:
                k_A = self.rainy_ka_spin.value()
                epsilon = self.rainy_epsilon_spin.value() / 100.0
                year = self.rainy_year_spin.value()
                results_widget = self.rainy_results
                season_name = "SAISON DES PLUIES"
                duration = 153
            
            self.status_label.setText(f"Génération en cours ({season_name})...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            # Récupérer la dernière date du fichier uploadé
            start_date = None
            if self.data_file and self.current_data is not None:
                try:
                    # Trouver la colonne date
                    date_col = None
                    for col in self.current_data.columns:
                        if 'date' in col.lower():
                            date_col = col
                            break
                    
                    if date_col:
                        # Récupérer la dernière date
                        last_date = pd.to_datetime(self.current_data[date_col]).max()
                        # Ajouter 1 jour pour commencer après la dernière date
                        start_date = last_date + pd.Timedelta(days=1)
                        start_date = start_date.to_pydatetime()
                except Exception as e:
                    print(f"Impossible de récupérer la dernière date: {e}")
                    start_date = None
            
            # Obtenir le module de formule avec coefficients extraits (Task 14)
            if is_dry:
                formula_module = self.controller.get_formula_module_dry()
                from backend.formula import GeneratorModuleSeche
                generator = GeneratorModuleSeche(formula_module=formula_module)
            else:
                formula_module = self.controller.get_formula_module_rainy()
                from backend.formula import GeneratorModule
                generator = GeneratorModule(formula_module=formula_module)
            
            # Générer la table complète avec start_date si disponible
            if is_dry:
                if start_date:
                    df = generator.generate_full_season(k_A=k_A, epsilon=epsilon, start_date=start_date)
                else:
                    df = generator.generate_full_season(k_A=k_A, epsilon=epsilon, year=year)
                stats = generator.get_statistics(k_A=k_A, epsilon=epsilon)
                self.dry_formula_df = df
            else:
                if start_date:
                    df = generator.generate_full_table(k_A=k_A, epsilon=epsilon, start_date=start_date)
                else:
                    df = generator.generate_full_table(k_A=k_A, epsilon=epsilon, year=year)
                stats = {
                    'Q_mean': df['Q centrale'].mean(),
                    'Q_min': df['Q centrale'].min(),
                    'Q_max': df['Q centrale'].max(),
                    'Q_std': df['Q centrale'].std(),
                    'duration_days': len(df)
                }
                self.rainy_formula_df = df
            
            self.progress_bar.setVisible(False)
            
            # Obtenir la source des coefficients
            coeffs_info = self.controller.get_coefficients_info('dry' if is_dry else 'rainy')
            
            # Afficher les résultats
            text = f"""
╔══════════════════════════════════════════════════════════════╗
║     TABLE JOURNALIÈRE COMPLÈTE - {season_name:^20s}     ║
╚══════════════════════════════════════════════════════════════╝

📊 STATISTIQUES GLOBALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Durée:                {stats['duration_days']} jours
Débit moyen:          {stats['Q_mean']:.2f} m³/s
Débit minimum:        {stats['Q_min']:.2f} m³/s
Débit maximum:        {stats['Q_max']:.2f} m³/s
Écart-type:           {stats['Q_std']:.2f} m³/s

📋 PARAMÈTRES UTILISÉS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coefficient k(A):     {k_A:.4f}
Taux erreur ε:        {epsilon*100:.1f}%
Année:                {year}

🔧 SOURCE DES COEFFICIENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Source:               {coeffs_info['source']}
Q historique:         {coeffs_info['Q_historical']:.2f} m³/s
R²:                   {coeffs_info['r_squared']:.3f}
"""
            
            if 'warnings' in coeffs_info and coeffs_info['warnings']:
                text += f"\n⚠️ AVERTISSEMENTS\n"
                text += "━" * 60 + "\n"
                for warning in coeffs_info['warnings']:
                    text += f"- {warning}\n"
            
            text += f"\n💾 Tableau complet généré ({duration} jours)\n"
            text += f"Utilisez 'Exporter vers Excel' pour sauvegarder les résultats.\n"
            
            text += f"\n📈 APERÇU DES DONNÉES (10 premiers jours)\n"
            text += "━" * 60 + "\n"
            
            # Afficher les 10 premiers jours
            for idx, row in df.head(10).iterrows():
                if is_dry:
                    text += f"Jour {row['t']:3d} ({row['Date']:10s}) - {row['Mois']:9s}: "
                    text += f"Q={row['Q_central']:7.2f} m³/s [{row['Q_min']:7.2f} - {row['Q_max']:7.2f}]\n"
                else:
                    text += f"Jour {row['t']:3d} - {row['Mois']:9s}: "
                    text += f"Q={row['Q centrale']:7.2f} m³/s [{row['Q min (-8%)']:7.2f} - {row['Q max (+19%)']:7.2f}]\n"
            
            text += f"\n... ({len(df)} jours au total)\n"
            text += "\n💾 Utilisez le bouton 'Exporter vers Excel' pour sauvegarder les résultats complets.\n"
            
            results_widget.setText(text)
            self.status_label.setText(f"Table complète générée ({len(df)} jours - {season_name})")
            
            QMessageBox.information(self, "Succès", 
                f"Table journalière complète générée avec succès!\n\n"
                f"Saison: {season_name}\n"
                f"Durée: {duration} jours\n"
                f"Q moyen: {stats['Q_mean']:.2f} m³/s")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "Erreur", f"Erreur lors de la génération:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def export_formula_results(self, season_type: str):
        """Exporte les résultats de formule vers Excel"""
        is_dry = (season_type == 'dry')
        
        # Récupérer le bon DataFrame
        if is_dry:
            df = self.dry_formula_df
            season_name = "seche"
            year = self.dry_year_spin.value()
            k_A = self.dry_ka_spin.value()
            epsilon = self.dry_epsilon_spin.value()
        else:
            df = self.rainy_formula_df
            season_name = "pluies"
            year = self.rainy_year_spin.value()
            k_A = self.rainy_ka_spin.value()
            epsilon = self.rainy_epsilon_spin.value()
        
        if df is None:
            QMessageBox.warning(self, "Attention", 
                "Veuillez d'abord générer une table complète avant d'exporter.")
            return
        
        try:
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Enregistrer les prédictions", 
                f"predictions_formule_{season_name}_{year}.xlsx",
                "Excel Files (*.xlsx)"
            )
            
            if file_path:
                # Exporter vers Excel
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Prédictions', index=False)
                    
                    # Ajouter une feuille avec les paramètres
                    params_df = pd.DataFrame({
                        'Paramètre': ['Saison', 'Année', 'Coefficient k(A)', 'Taux erreur ε (%)', 'Durée (jours)'],
                        'Valeur': [
                            f"Saison {'Sèche' if is_dry else 'Pluies'}",
                            year,
                            k_A,
                            epsilon,
                            len(df)
                        ]
                    })
                    params_df.to_excel(writer, sheet_name='Paramètres', index=False)
                
                QMessageBox.information(self, "Succès", 
                    f"Prédictions exportées avec succès!\n\nFichier: {file_path}")
                self.status_label.setText(f"Export réussi: {os.path.basename(file_path)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{str(e)}")
            import traceback
            traceback.print_exc()
