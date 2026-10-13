"""FastAPI Server for BHARATGURU — The Adaptive Multilingual AI Learning System.

Connects the Bharat Modern web interface to:
- Student Knowledge Graph & Dependency Modeler
- Misconception Engine & Cognitive Fingerprinter
- Adaptive Pedagogy Policy Selector & Socratic Engine
- Bharat Context Engine
- Hallucination Shield & Citation Grounding Verifier
- Learning DNA Profiler
- Spaced Repetition Review Queue
- Institutional Teacher Dashboard
- 12 Indian Languages Audio & Video Synthesizer

Run with:
    python server.py
"""
from __future__ import annotations

import json
import shutil
import tempfile
import threading
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import Cookie, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from src.assessment import build_report, format_report, generate_quiz, grade_answer
from src.auth import get_auth_store
from src.firebase_backend import get_firebase_backend
from src.ingestion import extract_doc_metadata, ingest_many
from src.knowledge_graph import KnowledgeGraphStore
from src.learning_dna import compute_learning_dna
from src.lesson_planner import LearnerInstruction, LessonPlan, make_lesson_plan, parse_instruction
from src.misconception_engine import fingerprint_misconception
from src.pedagogy import socratic_dialogue_turn
from src.pipeline import LessonContext, build_lesson, render_segment_media
from src.model_3d import generate_custom_3d_concept, get_3d_model
from src.profile_store import ProfileStore
from src.retrieval import build_retriever
from src.spaced_repetition import get_spaced_repetition_queue
from src.teacher_dashboard import (
    get_class_overview,
    get_student_pedagogical_guidance,
    get_students_roster,
)
from src.teaching import State, TeachingSession
from src.tts import synthesize

app = FastAPI(title="BHARATGURU AI Learning System API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active in-memory session caches
_SESSIONS: dict[str, dict[str, Any]] = {}


class PlanRequest(BaseModel):
    topic: str = ""
    instruction: str = "I am a beginner, teach me in 20 minutes, in English, with simple examples"
    upload_paths: list[str] = []
    language: str = "English"
    preset_style: str = ""
    mode: str = "DIRECT"
    exam_board: str = ""
    student: str = "student1"
    production_tier: str = "express"  # "express" (1 credit) or "realistic" (5 credits)


class StartSessionRequest(BaseModel):
    session_id: str
    language: str | None = None


class ExplainRequest(BaseModel):
    session_id: str
    segment_index: int
    render_video: bool = True
    production_tier: str | None = "express"


class AnswerRequest(BaseModel):
    session_id: str
    segment_index: int
    answer: str
    is_followup: bool = False
    student: str = "student1"


class StudentAskRequest(BaseModel):
    session_id: str
    segment_index: int
    question: str


class AdaptRequest(BaseModel):
    session_id: str
    segment_index: int
    render_video: bool = False


class LanguageRequest(BaseModel):
    session_id: str
    language: str


class SessionAdvanceRequest(BaseModel):
    session_id: str


class SocraticRequest(BaseModel):
    session_id: str
    concept: str
    student_input: str
    history: list[dict[str, str]] = []


class QuizGenerateRequest(BaseModel):
    session_id: str


class QuizSubmitRequest(BaseModel):
    session_id: str
    student: str = "student1"
    answers: dict[str, str] = {}


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""
    role: str = "student"
    grade_or_board: str = "CBSE Class 10"
    preferred_language: str = "English"


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class DemoLoginRequest(BaseModel):
    role: str = "student"


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    grade_or_board: str | None = None
    preferred_language: str | None = None
    avatar_url: str | None = None


class FirebaseLoginRequest(BaseModel):
    id_token: str
    role: str = "student"
    grade_or_board: str = "CBSE Class 10"
    preferred_language: str = "English"


class FirestoreSyncRequest(BaseModel):
    collection: str = "students"
    student: str
    data: dict[str, Any] = {}


def _extract_token(
    authorization: str | None = None,
    x_auth_token: str | None = None,
    cookie_token: str | None = None,
) -> str:
    if authorization:
        parts = authorization.strip().split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            return parts[1]
        return authorization.strip()
    if x_auth_token:
        return x_auth_token.strip()
    if cookie_token:
        return cookie_token.strip()
    return ""


def _require_user(
    authorization: str | None,
    x_auth_token: str | None,
    bg_session: str | None,
) -> dict[str, Any]:
    """Resolve the signed-in user from the Bearer header, X-Auth-Token, or session
    cookie — raising 401 if none is present or the session has expired."""
    token = _extract_token(authorization, x_auth_token, bg_session)
    if not token:
        raise HTTPException(status_code=401, detail="Please sign in to continue.")
    user = get_auth_store().get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Your session has expired. Please sign in again.")
    return user


def _require_teacher(
    authorization: str | None,
    x_auth_token: str | None,
    bg_session: str | None,
) -> dict[str, Any]:
    user = _require_user(authorization, x_auth_token, bg_session)
    if user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Access restricted: Teacher privileges required.")
    return user


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=token,
        max_age=config.SESSION_TTL_DAYS * 86400,
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        path="/",
    )


