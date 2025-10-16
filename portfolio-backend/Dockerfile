# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# (optional) system deps, falls du numpy/pandas/uvicorn wheels bauen musst
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 1) Abhaengigkeiten zuerst (bessere Layer-Caches)
COPY requirements.txt .

# CPU-only Torch ist deutlich schlanker; Option A oder B benutzen:
# A) falls du requirements.txt bereits auf CPU-Index umgestellt hast:
# RUN pip install --no-cache-dir -r requirements.txt
# B) ansonsten so installieren (zieht torch CPU Wheels trotzdem):
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

# 2) Code kopieren (nur Backend-Verzeichnis)
COPY . .

# 3) Modell NICHT im Build einbacken
#    Beim Start wird es nur geladen, wenn es fehlt (download-if-missing)
CMD bash -lc 'if [ -z "$BGE_MODEL_PATH" ]; then export BGE_MODEL_PATH=./app/ml_models/bge-m3; fi; \
  if [ ! -d "$BGE_MODEL_PATH" ] || [ -z "$(ls -A "$BGE_MODEL_PATH" 2>/dev/null)" ]; then \
    echo "Downloading BGE model to $BGE_MODEL_PATH"; python scripts/download_model.py; \
  else echo "Model present at $BGE_MODEL_PATH"; fi; \
  uvicorn app.main:app --host 0.0.0.0 --port 8000'