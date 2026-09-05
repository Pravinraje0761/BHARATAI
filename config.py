"""Central configuration + tiny .env loader (no python-dotenv dependency)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# HuggingFace models are pre-cached; skip the network metadata check that can
# fail with "client has been closed" on a Streamlit rerun.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key, val = key.strip(), val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


def reload_env() -> None:
    """Reload environment variables from .env and update module-level configuration variables."""
    dotenv_path = ROOT / ".env"
    if dotenv_path.exists():
        for raw in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip('"').strip("'")
            os.environ[key] = val

    global GROQ_API_KEY, GROQ_BASE_URL, GROQ_MODEL
    global NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL
    global GEMINI_API_KEY, GEMINI_MODEL, LLM_MOCK
    global FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_PROJECT_ID
    global FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID, FIREBASE_APP_ID
    global FIREBASE_MEASUREMENT_ID, FIREBASE_SERVICE_ACCOUNT, FIREBASE_DATABASE_URL

    GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
    GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")
    NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
    LLM_MOCK = os.environ.get("LLM_MOCK", "0") == "1"

    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "")
    FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "")
    FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID", "")
    FIREBASE_SERVICE_ACCOUNT = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
    FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "")


_load_dotenv(ROOT / ".env")
reload_env()

# --- Groq LPU (Sub-Second Lightning Inference) ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_BASE_URL = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.environ.get("GROQ_MODEL", "qwen/qwen3.8-27b")

# --- NVIDIA NIM (High-Performance GPU Inference) ---
NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.environ.get("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.environ.get("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct")

# --- Gemini ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-flash-latest")
LLM_MOCK = os.environ.get("LLM_MOCK", "0") == "1"

# --- Firebase Cloud Backend ---
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "")
FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "")
FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "")
FIREBASE_MESSAGING_SENDER_ID = os.environ.get("FIREBASE_MESSAGING_SENDER_ID", "")
FIREBASE_APP_ID = os.environ.get("FIREBASE_APP_ID", "")
FIREBASE_MEASUREMENT_ID = os.environ.get("FIREBASE_MEASUREMENT_ID", "")
FIREBASE_SERVICE_ACCOUNT = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "")
FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "")

# --- Auth session cookie ---
# Set COOKIE_SECURE=1 once the site is deployed behind HTTPS (browsers drop
# Secure cookies over plain HTTP, so this stays off by default for local dev).
COOKIE_SECURE = os.environ.get("COOKIE_SECURE", "0") == "1"
SESSION_COOKIE_NAME = "bg_session"
SESSION_TTL_DAYS = 30

# --- Embeddings ---
EMBED_MODEL = os.environ.get("EMBED_MODEL", "all-MiniLM-L6-v2")

# --- Chunking ---
CHUNK_MIN_WORDS = 220
CHUNK_MAX_WORDS = 480

# --- Paths ---
WORKDIR = Path(os.environ.get("AITEACHER_WORKDIR", ROOT / "output"))
ASSETS_DIR = ROOT / "assets"
AVATAR_DIR = ASSETS_DIR / "avatar"
SAMPLE_DIR = ROOT / "sample_data"
DB_PATH = WORKDIR / "profiles.sqlite3"

# --- Video ---
VIDEO_FPS = 12
VIDEO_W = 1280
VIDEO_H = 720

# --- Languages exposed in the UI (12 Indian Languages) ---
LANGUAGES = {
    "English": {"code": "en", "voice": "en-IN-NeerjaNeural", "native": "English (India)"},
    "Hindi": {"code": "hi", "voice": "hi-IN-SwaraNeural", "native": "हिन्दी"},
    "Hinglish": {"code": "hi", "voice": "hi-IN-SwaraNeural", "native": "Hinglish"},
    "Tamil": {"code": "ta", "voice": "ta-IN-PallaviNeural", "native": "தமிழ்"},
    "Telugu": {"code": "te", "voice": "te-IN-ShrutiNeural", "native": "తెలుగు"},
    "Kannada": {"code": "kn", "voice": "kn-IN-SapnaNeural", "native": "ಕನ್ನಡ"},
    "Malayalam": {"code": "ml", "voice": "ml-IN-SobhanaNeural", "native": "മലയാളം"},
    "Bengali": {"code": "bn", "voice": "bn-IN-TanishaaNeural", "native": "বাংলা"},
    "Marathi": {"code": "mr", "voice": "mr-IN-AarohiNeural", "native": "मराठी"},
    "Gujarati": {"code": "gu", "voice": "gu-IN-DhwaniNeural", "native": "ગુજરાતી"},
    "Punjabi": {"code": "pa", "voice": "pa-IN-GurpreetNeural", "native": "ਪੰਜਾਬੀ"},
    "Urdu": {"code": "ur", "voice": "ur-IN-GulNeural", "native": "اردو"},
}

# --- Teach Me Like... Presets ---
TEACH_ME_PRESETS = {
    "ten_year_old": {"label": "Like I'm 10", "style": "kid-friendly simple analogies, playful examples, no jargon"},
    "cricket": {"label": "Using Cricket", "style": "cricket scenarios (bowling speed, bat impact, fielding, pitch conditions)"},
    "professor": {"label": "Like My Professor", "style": "academic rigor, derivations, formal definitions and boundary conditions"},
    "bilingual_tamil": {"label": "Tanglish (Tamil + English)", "style": "conversational Tamil with scientific technical terms in clear English"},
    "five_min": {"label": "5-Minute Blitz", "style": "rapid high-impact overview, core intuition and formula punchline"},
    "socratic": {"label": "Socratic Guide", "style": "guiding exploratory questions that make the student deduce the law themselves"},
}

# --- Teaching Modes ---
TEACHING_MODES = ["DIRECT", "SOCRATIC", "EXAM", "REVISION", "BEGINNER", "DEEP DIVE"]

# --- Exam Syllabi ---
EXAM_BOARDS = ["CBSE Class 10/12", "ICSE / ISC", "JEE Main & Advanced", "NEET-UG", "State Board", "Custom Syllabus"]

# --- Duration templates: minutes -> (segment count, depth label) ---
DURATION_TEMPLATES = {
    5: {"segments": 3, "depth": "quick overview, one example per concept"},
    20: {"segments": 5, "depth": "solid understanding, worked example + check per concept"},
    60: {"segments": 9, "depth": "deep mastery, multiple examples, edge cases, practice"},
}

for _p in (WORKDIR, ASSETS_DIR, AVATAR_DIR, SAMPLE_DIR):
    _p.mkdir(parents=True, exist_ok=True)
