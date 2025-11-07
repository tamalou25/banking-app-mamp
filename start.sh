#!/bin/bash

# Script de démarrage rapide pour l'application bancaire
# Usage: ./start.sh

echo "🏦 Application Bancaire - Démarrage"
echo "======================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Erreur: Python 3 n'est pas installé"
    echo "Installez Python 3 depuis https://www.python.org"
    exit 1
fi

echo "✅ Python 3 détecté: $(python3 --version)"

# Vérifier si les dépendances sont installées
if [ ! -d "backend/__pycache__" ]; then
    echo "📦 Installation des dépendances..."
    cd backend
    pip3 install -r requirements.txt
    cd ..
fi

# Vérifier si le fichier .env existe
if [ ! -f "backend/.env" ]; then
    echo "⚠️  Fichier .env manquant"
    echo "Copie de .env.example vers .env..."
    cp backend/.env.example backend/.env
    echo "✅ Fichier .env créé"
    echo "⚠️  N'oubliez pas de modifier les clés secrètes en production !"
fi

echo ""
echo "🚀 Démarrage du serveur Flask..."
echo ""
echo "API disponible sur: http://localhost:5000"
echo "Frontend disponible sur: http://localhost:8888/banking-app/frontend/login.html"
echo ""
echo "Compte de test:"
echo "  Email: jean.dupont@example.com"
echo "  Mot de passe: TestPassword123!"
echo ""
echo "Appuyez sur Ctrl+C pour arrêter le serveur"
echo ""

cd backend
python3 app.py
