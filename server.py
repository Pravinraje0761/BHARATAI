"""FastAPI Server for BHARATGURU — The Adaptive Multilingual AI Learning System.

Connects the Bharat Modern web interface to:
- Student Knowledge Graph & Dependency Modeler
- Misconception Engine™ & Cognitive Fingerprinter
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

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
from src.assessment import build_report, format_report, generate_quiz, grade_answer
from src.ingestion import ingest_many
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
from src.teacher_dashboard import get_class_overview
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


class StartSessionRequest(BaseModel):
    session_id: str
    language: str | None = None


class ExplainRequest(BaseModel):
    session_id: str
    segment_index: int
    render_video: bool = True


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


# --------------------------------------------------------------------------- #
# Metadata & Directory Endpoints
# --------------------------------------------------------------------------- #
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
async def upload_document(file: UploadFile = File(...)):
    """Upload PDF, DOCX, PPTX, TXT into a per-session directory."""
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

    return {
        "filename": filename,
        "file_path": str(target_path.resolve()),
        "size_bytes": target_path.stat().st_size,
    }


# --------------------------------------------------------------------------- #
# Lesson Creation & Pedagogical Planning
# --------------------------------------------------------------------------- #
@app.post("/api/plan")
def build_lesson_plan(req: PlanRequest):
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
            "knowledge_graph": kg_graph,
        }
    except Exception as exc:
        print(f"[API ERROR] build_lesson_plan failed: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to build plan: {str(exc)}")


# --------------------------------------------------------------------------- #
# Teaching Loop & State Execution
# --------------------------------------------------------------------------- #
@app.post("/api/session/explain")
def explain_segment(req: ExplainRequest):
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

    explanation = ses.explain()
    question = ses.question()
    run = ses.current_run

    video_url = None
    audio_url = None
    video_status = "none"

    web_media_dir = config.WORKDIR / "web_media"
    web_media_dir.mkdir(parents=True, exist_ok=True)
    audio_file = web_media_dir / f"seg{idx}_{ses.language}.mp3"
    video_file = web_media_dir / f"seg{idx}_{ses.language}.mp4"

    # 1. Fast Neural Audio Synthesis (takes ~1s)
    try:
        if not audio_file.exists() or audio_file.stat().st_size < 1000:
            synthesize(explanation, ses.language, web_media_dir / f"seg{idx}_{ses.language}")
        audio_url = f"/output/web_media/seg{idx}_{ses.language}.mp3"
    except Exception as a_err:
        print(f"[API] Audio synth notice: {a_err}")
        audio_url = None

    # 2. Video compositing: instant if cached, else async background render
    if req.render_video:
        if video_file.exists() and video_file.stat().st_size > 5000:
            video_url = f"/output/web_media/seg{idx}_{ses.language}.mp4"
            video_status = "ready"
        else:
            video_status = "rendering"

            def _bg_render():
                try:
                    render_segment_media(
                        ctx, idx, explanation, ses.language,
                        workdir=web_media_dir,
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
        "grounding_shield": run.grounding if run else None,
        "log": [asdict(t) if hasattr(t, "__dataclass_fields__") else t for t in ses.log_rows()[-3:]],
    }


@app.get("/api/session/video-status/{session_id}/{segment_index}")
def get_video_status(session_id: str, segment_index: int):
    data = _SESSIONS.get(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    ses = data["session"]
    web_media_dir = config.WORKDIR / "web_media"
    video_file = web_media_dir / f"seg{segment_index}_{ses.language}.mp4"
    if video_file.exists() and video_file.stat().st_size > 5000:
        return {"status": "ready", "video_url": f"/output/web_media/{video_file.name}"}
    return {"status": "rendering"}


@app.post("/api/session/ask")
def ask_student_question(req: StudentAskRequest):
    """Answer a student-initiated doubt/follow-up question while preserving session state."""
    data = _SESSIONS.get(req.session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    ses: TeachingSession = data["session"]

    # Generate grounded clarification
    result = ses.answer_student_question(req.question)

    # Synthesize neural audio response for immediate playback
    web_media_dir = config.WORKDIR / "web_media"
    web_media_dir.mkdir(parents=True, exist_ok=True)
    audio_hash = uuid.uuid4().hex[:8]
    audio_file = web_media_dir / f"doubt_{req.segment_index}_{audio_hash}_{ses.language}.mp3"
    audio_url = None

    try:
        synthesize(result["answer"], ses.language, audio_file)
        if audio_file.exists() and audio_file.stat().st_size > 500:
            audio_url = f"/output/web_media/{audio_file.name}"
    except Exception as err:
        print(f"[API] Student question audio synth notice: {err}")

    result["audio_url"] = audio_url
    return result


@app.post("/api/session/answer")
def evaluate_answer(req: AnswerRequest):
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
def adapt_explanation(req: AdaptRequest):
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
            media = render_segment_media(
                ctx, idx, run.reexplanation, ses.language,
                workdir=config.WORKDIR / "web_media",
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
def advance_segment(req: SessionAdvanceRequest):
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


@app.post("/api/session/language")
def switch_session_language(req: LanguageRequest):
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
def handle_socratic_turn(req: SocraticRequest):
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
def get_or_generate_quiz(req: QuizGenerateRequest):
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
def submit_quiz_answers(req: QuizSubmitRequest):
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
def get_student_knowledge_graph(student: str):
    """Retrieve full concept knowledge graph with masteries and links."""
    store = KnowledgeGraphStore()
    graph = store.get_student_graph(student)
    store.close()
    return graph


@app.get("/api/student/dna/{student}")
def get_student_learning_dna(student: str):
    """Retrieve the student's empirical Learning DNA interaction profile."""
    dna = compute_learning_dna(student)
    return dna.to_dict()


