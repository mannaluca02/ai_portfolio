# AI Portfolio - Digitales Portfolio mit RAG-Chatbot

![Status](https://img.shields.io/badge/Status-Development-blue) ![Technology](https://img.shields.io/badge/Stack-Next.js%20%7C%20FastAPI%20%7C%20OpenAI-black)

Willkommen im Repository meines **KI-gestützten Portfolios**. 

Dieses Projekt ist mehr als nur eine Website – es ist eine Demonstration moderner Web- und KI-Technologien. Anstatt sich nur durch statische Seiten zu klicken, können Besucher über einen integrierten **RAG-Chatbot (Retrieval-Augmented Generation)** direkt Fragen zu meinem Werdegang, meinen Skills und Projekten stellen.

---

## 📖 Über das Projekt

In der modernen Softwareentwicklung reicht es oft nicht mehr, "nur" Code zu zeigen. Dieses Portfolio wurde entwickelt, um **AI Engineering** und **Full-Stack Development** in der Praxis zu demonstrieren.

**Das Kern-Feature:** Ein KI-Assistent, der nicht halluziniert. Er greift auf eine vektorisierte Datenbank meiner echten Lebenslauf-Daten zu, um präzise, verifizierte Antworten zu geben. Wenn ich keine Erfahrung in "Cobol" habe, wird der Bot das ehrlich sagen, anstatt etwas zu erfinden.

### ✨ Hauptfunktionen

- **💬 RAG-Chatbot**: Ein intelligenter Assistent, der Fragen beantwortet (z.B. _"Hat Luca Erfahrung mit React?"_).
- **🔍 Verifizierte Antworten**: Der Bot nutzt `gpt-3.5-turbo` in Kombination mit einer Vektordatenbank, um Antworten auf Basis tatsächlicher Fakten zu generieren.
- **📄 Deep-Linking**: Zitate im Chat führen direkt zur entsprechenden Stelle im Portfolio (z.B. zu einem spezifischen Zertifikat).
- **🎨 Modernes UI**: Entwickelt mit **Next.js 14**, **Tailwind CSS** und **Framer Motion** für flüssige Animationen.
- **🌗 Dark Mode**: Vollständige Unterstützung für Hell- und Dunkelmodus.
- **🛡️ Sicherheit**: Integriertes Rate-Limiting und Input-Validierung.

---

## 🛠 Technologie-Stack

Dieses Projekt folgt einer modernen **Microservices-Architektur**, getrennt in Frontend und Backend.

### Frontend (User Interface)
| Technologie | Zweck |
|-------------|-------|
| **Next.js 14** | React Framework für Server-Side Rendering & Routing |
| **TypeScript** | Typsicherheit und bessere Developer Experience |
| **Tailwind CSS** | Styling und Design System |
| **Framer Motion** | Komplexe Animationen und Transitions |

### Backend (AI Logic)
| Technologie | Zweck |
|-------------|-------|
| **FastAPI** | Hochperformantes Python Web-Framework |
| **LangChain / OpenAI** | LLM-Orchestrierung und Embeddings |
| **Supabase (PostgreSQL)** | Datenbank mit `pgvector` für Vektorsuche |
| **Sentence-Transformers** | Lokale Generierung von Embeddings (`BAAI/bge-m3`) |

---

## 🧠 Wie es funktioniert (RAG Pipeline)

Das Herzstück des Chatbots ist die **RAG-Architektur**. Hier ist, was im Hintergrund passiert, wenn du eine Frage stellst:

1.  **Ingestion (Vorab)**: Alle meine Portfolio-Daten (CV, Projekte, Texte) werden in kleine Stücke ("Chunks") zerlegt.
2.  **Embedding**: Ein KI-Modell (`BAAI/bge-m3`) wandelt diese Textstücke in mathematische Vektoren um. Diese werden in der **Supabase**-Datenbank gespeichert.
3.  **Retrieval (Zur Laufzeit)**:
    *   Deine Frage wird ebenfalls in einen Vektor umgewandelt.
    *   Die Datenbank sucht nach den Portfolio-Einträgen, die deiner Frage mathematisch am ähnlichsten sind (Semantische Suche).
4.  **Generation**:
    *   Die gefundenen Informationen werden zusammen mit deiner Frage an **ChatGPT (OpenAI)** gesendet.
    *   Das LLM formuliert eine natürliche Antwort, die <u>ausschließlich</u> auf den gefundenen Informationen basiert.

---

## 🚀 Installation & Setup

Möchtest du das Projekt lokal ausführen? Folge diesen Schritten.

### Voraussetzungen
*   Node.js 18+
*   Python 3.10+
*   Ein Supabase-Account (oder lokale PostgreSQL mit `pgvector`)
*   Ein OpenAI API Key

### 1. Repository klonen
```bash
git clone https://github.com/DEIN_USERNAME/ai_portfolio.git
cd ai_portfolio
```

### 2. Backend einrichten
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# Umgebungsvariablen setzen
cp .env.example .env
# -> Trage deinen OPENAI_API_KEY und DATABASE_URL in die .env Datei ein.

# Embeddings generieren (Initialisierung der DB)
python scripts/generate_embeddings.py

# Server starten
./start_local.sh
```

### 3. Frontend einrichten
```bash
cd ../frontend
npm install

# Entwicklungsserver starten
npm run dev
```

Die Anwendung läuft nun unter:
*   Frontend: [http://localhost:3000](http://localhost:3000)
*   Backend Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Projektstruktur

```
ai_portfolio/
├── backend/            # Python FastAPI Server
│   ├── app/
│   │   ├── services/   # RAG Logic (Retriever, Generator)
│   │   └── api/        # REST Endpoints
│   └── scripts/        # Datenbank-Tools
├── frontend/           # Next.js App
│   ├── app/            # Pages & Routes
│   └── components/     # React UI Components
│       └── chatbot/    # Chat-Widget Logik
└── database/           # SQL Migrationen
```

---

## 🛡️ Datenschutz

Da dieses Projekt persönliche Daten verarbeitet (CV), wurde großer Wert auf Datenschutz gelegt:
*   **Kein Tracking**: Es werden keine persönlichen Nutzerdaten gespeichert.
*   **Transparenz**: Der Chatbot erklärt, worauf seine Antworten basieren.

---

## 👤 Autor

**Luca Manna**  
Student @ FHNW | Data Science & Software Engineering  
[LinkedIn](https://www.linkedin.com/in/luca-manna-ch/) | [GitHub](https://github.com/mannaluca02)
