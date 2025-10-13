# Backend Starten - Ultra-Kurzanleitung

## Schnellstart

```bash
cd portfolio-backend
./start.sh
```

Fertig! Der Server läuft jetzt auf `http://localhost:8000`

---

## Alternative (Manuell)

```bash
cd portfolio-backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## Wichtige URLs

- **API**: http://localhost:8000
- **Dokumentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health
- **Chatbot**: http://localhost:8000/api/chat

---

## Server stoppen

Drücke `CTRL+C` im Terminal

---

## Probleme?

### Port bereits belegt
```bash
lsof -ti:8000 | xargs kill -9
```

### Virtual Environment fehlt
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### .env Datei fehlt
```bash
cp .env.example .env
# Dann .env bearbeiten und Credentials eintragen
```

### Alte Rate-Limit-Fehler
```bash
./migrate_env.sh
```

---

## Vollständige Dokumentation

Siehe `README.md` für die vollständige Dokumentation.