# --------------------------------------------------------------------------- #
# Metadata & Directory Endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/health")
def health():
    """Liveness probe for containers / load balancers."""
    return {"status": "ok", "sessions_active": len(_SESSIONS)}


# --------------------------------------------------------------------------- #
# Free Backend Status & Authentication Endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/backend/status")
def get_backend_status():
    """Report status of free local engine, zero-cost LLM fallback, and storage."""
    active_llm = (
        "Offline Pedagogical Rule-Based Engine (100% Free / $0)"
        if config.LLM_MOCK
        else (
            f"Google Gemini ({config.GEMINI_MODEL}) [Free Tier]"
            if config.GEMINI_API_KEY
            else (
                f"Groq LPU ({config.GROQ_MODEL}) [Free Tier]"
                if config.GROQ_API_KEY
                else "Offline Pedagogical Fallback Engine (100% Free / $0)"
            )
        )
    )

    return {
        "status": "active",
        "free_tier": True,
        "database": "SQLite (Zero-cost, embedded local persistence)",
        "tts_engine": "Microsoft Edge Neural TTS / gTTS (100% Free / $0)",
        "embeddings_engine": f"Local MiniLM ({config.EMBED_MODEL}) (0 API Cost)",
        "active_llm": active_llm,
        "supported_free_modes": [
            {
                "name": "Offline Pedagogical Fallback",
                "cost": "100% Free ($0)",
                "status": "Ready",
                "description": "Deterministic pedagogical reasoning engine for core STEM topics with zero API keys required.",
            },
            {
                "name": "Google AI Studio (Gemini Flash)",
                "cost": "Free Tier",
                "status": "Configured" if bool(config.GEMINI_API_KEY) else "Key Required (Free at aistudio.google.com)",
                "description": "Fast multilingual multimodal reasoning via free Google AI Studio developer tier.",
            },
            {
                "name": "Groq LPU Cloud",
                "cost": "Free Tier",
                "status": "Configured" if bool(config.GROQ_API_KEY) else "Key Required (Free at console.groq.com)",
                "description": "Sub-second Llama-3.3-70B LPU inference via free Groq API key.",
            },
            {
                "name": "Local Ollama / Open-Source LLMs",
                "cost": "100% Free ($0)",
                "status": "Supported",
                "description": "Run open weights (Llama 3, Qwen 2.5, Mistral) locally on your own machine.",
            },
        ],
    }


