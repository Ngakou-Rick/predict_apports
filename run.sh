#!/bin/bash

echo "========================================"
echo "  Prévision Hydrologique Mbakaou"
echo "========================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "ERREUR: Python 3 n'est pas installé"
    echo "Installez Python 3 depuis https://www.python.org/downloads/"
    exit 1
fi

echo "Python détecté!"
echo ""

# Vérifier si les dépendances sont installées
echo "Vérification des dépendances..."
python3 -c "import pandas, numpy, sklearn, PyQt5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "ERREUR: Impossible d'installer les dépendances"
        exit 1
    fi
fi

echo "Dépendances OK!"
echo ""

# Lancer l'application
echo "Lancement de l'application..."
echo ""
python3 main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERREUR lors de l'exécution"
    read -p "Appuyez sur Entrée pour continuer..."
fi
