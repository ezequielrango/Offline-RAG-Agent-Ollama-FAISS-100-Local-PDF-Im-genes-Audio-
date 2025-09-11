#!/usr/bin/env bash
set -e

echo "[entrypoint] Esperando Ollama en: ${OLLAMA_BASE_URL:-http://host.docker.internal:11434}"
for i in {1..60}; do
  if curl -sf "${OLLAMA_BASE_URL:-http://host.docker.internal:11434}/api/tags" >/dev/null; then
    echo "[entrypoint] Ollama OK."
    break
  fi
  echo "[entrypoint] Ollama no responde aún, reintentando..."
  sleep 2
done

python - <<'PY'
from app.db import init_db
init_db()
print("[entrypoint] DB init OK.")
PY

# Lanzar API FastAPI (8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Lanzar UI Gradio (7860)
python -m app.ui &
UI_PID=$!

wait -n $API_PID $UI_PID
