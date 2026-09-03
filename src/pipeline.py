"""End-to-end orchestrator used by the CLI scripts and the Streamlit app."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import config
from src.assessment import build_report, format_report, generate_quiz, grade_answer
from src.ingestion import ingest_many
from src.lesson_planner import LearnerInstruction, LessonPlan, make_lesson_plan, parse_instruction
from src.profile_store import ProfileStore
from src.retrieval import build_retriever
from src.teaching import TeachingSession, run_segment
from src.tts import synthesize
from src.video import compose_segment_video, concat_videos


@dataclass
class LessonContext:
    topic: str
    instruction: LearnerInstruction
    plan: LessonPlan
    retriever: object | None
    source_files: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# 1. Ingest + plan
# --------------------------------------------------------------------------- #
def build_lesson(
    topic: str = "",
    instruction_text: str = "",
    upload_paths: list[str | Path] | None = None,
    instruction: LearnerInstruction | str | None = None,
    student: str = "student1",
) -> LessonContext:
    upload_paths = [str(p) for p in (upload_paths or [])]
    retriever = None
    if upload_paths:
        chunks = ingest_many(upload_paths)
        retriever = build_retriever(chunks)

    if isinstance(instruction, LearnerInstruction):
        inst = instruction
    elif isinstance(instruction, str) and instruction:
        inst = parse_instruction(instruction)
    else:
        inst = parse_instruction(instruction_text or "")

    if not topic:
        topic = inst.focus or (Path(upload_paths[0]).stem if upload_paths else "General topic")

    plan = make_lesson_plan(topic, inst, retriever)
    return LessonContext(
        topic=topic,
        instruction=inst,
        plan=plan,
        retriever=retriever,
        source_files=upload_paths,
    )


# --------------------------------------------------------------------------- #
# 2. Media for one segment
# --------------------------------------------------------------------------- #
def render_segment_media(
    ctx: LessonContext,
    seg_index: int,
    explanation_text: str,
    language: str,
    workdir: Path | None = None,
) -> dict:
    workdir = Path(workdir or config.WORKDIR / "media")
    workdir.mkdir(parents=True, exist_ok=True)
    seg = ctx.plan.segments[seg_index]

    audio = synthesize(
        explanation_text, language, workdir / f"seg{seg_index}_{language}"
    )
    video = compose_segment_video(
        title=f"{ctx.plan.title}",
        explanation_text=explanation_text,
        audio_path=audio,
        out_path=workdir / f"seg{seg_index}_{language}.mp4",
        subtitle=f"{seg_index + 1}. {seg.concept}",
    )
    return {"audio": str(audio), "video": str(video), "concept": seg.concept}


# --------------------------------------------------------------------------- #
# 3. Headless full-lesson run (used by test scripts + demo prep)
# --------------------------------------------------------------------------- #
def _scripted_answer(question: str, wrong_for: set[str], concept: str) -> str:
    """Deterministic student: deliberately wrong on the flagged concept."""
    if concept in wrong_for:
        return "The current increases."          # canonical misconception from the brief
    return "It decreases, because with voltage fixed, current is inversely proportional to resistance."


def run_full_lesson(
    ctx: LessonContext,
    *,
    student: str = "demo_student",
    language: str | None = None,
    wrong_on_indices: tuple[int, ...] = (2,),
    make_videos: bool = False,
    store: ProfileStore | None = None,
    verbose: bool = True,
) -> dict:
    language = language or ctx.instruction.language
    session = TeachingSession(ctx.plan, ctx.retriever, language=language)
    wrong_concepts = {
        ctx.plan.segments[i].concept
        for i in wrong_on_indices
        if 0 <= i < len(ctx.plan.segments)
    }

    media = []
    while not session.finished:
        idx = session.idx
        seg = session.current_segment
        run = run_segment(
            session,
            answer_fn=lambda q, c=seg.concept: _scripted_answer(q, wrong_concepts, c),
        )
        if verbose:
            print(f"  [seg {idx}] {run.concept}: verdict={run.verdict} action={run.action}")
        if make_videos:
            text = run.explanation + (
                ("\n\n" + run.reexplanation) if run.reexplanation else ""
            )
            media.append(render_segment_media(ctx, idx, text, language))

    taught = [r.concept for r in session.runs]
    summary = session.score_summary()

    quiz = generate_quiz(ctx.plan, taught)
    q_results = [grade_answer(q, _scripted_answer(q.question, wrong_concepts, q.concept)) for q in quiz]
    report = build_report(ctx.plan, q_results, session_weak=summary["weak"])

    lesson_video = None
    if make_videos and media:
        parts = [Path(m["video"]) for m in media]
        lesson_video = str(concat_videos(parts, config.WORKDIR / "lesson_full.mp4"))

    # persist + next-topic recommendation
    close_store = False
    if store is None:
        store = ProfileStore()
        close_store = True
    store.record_session(
        student, ctx.plan.title,
        language=language, level=ctx.plan.level,
        score=report["raw_score"], out_of=report["out_of"],
        strong=report["strong_areas"], weak=report["needs_improvement"],
    )
    next_topic = store.recommend_next_topic(student, ctx.plan.title)
    if close_store:
        store.close()

    result = {
        "plan_title": ctx.plan.title,
        "grounded": ctx.plan.grounded,
        "language": language,
        "segments_taught": taught,
        "teaching_summary": summary,
        "transition_log": session.log_rows(),
        "quiz_results": [
            {
                "question": r.question.question,
                "concept": r.question.concept,
                "student_answer": r.student_answer,
                "verdict": r.verdict,
                "score": r.score,
            }
            for r in q_results
        ],
        "report": report,
        "report_text": format_report(report),
        "next_topic": next_topic,
        "media": media,
        "lesson_video": lesson_video,
    }
    return result


def save_run_artifacts(result: dict, path: Path | None = None) -> Path:
    path = Path(path or config.WORKDIR / "last_run.json")
    path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    return path
