"""
PHASE 1: Transformation du fichier brut en fichiers saisonniers
Application simple pour séparer les données en saisons
"""
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
import sys
import os

from backend.data_processing.seasonal_transformer import SeasonalTransformer


class TransformationWindow(QMainWindow):
    """Fenêtre de transformation Phase 1"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Phase 1 - Transformation Saisonnière")
        self.setGeometry(200, 200, 800, 500)
        
        self.transformer = SeasonalTransformer()
        self.data_loaded = False
        
        self.init_ui()
    
    def init_ui(self):
        """Initialise l'interface"""
        # Définir l'image de fond avec opacité
        self.set_background_image()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Titre
        title = QLabel("🔄 Transformation en Années Hydrologiques Saisonnières")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1f4788; padding: 20px;")
        layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            "1. Chargez votre fichier de données brut\n"
            "2. Exportez la saison sèche (1er déc → 30 juin)\n"
            "3. Exportez la saison des pluies (1er juillet → 30 nov)"
        )
        instructions.setStyleSheet("padding: 10px; font-size: 12px;")
        layout.addWidget(instructions)
        
        # Bouton charger
        self.btn_load = QPushButton("📁 Charger Fichier Brut")
        self.btn_load.setStyleSheet(self.get_button_style("#1f4788"))
        self.btn_load.clicked.connect(self.load_file)
        layout.addWidget(self.btn_load)
        
        # Zone d'information
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("background-color: #f0f0f0; padding: 10px;")
        layout.addWidget(self.info_text)
        
        # Boutons d'export
        self.btn_export_dry = QPushButton("💾 Exporter Saison Sèche")
        self.btn_export_dry.setStyleSheet(self.get_button_style("#28a745"))
        self.btn_export_dry.setEnabled(False)
        self.btn_export_dry.clicked.connect(lambda: self.export_season('dry'))
        layout.addWidget(self.btn_export_dry)
        
        self.btn_export_rainy = QPushButton("💾 Exporter Saison des Pluies")
        self.btn_export_rainy.setStyleSheet(self.get_button_style("#007bff"))
        self.btn_export_rainy.setEnabled(False)
        self.btn_export_rainy.clicked.connect(lambda: self.export_season('rainy'))
        layout.addWidget(self.btn_export_rainy)
        
        # Statut
        self.status_label = QLabel("En attente du fichier...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Bouton de navigation vers Phase 2
        self.btn_goto_phase2 = QPushButton("➡️ Aller à Phase 2 (Analyse & Prédiction)")
        self.btn_goto_phase2.setStyleSheet(self.get_button_style("#ff6b6b"))
        self.btn_goto_phase2.clicked.connect(self.goto_phase2)
        layout.addWidget(self.btn_goto_phase2)
    
    def get_button_style(self, color):
        """Style des boutons"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
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
    
    def load_file(self):
        """Charge le fichier brut"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner le fichier de données brut", "", "Excel Files (*.xlsx *.xls)"
        )
        
        if file_path:
            try:
                # Charger et transformer
                df = self.transformer.load_data(file_path)
                dry, rainy = self.transformer.split_by_season(df)
                
                # Afficher les informations
                info = f"""
Fichier chargé: {os.path.basename(file_path)}
Total observations: {len(df)}

SAISON SÈCHE (1er déc → 30 juin):
  - Observations: {len(dry)}
  - Années: {', '.join(str(y) for y in self.transformer.get_season_years('dry'))}

SAISON DES PLUIES (1er juillet → 30 nov):
  - Observations: {len(rainy)}
  - Années: {', '.join(str(y) for y in self.transformer.get_season_years('rainy'))}
                """
                self.info_text.setText(info)
                
                # Activer les boutons d'export
                self.btn_export_dry.setEnabled(True)
                self.btn_export_rainy.setEnabled(True)
                self.data_loaded = True
                
                self.status_label.setText("✅ Données chargées - Prêt pour l'export")
                QMessageBox.information(self, "Succès", "Données transformées avec succès!")
                
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors du chargement:\n{str(e)}")
                self.status_label.setText("❌ Erreur de chargement")
    
    def export_season(self, season_type):
        """Exporte une saison"""
        if not self.data_loaded:
            QMessageBox.warning(self, "Attention", "Veuillez d'abord charger un fichier")
            return
        
        season_name = "saison_seche" if season_type == 'dry' else "saison_pluies"
        default_name = f"{season_name}.xlsx"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Enregistrer {season_name}", default_name, "Excel Files (*.xlsx)"
        )
        
        if file_path:
            try:
                success = self.transformer.export_season_data(season_type, file_path)
                if success:
                    QMessageBox.information(
                        self, "Succès", 
                        f"Fichier exporté:\n{file_path}\n\n"
                        f"Vous pouvez maintenant utiliser ce fichier dans la Phase 2 (Analyse & Prédiction)"
                    )
                    self.status_label.setText(f"✅ {season_name}.xlsx exporté")
                else:
                    QMessageBox.critical(self, "Erreur", "Erreur lors de l'export")
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Erreur lors de l'export:\n{str(e)}")
    
    def goto_phase2(self):
        """Passe à la Phase 2"""
        from phase2_prediction import PredictionWindow
        self.phase2_window = PredictionWindow()
        self.phase2_window.show()
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
    """Fonction principale Phase 1"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TransformationWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
