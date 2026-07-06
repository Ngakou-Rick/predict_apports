"""
Point d'entrée principal de l'application
Prévision Hydrologique - Barrage de Mbakaou
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class MenuPrincipal(QDialog):
    """Menu de sélection Phase 1 ou Phase 2"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prévision Hydrologique - Mbakaou")
        self.setGeometry(400, 300, 500, 300)
        self.choice = None
        self.init_ui()
    
    def init_ui(self):
        # Définir l'image de fond avec opacité
        self.set_background_image()
        
        layout = QVBoxLayout(self)
        
        # Titre
        title = QLabel("🌊 Système de Prévision Hydrologique\nBarrage de Mbakaou")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #1f4788; padding: 20px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Choisissez la phase à exécuter:")
        desc.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc)
        
        # Bouton Phase 1
        btn_phase1 = QPushButton("📂 PHASE 1: Transformation Saisonnière\n\n"
                                 "Convertir fichier brut en fichiers saisonniers")
        btn_phase1.setStyleSheet(self.get_button_style("#1f4788"))
        btn_phase1.clicked.connect(lambda: self.select_phase(1))
        layout.addWidget(btn_phase1)
        
        # Bouton Phase 2
        btn_phase2 = QPushButton("🎯 PHASE 2: Analyse et Prédiction\n\n"
                                 "Analyser et prédire l'année suivante")
        btn_phase2.setStyleSheet(self.get_button_style("#28a745"))
        btn_phase2.clicked.connect(lambda: self.select_phase(2))
        layout.addWidget(btn_phase2)
    
    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 20px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """
    
    def select_phase(self, phase):
        self.choice = phase
        self.accept()
    
    def set_background_image(self):
        """Définit l'image de fond avec opacité de 95%"""
        image_path = os.path.join('image', 'mbaka.png')
        if os.path.exists(image_path):
            palette = QPalette()
            pixmap = QPixmap(image_path)
            # Redimensionner l'image pour qu'elle s'adapte à la fenêtre
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            palette.setBrush(QPalette.Window, QBrush(scaled_pixmap))
            self.setPalette(palette)
            self.setAutoFillBackground(True)
            
            # Appliquer l'opacité de 95% à la fenêtre
            self.setWindowOpacity(0.95)


def main():
    """Fonction principale"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Afficher le menu
    menu = MenuPrincipal()
    if menu.exec_() == QDialog.Accepted:
        if menu.choice == 1:
            # Lancer Phase 1
            from phase1_transformation import TransformationWindow
            window = TransformationWindow()
            window.show()
            sys.exit(app.exec_())
        elif menu.choice == 2:
            # Lancer Phase 2
            from phase2_prediction import PredictionWindow
            window = PredictionWindow()
            window.show()
            sys.exit(app.exec_())


if __name__ == "__main__":
    main()
