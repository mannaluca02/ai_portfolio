#!/bin/bash
# Backend Start Script für Portfolio Chatbot

echo "=========================================="
echo "Portfolio Backend - Start Script"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Fehler: Virtual environment nicht gefunden!"
    echo "Bitte führe zuerst aus: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✓ Virtual environment gefunden"

# Activate virtual environment
echo "→ Aktiviere virtual environment..."
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warnung: .env Datei nicht gefunden!"
    echo "Erstelle .env aus .env.example..."
    cp .env.example .env
    echo "⚠️  Bitte konfiguriere die .env Datei mit deinen Credentials!"
    exit 1
fi

echo "✓ .env Datei gefunden"

# Check if port 8000 is already in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo ""
    echo "⚠️  Port 8000 ist bereits belegt!"
    echo ""
    read -p "Möchtest du den laufenden Prozess beenden? (j/n): " answer
    if [ "$answer" = "j" ] || [ "$answer" = "J" ]; then
        echo "→ Beende Prozess auf Port 8000..."
        lsof -ti:8000 | xargs kill -9
        sleep 2
        echo "✓ Prozess beendet"
    else
        echo "Abgebrochen."
        exit 1
    fi
fi

echo ""
echo "=========================================="
echo "→ Starte Backend Server..."
echo "=========================================="
echo ""
echo "API verfügbar unter:"
echo "  - http://localhost:8000"
echo "  - http://localhost:8000/docs (Dokumentation)"
echo "  - http://localhost:8000/api/health (Health Check)"
echo ""
echo "Zum Beenden: CTRL+C"
echo ""

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