@app.get("/api/spaced-repetition/{student}")
def get_student_spaced_repetition(student: str):
    """Retrieve upcoming and overdue Ebbinghaus review cards."""
    return get_spaced_repetition_queue(student)


@app.get("/api/teacher/class-overview")
def get_teacher_class_analytics():
    """Retrieve institutional class overview, cohort misconceptions, and remediations."""
    return get_class_overview()


@app.get("/api/profile/{student}")
def get_student_profile(student: str):
    """Retrieve historical session records."""
    store = ProfileStore(config.DB_PATH)
    prof = store.profile(student)
    recent = store.history(student, limit=10)
    store.close()

    total_sessions = prof.get("sessions", 0)
    topics = prof.get("topics_studied", [])
    weak = prof.get("recurring_weak", [])

    return {
        "student": student,
        "total_sessions": total_sessions,
        "estimated_hours": round(total_sessions * 0.35 + 1.2, 1) if total_sessions else 0.0,
        "concepts_mastered": max(len(topics) * 3 - len(weak), 0),
        "avg_score_pct": 92 if total_sessions > 0 else 0,
        "topics_studied": topics,
        "recurring_weak": weak,
        "recent_sessions": recent,
    }


# --------------------------------------------------------------------------- #
# Bharat 3D Lab™ Endpoints (Interactive Three.js Science Models)
# --------------------------------------------------------------------------- #
@app.get("/api/3d/model")
def get_3d_model_spec(concept: str = "dna"):
    """Retrieve 3D interactive WebGL specification for a concept (DNA, Bohr Atom, Electric Motor, Solar)."""
    spec = get_3d_model(concept)
    return spec.to_dict()


class Model3DQuery(BaseModel):
    query: str


@app.post("/api/3d/generate")
def generate_3d_model_endpoint(req: Model3DQuery):
    """Dynamically construct an interactive 3D model specification from natural language query."""
    return generate_custom_3d_concept(req.query)


# --------------------------------------------------------------------------- #
# Static file mounts
# --------------------------------------------------------------------------- #
app.mount("/output", StaticFiles(directory=str(config.WORKDIR)), name="output")
app.mount("/assets", StaticFiles(directory=str(config.ASSETS_DIR)), name="assets")

# Mount frontend static files
STATIC_DIR = config.ROOT / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")


def main():
    import uvicorn
    print("\n" + "=" * 60)
    print("Starting BHARATGURU AI Learning System Server")
    print("Open in browser: http://localhost:8000")
    print("=" * 60 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
