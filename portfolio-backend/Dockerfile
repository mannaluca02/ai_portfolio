# syntax=docker/dockerfile:1
FROM python:3.11-slim

# ====== ENVIRONMENT ======
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# ====== SYSTEM DEPENDENCIES ======
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
 && rm -rf /var/lib/apt/lists/*

# ====== WORKDIR ======
WORKDIR /app

# ====== COPY REQUIREMENTS ======
COPY requirements.txt .

# Torch & ML libs → CPU-only Wheels (kleiner!)
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# ====== COPY APPLICATION CODE ======
COPY . .

# ====== EXPOSE PORT ======
# Railway setzt automatisch $PORT, aber wir deklarieren ihn zur Doku
EXPOSE 8000

# ====== START COMMAND ======
# - Lädt Modell asynchron im Hintergrund (blockiert nicht den Start)
# - Nutzt $PORT von Railway (Fallback 8000)
CMD bash -lc '\
  : ${BGE_MODEL_PATH:=./app/ml_models/bge-m3}; \
  if [ ! -d "$BGE_MODEL_PATH" ] || [ -z "$(ls -A "$BGE_MODEL_PATH" 2>/dev/null)" ]; then \
    echo "[startup] Model missing → downloading in background to $BGE_MODEL_PATH"; \
    python scripts/download_model.py & \
  else \
    echo "[startup] Model present at $BGE_MODEL_PATH"; \
  fi; \
  : ${PORT:=8000}; \
  echo "[startup] Starting uvicorn on 0.0.0.0:$PORT"; \
  uvicorn app.main:app --host 0.0.0.0 --port $PORT'