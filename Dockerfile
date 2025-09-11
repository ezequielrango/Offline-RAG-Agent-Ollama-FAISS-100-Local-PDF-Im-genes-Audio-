FROM python:3.11-slim

# Dependencias del sistema: OCR (tesseract + idiomas), ffmpeg para Whisper, curl para healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends \
      tesseract-ocr tesseract-ocr-spa tesseract-ocr-por \
      ffmpeg git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Reqs de Python
COPY app/requirements.txt /app/app/requirements.txt
RUN pip install --no-cache-dir -r /app/app/requirements.txt

# Copiamos código (también montamos en volumen, pero así sirve para build limpio)
COPY app /app/app
COPY scripts /app/scripts

# Carpetas persistentes
RUN mkdir -p /app/data/pdfs /app/data/images /app/data/audio /app/indexes /app/storage /app/hf-cache

EXPOSE 8000
EXPOSE 7860