@app.post("/api/auth/register")
def register_user(req: RegisterRequest, response: Response):
    """Register a new student or educator account."""
    store = get_auth_store()
    try:
        user = store.register_user(
            username=req.username,
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            role=req.role,
            grade_or_board=req.grade_or_board,
            preferred_language=req.preferred_language,
        )
        token = store.create_session(user["id"])
        _set_session_cookie(response, token)
        return {
            "success": True,
            "token": token,
            "user": user,
            "message": f"Welcome to BHARATGURU, {user['full_name']}!",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
def login_user(req: LoginRequest, response: Response):
    """Authenticate with username/email and password."""
    store = get_auth_store()
    user = store.authenticate_user(req.username_or_email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")

    token = store.create_session(user["id"])
    _set_session_cookie(response, token)
    return {
        "success": True,
        "token": token,
        "user": user,
        "message": f"Welcome back, {user['full_name']}!",
    }


@app.post("/api/auth/demo-login")
def demo_login(req: DemoLoginRequest, response: Response):
    """1-Click instant login as Demo Student ('aarav') or Demo Teacher ('priya')."""
    store = get_auth_store()
    target_username = "priya" if req.role.lower() == "teacher" else "aarav"
    user = store.get_user_by_username(target_username)
    if not user:
        # Fallback to student1 if somehow missing
        user = store.get_user_by_username("student1")
    if not user:
        raise HTTPException(status_code=500, detail="Demo account could not be initialized.")

    token = store.create_session(user["id"])
    _set_session_cookie(response, token)
    return {
        "success": True,
        "token": token,
        "user": user,
        "message": f"Logged in as Demo {user['role'].capitalize()} ({user['full_name']})",
    }


@app.get("/api/auth/me")
def get_current_user_profile(
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Validate bearer token and return current user profile."""
    user = _require_user(authorization, x_auth_token, bg_session)
    return {"success": True, "user": user}


@app.post("/api/auth/logout")
def logout_user(
    response: Response,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Invalidate current session token."""
    token = _extract_token(authorization, x_auth_token, bg_session)
    if token:
        store = get_auth_store()
        store.invalidate_session(token)
    response.delete_cookie(config.SESSION_COOKIE_NAME, path="/")
    return {"success": True, "message": "Logged out successfully."}


@app.put("/api/auth/profile")
def update_user_profile(
    req: ProfileUpdateRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Update profile preferences for logged-in user."""
    user = _require_user(authorization, x_auth_token, bg_session)
    store = get_auth_store()
    updates = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = store.update_profile(user["id"], updates)
    return {"success": True, "user": updated_user, "message": "Profile updated successfully."}


# --------------------------------------------------------------------------- #
# Firebase Cloud Backend Endpoints
# --------------------------------------------------------------------------- #
@app.get("/api/firebase/config")
def get_firebase_config_endpoint():
    """Retrieve public Firebase Web Client configuration."""
    fb = get_firebase_backend()
    return fb.get_public_config()


@app.get("/api/firebase/status")
def get_firebase_status_endpoint():
    """Report connectivity status of Firebase Admin SDK & Cloud Firestore."""
    fb = get_firebase_backend()
    return fb.get_status()


@app.post("/api/auth/firebase-login")
def firebase_login_endpoint(req: FirebaseLoginRequest, response: Response):
    """Authenticate or auto-provision user using Firebase ID Token (Google Sign-In)."""
    import re
    import secrets

    fb = get_firebase_backend()
    try:
        decoded = fb.verify_firebase_id_token(req.id_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    store = get_auth_store()
    email = decoded.get("email") or f"{decoded['uid']}@bharatguru.firebase.io"
    user = store.get_user_by_email(email)

    if not user:
        # Auto-provision user account from Firebase profile
        raw_name = decoded.get("name") or email.split("@")[0]
        username_seed = raw_name.lower().replace(" ", "_")
        username_clean = re.sub(r"[^a-z0-9_]", "", username_seed)[:20] or f"fb_{decoded['uid'][:8]}"

        # Guarantee unique username
        base_username = username_clean
        counter = 1
        while store.get_user_by_username(username_clean):
            username_clean = f"{base_username}_{counter}"
            counter += 1

        rand_pwd = secrets.token_urlsafe(16)
        user = store.register_user(
            username=username_clean,
            email=email,
            password=rand_pwd,
            full_name=raw_name,
            role=req.role,
            grade_or_board=req.grade_or_board,
            preferred_language=req.preferred_language,
            avatar_url=decoded.get("picture") or ("👩‍🏫" if req.role == "teacher" else "👨‍🎓"),
        )
    else:
        if decoded.get("picture") and not user.get("avatar_url"):
            store.update_profile(user["id"], {"avatar_url": decoded["picture"]})
            user["avatar_url"] = decoded["picture"]

    token = store.create_session(user["id"])
    _set_session_cookie(response, token)

    # Sync user record to Cloud Firestore (best-effort)
    fb.sync_to_firestore("users", user["id"], {
        "username": user["username"],
        "email": user["email"],
        "full_name": user["full_name"],
        "role": user["role"],
        "grade_or_board": user["grade_or_board"],
        "preferred_language": user["preferred_language"],
        "provider": decoded.get("provider", "firebase"),
    })

    return {
        "success": True,
        "token": token,
        "user": user,
        "message": f"Welcome, {user['full_name']}! Authenticated via Firebase Google Sign-In.",
    }


@app.post("/api/firebase/sync")
def sync_to_firestore_endpoint(
    req: FirestoreSyncRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Sync student progress or knowledge graph to Google Cloud Firestore."""
    _require_user(authorization, x_auth_token, bg_session)
    fb = get_firebase_backend()
    success = fb.sync_to_firestore(req.collection, req.student, req.data)
    return {
        "success": success,
        "status": "synced" if success else "firestore_offline_or_not_configured",
    }


@app.get("/api/languages")
def list_languages():
    return config.LANGUAGES


@app.get("/api/presets")
def list_presets():
    return {
        "presets": config.TEACH_ME_PRESETS,
        "modes": config.TEACHING_MODES,
        "exam_boards": config.EXAM_BOARDS,
    }


@app.get("/api/sample-files")
def list_sample_files():
    sample_files = []
    if config.SAMPLE_DIR.exists():
        for f in config.SAMPLE_DIR.iterdir():
            if f.is_file() and not f.name.startswith("."):
                sample_files.append({
                    "name": f.name,
                    "path": str(f.resolve()),
                    "size_bytes": f.stat().st_size,
                })
    return sample_files


@app.post("/api/upload")
async def upload_document(
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Upload PDF, DOCX, PPTX, TXT into a per-session directory."""
    _require_user(authorization, x_auth_token, bg_session)
    filename = file.filename or "uploaded_doc.txt"
    suffix = Path(filename).suffix.lower()

    if suffix not in (".pdf", ".docx", ".pptx", ".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {suffix}. Supported: PDF, DOCX, PPTX, TXT, MD.",
        )

    upload_dir = config.WORKDIR / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / f"{uuid.uuid4().hex[:8]}_{filename}"

    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Immediately inspect & validate document for rich client feedback
    meta = extract_doc_metadata(target_path)

    return {
        "filename": filename,
        "file_path": str(target_path.resolve()),
        "size_bytes": target_path.stat().st_size,
        "page_count": meta.get("page_count", 0),
        "word_count": meta.get("word_count", 0),
        "chunk_count": meta.get("chunk_count", 0),
        "suggested_topic": meta.get("suggested_topic", ""),
        "preview_snippet": meta.get("preview_snippet", ""),
        "is_valid": meta.get("is_valid", True),
        "error": meta.get("error"),
    }


# --------------------------------------------------------------------------- #
# Lesson Creation & Pedagogical Planning
# --------------------------------------------------------------------------- #
@app.post("/api/plan")
def build_lesson_plan(
    req: PlanRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    try:
        instruction = req.instruction
        if req.preset_style and req.preset_style in config.TEACH_ME_PRESETS:
            preset_desc = config.TEACH_ME_PRESETS[req.preset_style]["style"]
            instruction = f"{instruction}. Style: {preset_desc}."

        parsed = parse_instruction(instruction)
        if req.language and req.language in config.LANGUAGES:
            parsed.language = req.language

        ctx = build_lesson(
            topic=req.topic,
            instruction=parsed,
            upload_paths=req.upload_paths,
            student=req.student,
        )

        session = TeachingSession(
            plan=ctx.plan,
            retriever=ctx.retriever,
            language=parsed.language,
            preset_style=req.preset_style,
            mode=req.mode,
        )

        session_id = uuid.uuid4().hex[:10]
        _SESSIONS[session_id] = {
            "ctx": ctx,
            "session": session,
            "student": req.student,
            "quiz": None,
            "media_cache": {},
            "preset_style": req.preset_style,
            "mode": req.mode,
            "production_tier": req.production_tier,
        }

        # Initialize knowledge graph nodes for this plan
        kg_store = KnowledgeGraphStore()
        kg_graph = kg_store.get_student_graph(req.student)
        kg_store.close()

        plan_dict = asdict(ctx.plan)
        return {
            "session_id": session_id,
            "title": ctx.plan.title,
            "language": ctx.plan.language,
            "level": ctx.plan.level,
            "grounded": ctx.plan.grounded,
            "segments": plan_dict["segments"],
            "instruction": asdict(parsed),
            "mode": req.mode,
            "production_tier": req.production_tier,
            "credits_cost": 5 if req.production_tier == "realistic" else 1,
            "knowledge_graph": kg_graph,
        }
    except Exception as exc:
        print(f"[API ERROR] build_lesson_plan failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to build plan: {str(exc)}")


# --------------------------------------------------------------------------- #
# Teaching Loop & State Execution
# --------------------------------------------------------------------------- #
@app.post("/api/session/explain")
def explain_segment(
    req: ExplainRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ctx: LessonContext = data["ctx"]
    idx = req.segment_index

    if idx < 0 or idx >= len(ses.plan.segments):
        raise HTTPException(status_code=400, detail="Invalid segment index")

    ses.idx = idx
    ses.state = State.EXPLAIN

    tier = req.production_tier or data.get("production_tier", "express")
    data["production_tier"] = tier

    explanation = ses.explain()
    question = ses.question()
    run = ses.current_run

    video_url = None
    audio_url = None
    video_status = "none"

    # Scoped per session (so different lessons never share a cached file) and
    # per tier (so upgrading a segment from Express to Realistic Studio mid-
    # lesson renders a fresh, actually-higher-quality clip instead of just
    # re-serving the cached Express one back).
    web_media_dir = config.WORKDIR / "web_media" / req.session_id / tier
    web_media_dir.mkdir(parents=True, exist_ok=True)
    audio_file = web_media_dir / f"seg{idx}_{ses.language}.mp3"
    video_file = web_media_dir / f"seg{idx}_{ses.language}.mp4"

    # 1. Fast Neural Audio Synthesis (takes ~1s)
    try:
        if not audio_file.exists() or audio_file.stat().st_size < 1000:
            synthesize(explanation, ses.language, web_media_dir / f"seg{idx}_{ses.language}")
        audio_url = f"/output/web_media/{req.session_id}/{tier}/seg{idx}_{ses.language}.mp3"
    except Exception as a_err:
        print(f"[API] Audio synth notice: {a_err}")
        audio_url = None

    # 2. Video compositing: instant if cached, else async background render
    if req.render_video:
        if video_file.exists() and video_file.stat().st_size > 5000:
            video_url = f"/output/web_media/{req.session_id}/{tier}/seg{idx}_{ses.language}.mp4"
            video_status = "ready"
        else:
            video_status = "rendering"

            def _bg_render():
                try:
                    render_segment_media(
                        ctx, idx, explanation, ses.language,
                        workdir=web_media_dir,
                        production_tier=tier,
                    )
                except Exception as b_err:
                    print(f"[BG Video] Render error: {b_err}")

            threading.Thread(target=_bg_render, daemon=True).start()

    seg = ses.plan.segments[idx]

    return {
        "segment_index": idx,
        "concept": seg.concept,
        "explanation": explanation,
        "question": question,
        "source_label": seg.source_label,
        "source_quote": seg.source_quote,
        "video_url": video_url,
        "video_status": video_status,
        "audio_url": audio_url,
        "language": ses.language,
        "state": ses.state.value,
        "score_summary": ses.score_summary(),
        "production_tier": tier,
        "is_realistic_studio": (tier == "realistic"),
        "grounding_shield": run.grounding if run else None,
        "log": [asdict(t) if hasattr(t, "__dataclass_fields__") else t for t in ses.log_rows()[-3:]],
    }


@app.get("/api/session/video-status/{session_id}/{segment_index}")
def get_video_status(
    session_id: str,
    segment_index: int,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    ses = data["session"]
    tier = data.get("production_tier", "express")
    web_media_dir = config.WORKDIR / "web_media" / session_id / tier
    video_file = web_media_dir / f"seg{segment_index}_{ses.language}.mp4"
    if video_file.exists() and video_file.stat().st_size > 5000:
        return {"status": "ready", "video_url": f"/output/web_media/{session_id}/{tier}/{video_file.name}"}
    return {"status": "rendering"}


@app.post("/api/session/ask")
def ask_student_question(
    req: StudentAskRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Answer a student-initiated doubt/follow-up question while preserving session state."""
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    ses: TeachingSession = data["session"]

    # Generate grounded clarification
    result = ses.answer_student_question(req.question)

    # Synthesize neural audio response for immediate playback
    web_media_dir = config.WORKDIR / "web_media" / req.session_id
    web_media_dir.mkdir(parents=True, exist_ok=True)
    audio_hash = uuid.uuid4().hex[:8]
    audio_file = web_media_dir / f"doubt_{req.segment_index}_{audio_hash}_{ses.language}.mp3"
    audio_url = None

    try:
        synthesize(result["answer"], ses.language, audio_file)
        if audio_file.exists() and audio_file.stat().st_size > 500:
            audio_url = f"/output/web_media/{req.session_id}/{audio_file.name}"
    except Exception as err:
        print(f"[API] Student question audio synth notice: {err}")

    result["audio_url"] = audio_url
    return result


@app.post("/api/session/answer")
def evaluate_answer(
    req: AnswerRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    eval_res = ses.evaluate(req.answer, followup=req.is_followup)

    student = req.student or data.get("student", "student1")
    seg = ses.current_segment
    c_name = seg.concept if seg else "General Concept"

    # Update Knowledge Graph Store dynamically
    kg_store = KnowledgeGraphStore()
    kg_node_update = kg_store.record_attempt(
        student,
        c_name,
        is_correct=(eval_res.get("verdict") == "correct"),
        misconception=eval_res.get("misconception"),
        language=ses.language,
    )
    kg_store.close()

    return {
        "verdict": eval_res.get("verdict", "partial"),
        "misconception": eval_res.get("misconception"),
        "fingerprint": eval_res.get("fingerprint"),
        "feedback": eval_res.get("feedback", ""),
        "state": ses.state.value,
        "kg_update": kg_node_update,
    }


@app.post("/api/session/adapt")
def adapt_explanation(
    req: AdaptRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ctx: LessonContext = data["ctx"]
    idx = req.segment_index

    adapt_res = ses.adapt()
    run = ses.current_run

    video_url = None
    if req.render_video and run and run.reexplanation:
        try:
            tier = data.get("production_tier", "express")
            # Own subfolder (not just session-scoped): a re-teach of segment N
            # must not overwrite the original explain video for segment N,
            # which shares the same "seg{idx}_{language}" filename pattern.
            media = render_segment_media(
                ctx, idx, run.reexplanation, ses.language,
                workdir=config.WORKDIR / "web_media" / req.session_id / "adapt" / tier,
                production_tier=tier,
            )
            v_path = Path(media["video"]).resolve()
            try:
                v_rel = v_path.relative_to(config.ROOT).as_posix()
                video_url = f"/{v_rel}"
            except Exception:
                video_url = f"/output/web_media/{v_path.name}"
        except Exception as exc:
            print(f"[API] Adapt video render error: {exc}")

    return {
        "action": adapt_res.get("action"),
        "strategy": adapt_res.get("strategy", "analogy"),
        "reexplanation": run.reexplanation if run else "",
        "followup_question": run.followup_question if run else "",
        "fingerprint": run.fingerprint if run else None,
        "video_url": video_url,
        "state": ses.state.value,
    }


@app.post("/api/session/advance")
def advance_segment(
    req: SessionAdvanceRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    has_next = ses.advance()

    return {
        "has_next": has_next,
        "next_segment_index": ses.idx if has_next else -1,
        "state": ses.state.value,
        "score_summary": ses.score_summary(),
    }


@app.get("/api/session/complete/{session_id}")
def get_session_completion(
    session_id: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve consolidated completion statistics, certificate data, and recommendations."""
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ctx: LessonContext = data["ctx"]
    student = data.get("student", "student1")

    # Concepts covered
    segments_out = []
    for i, s in enumerate(ctx.plan.segments):
        segments_out.append({
            "segment_index": i,
            "concept": s.concept,
            "example": s.example,
            "source_label": s.source_label,
            "checkpoint_question": s.checkpoint_question,
        })

    summary = ses.score_summary()
    total_segments = len(ctx.plan.segments)
    completed_segments = total_segments if (ses.finished or ses.idx >= total_segments) else min(ses.idx + 1, total_segments)

    # Persist in ProfileStore so completed lesson is registered in student history
    store = ProfileStore(config.DB_PATH)
    next_topic = None
    try:
        store.record_session(
            student,
            ctx.plan.title,
            language=ses.language,
            level=ctx.plan.level,
            score=float(summary.get("correct", total_segments)),
            out_of=float(total_segments),
            strong=[s["concept"] for s in segments_out],
            weak=summary.get("weak", []),
        )
        next_topic = store.recommend_next_topic(student, ctx.plan.title)
    except Exception as e:
        print(f"[API] ProfileStore completion notice: {e}")
        next_topic = {"next_topic": "Advanced Applications of " + ctx.plan.title, "reason": "Next sequential milestone in syllabus"}
    finally:
        store.close()

    # Knowledge Graph stats
    kg_store = KnowledgeGraphStore()
    kg_data = kg_store.get_student_graph(student)
    kg_store.close()

    return {
        "session_id": session_id,
        "title": ctx.plan.title,
        "language": ses.language,
        "level": ctx.plan.level,
        "student": student,
        "total_segments": total_segments,
        "completed_segments": completed_segments,
        "segments": segments_out,
        "score_summary": summary,
        "mastery_percentage": kg_data.get("overall_mastery", 88.0),
        "next_topic": next_topic,
        "grounded": ctx.plan.grounded,
    }


@app.post("/api/session/language")
def switch_session_language(
    req: LanguageRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ses.set_language(req.language)

    return {
        "language": ses.language,
        "segment_index": ses.idx,
        "state": ses.state.value,
        "score_summary": ses.score_summary(),
    }


@app.post("/api/session/socratic")
def handle_socratic_turn(
    req: SocraticRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    reply_data = socratic_dialogue_turn(
        concept=req.concept,
        dialogue_history=req.history,
        student_latest_input=req.student_input,
    )
    return reply_data


# --------------------------------------------------------------------------- #
# Assessment, Quiz & Report
# --------------------------------------------------------------------------- #
@app.post("/api/quiz/generate")
def get_or_generate_quiz(
    req: QuizGenerateRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ctx: LessonContext = data["ctx"]

    if data.get("quiz") is None:
        taught_concepts = [r.concept for r in ses.runs] or [s.concept for s in ctx.plan.segments]
        questions = generate_quiz(ctx.plan, taught_concepts)
        data["quiz"] = questions

    out_q = []
    for q in data["quiz"]:
        out_q.append({
            "concept": q.concept,
            "type": q.type,
            "question": q.question,
            "options": q.options,
        })

    return {
        "topic": ctx.plan.title,
        "questions": out_q,
    }


@app.post("/api/quiz/submit")
def submit_quiz_answers(
    req: QuizSubmitRequest,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    ses: TeachingSession = data["session"]
    ctx: LessonContext = data["ctx"]
    quiz_questions = data.get("quiz")

    if not quiz_questions:
        taught = [r.concept for r in ses.runs] or [s.concept for s in ctx.plan.segments]
        quiz_questions = generate_quiz(ctx.plan, taught)
        data["quiz"] = quiz_questions

    graded = []
    kg_store = KnowledgeGraphStore()
    for i, q in enumerate(quiz_questions):
        ans = req.answers.get(str(i), "")
        res = grade_answer(q, ans)
        graded.append(res)
        # Update knowledge graph with quiz performance
        kg_store.record_attempt(
            req.student,
            q.concept,
            is_correct=(res.score >= 0.7),
            language=ses.language,
        )
    kg_store.close()

    summary = ses.score_summary()
    report = build_report(ctx.plan, graded, session_weak=summary["weak"])

    # Persist in SQLite
    store = ProfileStore(config.DB_PATH)
    store.record_session(
        req.student,
        ctx.plan.title,
        language=ses.language,
        level=ctx.plan.level,
        score=report["raw_score"],
        out_of=report["out_of"],
        strong=report["strong_areas"],
        weak=report["needs_improvement"],
    )
    next_topic = store.recommend_next_topic(req.student, ctx.plan.title)
    prof = store.profile(req.student)
    store.close()

    results_out = []
    for r in graded:
        results_out.append({
            "concept": r.question.concept,
            "question": r.question.question,
            "type": r.question.type,
            "student_answer": r.student_answer,
            "verdict": r.verdict,
            "score": r.score,
            "feedback": r.feedback,
        })

    return {
        "report": report,
        "report_formatted": format_report(report),
        "results": results_out,
        "next_topic": next_topic,
        "student_profile": prof,
        "transition_logs": ses.log_rows(),
    }


# --------------------------------------------------------------------------- #
# Intelligence Layer Endpoints (Knowledge Graph, DNA, Spaced Repetition)
# --------------------------------------------------------------------------- #
@app.get("/api/knowledge-graph/{student}")
def get_student_knowledge_graph(
    student: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve full concept knowledge graph with masteries and links."""
    _require_user(authorization, x_auth_token, bg_session)
    store = KnowledgeGraphStore()
    graph = store.get_student_graph(student)
    store.close()
    return graph


@app.get("/api/student/dna/{student}")
def get_student_learning_dna(
    student: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve the student's empirical Learning DNA interaction profile."""
    _require_user(authorization, x_auth_token, bg_session)
    dna = compute_learning_dna(student)
    return dna.to_dict()


@app.get("/api/spaced-repetition/{student}")
def get_student_spaced_repetition(
    student: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve upcoming and overdue Ebbinghaus review cards."""
    _require_user(authorization, x_auth_token, bg_session)
    return get_spaced_repetition_queue(student)


@app.get("/api/teacher/class-overview")
def get_teacher_class_analytics(
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve institutional class overview, cohort misconceptions, and remediations."""
    _require_teacher(authorization, x_auth_token, bg_session)
    return get_class_overview()


@app.get("/api/teacher/students-roster")
def get_teacher_students_roster(
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve enrolled student roster with mastery stats for teacher inspection."""
    _require_teacher(authorization, x_auth_token, bg_session)
    return {"students": get_students_roster()}


@app.get("/api/teacher/student-guidance/{student}")
def get_student_guidance_endpoint(
    student: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve personalized 'How to Teach This Student' pedagogical blueprint."""
    _require_teacher(authorization, x_auth_token, bg_session)
    return get_student_pedagogical_guidance(student)


@app.get("/api/profile/{student}")
def get_student_profile(
    student: str,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Retrieve historical session records."""
    _require_user(authorization, x_auth_token, bg_session)
    store = ProfileStore(config.DB_PATH)
    prof = store.profile(student)
    recent = store.history(student, limit=10)
    store.close()

    total_sessions = prof.get("sessions", 0)
    topics = prof.get("topics_studied", [])
    weak = prof.get("recurring_weak", [])

    # Real average score across the student's graded sessions.
    scored = [
        (r["score"], r["out_of"])
        for r in recent
        if r.get("out_of")
    ]
    avg_score_pct = (
        round(100 * sum(s for s, _ in scored) / sum(o for _, o in scored))
        if scored else 0
    )

    # Real mastered-concept count from the knowledge graph (mastery >= 80%).
    kg_store = KnowledgeGraphStore()
    kg_graph = kg_store.get_student_graph(student)
    kg_store.close()
    concepts_mastered = sum(1 for n in kg_graph["nodes"] if n["mastery"] >= 80.0)

    return {
        "student": student,
        "total_sessions": total_sessions,
        "estimated_hours": round(total_sessions * 0.33, 1) if total_sessions else 0.0,
        "concepts_mastered": concepts_mastered,
        "avg_score_pct": avg_score_pct,
        "topics_studied": topics,
        "recurring_weak": weak,
        "recent_sessions": recent,
    }


# --------------------------------------------------------------------------- #
# Bharat 3D Lab Endpoints (Interactive Three.js Science Models)
# --------------------------------------------------------------------------- #
@app.get("/api/3d/model")
def get_3d_model_spec(concept: str = "dna"):
    """Retrieve 3D interactive WebGL specification for a concept (DNA, Bohr Atom, Electric Motor, Solar)."""
    spec = get_3d_model(concept)
    return spec.to_dict()


class Model3DQuery(BaseModel):
    query: str


@app.post("/api/3d/generate")
def generate_3d_model_endpoint(
    req: Model3DQuery,
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Dynamically construct an interactive 3D model specification from natural language query."""
    _require_user(authorization, x_auth_token, bg_session)
    return generate_custom_3d_concept(req.query)


# --------------------------------------------------------------------------- #
# Student Revision Notes Export
# --------------------------------------------------------------------------- #
def _build_session_notes_md(data: dict[str, Any]) -> str:
    ses: TeachingSession = data["session"]
    plan = ses.plan
    summary = ses.score_summary()
    lines = [
        f"# {plan.title} — Revision Notes",
        "",
        f"_Language: {ses.language} · Checkpoints correct: "
        f"{summary.get('correct', 0)}/{summary.get('total', 0)}_",
        "",
    ]

    runs_by_idx = {r.index: r for r in ses.runs}
    for i, seg in enumerate(plan.segments):
        lines.append(f"## {i + 1}. {seg.concept}")
        run = runs_by_idx.get(i)
        body = (run.explanation if run and run.explanation else
                getattr(seg, "example", "") or "")
        if body:
            lines += ["", body.strip(), ""]
        if run and run.reexplanation:
            lines += [f"**Explained another way:** {run.reexplanation.strip()}", ""]
        q = (run.question if run and run.question else
             getattr(seg, "checkpoint_question", "") or "")
        if q:
            lines.append(f"**Checkpoint:** {q}")
        if run and run.student_answer:
            lines.append(
                f"Your answer: _{run.student_answer.strip()}_ — **{run.verdict or 'unrated'}**"
            )
        if run and run.misconception:
            lines.append(f"⚠️ Watch out: {run.misconception.strip()}")
        src_label = getattr(seg, "source_label", "") or ""
        src_quote = getattr(seg, "source_quote", "") or ""
        if src_label or src_quote:
            lines.append("")
            lines.append(f"> Source: {src_label}" + (f' — "{src_quote.strip()}"' if src_quote else ""))
        lines.append("")

    weak = summary.get("weak") or []
    if weak:
        lines += ["---", "", "### Concepts to revise again", ""]
        lines += [f"- {w}" for w in weak]
        lines.append("")

    return "\n".join(lines)


@app.get("/api/session/{session_id}/notes")
def export_session_notes(
    session_id: str,
    format: str = "md",
    authorization: str | None = Header(None),
    x_auth_token: str | None = Header(None),
    bg_session: str | None = Cookie(None),
):
    """Download a plain-language revision sheet for everything taught this session."""
    _require_user(authorization, x_auth_token, bg_session)
    data = _SESSIONS.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")

    md = _build_session_notes_md(data)
    title = data["session"].plan.title
    safe = "".join(c if c.isalnum() or c in "-_ " else "" for c in title).strip().replace(" ", "_")[:60] or "lesson"

    if format == "html":
        body = md.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        html = (
            "<!doctype html><meta charset='utf-8'>"
            f"<title>{safe} notes</title>"
            "<style>body{font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;"
            "max-width:720px;margin:2rem auto;padding:0 1rem;color:#0b1c30}"
            "h1{font-size:1.6rem}h2{margin-top:1.8rem;color:#002045}"
            "blockquote{border-left:3px solid #fe9832;margin:.5rem 0;padding:.2rem .9rem;color:#43474e}"
            "@media print{body{margin:0}}</style>"
            f"<pre style='white-space:pre-wrap;font:inherit'>{body}</pre>"
        )
        return HTMLResponse(html)

    return Response(
        content=md,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{safe}_notes.md"'},
    )


# --------------------------------------------------------------------------- #
# Static file mounts
# --------------------------------------------------------------------------- #
app.mount("/output", StaticFiles(directory=str(config.WORKDIR)), name="output")
app.mount("/assets", StaticFiles(directory=str(config.ASSETS_DIR)), name="assets")

# Mount frontend static files
STATIC_DIR = config.ROOT / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/login")
@app.get("/login.html")
def serve_login_page():
    """Serve dedicated Bharat Modern Login & Registration Page."""
    login_file = STATIC_DIR / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    return HTMLResponse("<h1>Login page under construction</h1>", status_code=404)


def _serve_gated_app(request: Request):
    """Serve the main SPA only to a signed-in session; otherwise bounce to login.

    Sessions are recognized via the httpOnly `bg_session` cookie set at
    login/register/demo-login, so this check happens before any HTML or app
    JS reaches the browser — visiting `/` directly with no session redirects
    straight to `/login.html` instead of ever rendering the classroom.
    """
    token = request.cookies.get(config.SESSION_COOKIE_NAME, "")
    user = get_auth_store().get_user_by_token(token) if token else None
    if not user:
        return RedirectResponse(url="/login.html", status_code=303)
    index_file = STATIC_DIR / "index.html"
    return FileResponse(str(index_file))


@app.get("/", include_in_schema=False)
def serve_root(request: Request):
    return _serve_gated_app(request)


@app.get("/index.html", include_in_schema=False)
def serve_index_html(request: Request):
    return _serve_gated_app(request)


app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


def main():
    import os

    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    host = os.environ.get("HOST", "0.0.0.0")
    print("\n" + "=" * 60)
    print("Starting BHARATGURU AI Learning System Server")
    print(f"Open in browser: http://localhost:{port}")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    main()
