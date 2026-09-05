# Deploying BHARATGURU

The app is a single FastAPI process that serves the web UI, the REST API, and
the generated media from one origin. No external database or services.

## 1. Local (no container)

```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # fill in at least one LLM key
python server.py            # http://localhost:8000
```

## 2. Docker

```bash
cp .env.example .env        # fill in keys
docker compose up --build   # http://localhost:8000
```

or without compose:

```bash
docker build -t bharatguru .
docker run --rm -p 8000:8000 --env-file .env -v bharatguru_output:/app/output bharatguru
```

The image bundles `ffmpeg` and pre-caches the MiniLM embedding model at build
time, so the container runs the RAG engine fully offline.

## 3. Any PaaS (Render / Railway / Fly / Cloud Run / HF Spaces Docker)

- Build context: repo root, `Dockerfile` as-is.
- The server binds `$PORT` (falls back to 8000) and `$HOST` (falls back to
  `0.0.0.0`); most hosts inject `PORT` automatically.
- Health check path: `GET /api/health` -> `{"status":"ok"}`.
- Set the LLM keys from `.env.example` as service environment variables.
- Mount a persistent volume at `/app/output` if you want the SQLite profile
  store and rendered media to survive restarts.

## Notes

- `edge-tts` and `gTTS` reach Microsoft / Google at runtime for neural voices;
  outbound HTTPS must be allowed. Text/quiz still work if TTS is blocked.
- With no LLM key set the app still boots but only the offline mock topics
  (Newton / photosynthesis / electricity) produce meaningful lessons.
- Sessions are in-memory; run a single replica or add sticky sessions.

## Auth gate (required for production)

`/` and `/index.html` now require a signed-in session — anonymous visitors are
redirected to `/login.html`, and every content API (`/api/plan`,
`/api/session/*`, `/api/quiz/*`, `/api/upload`, `/api/3d/generate`, teacher
endpoints) rejects requests with no valid session (401/403). The session is
an httpOnly cookie (`bg_session`) set at login/register/demo-login.

- **Set `COOKIE_SECURE=1`** once you're serving over HTTPS (the default host
  for Render/Railway/Fly/Cloud Run/HF Spaces). Left at `0` (default), the
  cookie is dropped by browsers over plain HTTP, which is what you want for
  local `http://localhost` development — but the browser will also silently
  drop it over HTTPS if you forget to flip this to `1`, breaking login.
- The seeded demo accounts (`aarav` / `student123`, `priya` / `teacher123`)
  are convenient for a live demo but are printed in `src/auth.py`'s
  docstring — change or remove them before a public production launch if you
  don't want strangers logging in as your demo accounts.
- CORS currently allows `*` with credentials, which browsers only honor for
  same-origin requests anyway (this app serves frontend + API from one
  origin). If you ever split the frontend onto a different domain, replace
  `allow_origins=["*"]` in `server.py` with your actual frontend origin.
