# BHARATGURU — Adaptive Multilingual AI Learning System
# Single-container image: FastAPI + Hybrid RAG + CPU avatar/video pipeline.

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/.hf_cache \
    PORT=8000

# System libs: ffmpeg (video compositing), libsndfile1 (soundfile/librosa),
# libgl1 + libglib2.0-0 (opencv-python).
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg libsndfile1 libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Pre-cache the sentence-transformers embedding model so the running container
# stays fully offline (config.py forces HF_HUB_OFFLINE=1 at import time).
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 8000

# server.py reads $PORT / $HOST.
CMD ["python", "server.py"]
