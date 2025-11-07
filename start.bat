@echo off
REM Script de démarrage rapide pour Windows
REM Usage: start.bat

echo 🏦 Application Bancaire - Démarrage
echo ======================================
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Erreur: Python n'est pas installé
    echo Installez Python depuis https://www.python.org
    pause
    exit /b 1
)

echo ✅ Python détecté
echo.

REM Installer les dépendances si nécessaire
if not exist "backend\__pycache__" (
    echo 📦 Installation des dépendances...
    cd backend
    pip install -r requirements.txt
    cd ..
)

REM Vérifier le fichier .env
if not exist "backend\.env" (
    echo ⚠️  Fichier .env manquant
    echo Copie de .env.example vers .env...
    copy backend\.env.example backend\.env
    echo ✅ Fichier .env créé
)

echo.
echo 🚀 Démarrage du serveur Flask...
echo.
echo API disponible sur: http://localhost:5000
echo Frontend disponible sur: http://localhost:8888/banking-app/frontend/login.html
echo.
echo Compte de test:
echo   Email: jean.dupont@example.com
echo   Mot de passe: TestPassword123!
echo.
echo Appuyez sur Ctrl+C pour arrêter le serveur
echo.

cd backend
python app.py
