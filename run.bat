@echo off
echo ========================================
echo   Prevision Hydrologique Mbakaou
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo ERREUR: Python n'est pas installe ou n'est pas dans le PATH
    echo Telechargez Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python detecte!
echo.

REM Verifier si les dependances sont installees
echo Verification des dependances...
python -c "import pandas, numpy, sklearn, PyQt5" >nul 2>&1
if errorlevel 1 (
    echo Installation des dependances...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERREUR: Impossible d'installer les dependances
        pause
        exit /b 1
    )
)

echo Dependances OK!
echo.

REM Lancer l'application
echo Lancement de l'application...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ERREUR lors de l'execution
    pause
)
