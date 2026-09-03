"""AI Teacher — Streamlit frontend.

Flow: upload material OR enter a topic + free-text instruction
      -> lesson-plan preview
      -> segment-by-segment video playback with an inline Q&A box
      -> visible "adapting..." moment on a wrong answer
      -> final score / report + recommended next topic

Run:  streamlit run app.py
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

import config
from src.assessment import build_report, format_report, generate_quiz, grade_answer
from src.pipeline import build_lesson, render_segment_media
from src.profile_store import ProfileStore
from src.teaching import State, TeachingSession

st.set_page_config(page_title="AI Teacher", page_icon="🎓", layout="centered")

S = st.session_state
S.setdefault("stage", "setup")
S.setdefault("ctx", None)
S.setdefault("session", None)
S.setdefault("media_cache", {})
S.setdefault("seg_phase", "teach")     # teach | adapt | followup
S.setdefault("quiz", None)
S.setdefault("quiz_answers", {})
S.setdefault("report", None)
S.setdefault("next_topic", None)


def reset():
    for k in ("ctx", "session", "quiz", "report", "next_topic"):
        S[k] = None
    S["media_cache"] = {}
    S["quiz_answers"] = {}
    S["seg_phase"] = "teach"
    S["stage"] = "setup"


# --------------------------------------------------------------------------- #
st.title("🎓 AI Teacher")
st.caption(
    f"Reasoning engine: {'MOCK (offline)' if config.LLM_MOCK else config.GEMINI_MODEL}"
    " · RAG: MiniLM + cosine · Voice: edge-tts · Avatar: amplitude mouth-swap"
)

# ===================== 1. SETUP ===========================================
if S.stage == "setup":
    st.subheader("1 · What should I teach?")
    student = st.text_input("Student name", value="student1")
    uploads = st.file_uploader(
        "Upload material (PDF / DOCX / PPTX / TXT) — optional",
        type=["pdf", "docx", "pptx", "txt", "md"],
        accept_multiple_files=True,
    )
    topic = st.text_input("…or just a topic", value="" if uploads else "Newton's Laws of Motion")
    instruction = st.text_area(
        "Learner instruction (free text)",
        value="I am a beginner, teach me in 20 minutes, in English, with simple examples",
        height=80,
    )
    render_video = st.checkbox("Render narrated avatar video per segment", value=True)
    S["render_video"] = render_video
    S["student"] = student

    if st.button("Build lesson", type="primary"):
        paths = []
        if uploads:
            tmpdir = Path(tempfile.mkdtemp(prefix="aiteacher_"))
            for uf in uploads:
                p = tmpdir / uf.name
                p.write_bytes(uf.getbuffer())
                paths.append(p)
        with st.spinner("Ingesting, retrieving, planning…"):
            S.ctx = build_lesson(topic=topic, instruction_text=instruction, upload_paths=paths)
        S.stage = "plan"
        st.rerun()

# ===================== 2. PLAN ============================================
elif S.stage == "plan":
    ctx = S.ctx
    st.subheader("2 · Lesson plan")
    i = ctx.instruction
    st.write(
        f"**{ctx.plan.title}**  \n"
        f"level `{ctx.plan.level}` · language `{ctx.plan.language}` · "
        f"{i.time_minutes} min · grounded in upload: `{ctx.plan.grounded}`"
    )
    for n, seg in enumerate(ctx.plan.segments, 1):
        with st.expander(f"{n}. {seg.concept}", expanded=n == 1):
            st.write(f"**Depth:** {seg.depth}")
            st.write(f"**Example:** {seg.example}")
            if seg.source_label:
                st.write(f"**Citation:** `{seg.source_label}`  {seg.source_quote}")
            st.write(f"**Checkpoint:** {seg.checkpoint_question}")

    lang = st.selectbox("Teaching language", list(config.LANGUAGES),
                        index=list(config.LANGUAGES).index(ctx.plan.language)
                        if ctx.plan.language in config.LANGUAGES else 0)
    if st.button("Start teaching", type="primary"):
        S.session = TeachingSession(ctx.plan, ctx.retriever, language=lang)
        S.seg_phase = "teach"
        S.stage = "teach"
        st.rerun()

# ===================== 3. TEACH ==========================================
elif S.stage == "teach":
    ses: TeachingSession = S.session
    ctx = S.ctx

    if ses.finished:
        S.stage = "quiz"
        st.rerun()

    idx = ses.idx
    seg = ses.current_segment
    st.subheader(f"3 · Segment {idx + 1} / {len(ctx.plan.segments)} — {seg.concept}")
    st.progress((idx) / max(1, len(ctx.plan.segments)))

    # --- language switch mid-lesson (keeps position + score) ---
    with st.sidebar:
        st.markdown("**Live controls**")
        newlang = st.selectbox("Language", list(config.LANGUAGES),
                               index=list(config.LANGUAGES).index(ses.language))
        if newlang != ses.language:
            ses.set_language(newlang)
            S.media_cache.pop(idx, None)
            st.rerun()
        st.caption(f"Score so far: {ses.score_summary()['correct']} correct")

    # --- EXPLAIN + QUESTION (once per segment) ---
    if ses.current_run is None or not ses.current_run.explanation:
        with st.spinner("Preparing the explanation…"):
            ses.explain()
            ses.question()

    run = ses.current_run

    # --- media ---
    if S.get("render_video"):
        if idx not in S.media_cache:
            with st.spinner("Rendering narrated video (avatar + voice + captions)…"):
                text = run.explanation + (
                    "\n\n" + run.reexplanation if run.reexplanation else ""
                )
                try:
                    S.media_cache[idx] = render_segment_media(
                        ctx, idx, text, ses.language,
                        workdir=config.WORKDIR / "ui_media",
                    )
                except Exception as exc:  # noqa: BLE001
                    st.warning(f"Video render failed ({exc}); showing text only.")
                    S.media_cache[idx] = None
        media = S.media_cache.get(idx)
        if media:
            st.video(media["video"])

    st.markdown(f"**Explanation**\n\n{run.explanation}")
    if run.reexplanation:
        st.info(f"🔄 **Adapted re-explanation**\n\n{run.reexplanation}")

    # --- Q&A ---
    if S.seg_phase == "teach":
        st.markdown(f"**Question:** {run.question}")
        ans = st.text_input("Your answer", key=f"ans_{idx}")
        if st.button("Submit answer", type="primary"):
            ses.evaluate(ans)
            res = ses.adapt()
            if res["action"] == "advance":
                ses.advance()
                st.rerun()
            else:
                S.seg_phase = "followup"
                S.media_cache.pop(idx, None)   # re-render with the re-explanation
                st.rerun()

    elif S.seg_phase == "followup":
        st.warning("⚙️ Adapting to your answer — re-teaching with a different analogy…")
        st.markdown(f"**Misconception spotted:** {run.misconception or '—'}")
        st.markdown(f"**Follow-up question:** {run.followup_question}")
        fa = st.text_input("Your answer", key=f"fans_{idx}")
        if st.button("Submit follow-up", type="primary"):
            ses.evaluate(fa, followup=True)
            ses.advance()
            S.seg_phase = "teach"
            st.rerun()

# ===================== 4. QUIZ ===========================================
elif S.stage == "quiz":
    ses: TeachingSession = S.session
    ctx = S.ctx
    st.subheader("4 · End-of-lesson assessment")
    taught = [r.concept for r in ses.runs]

    if S.quiz is None:
        with st.spinner("Generating quiz from what was taught…"):
            S.quiz = generate_quiz(ctx.plan, taught)

    for n, q in enumerate(S.quiz):
        st.markdown(f"**Q{n + 1} ({q.type}).** {q.question}")
        if q.type == "mcq" and q.options:
            S.quiz_answers[n] = st.radio(
                "choose", q.options, key=f"q_{n}", label_visibility="collapsed"
            )
        else:
            S.quiz_answers[n] = st.text_input("answer", key=f"q_{n}",
                                              label_visibility="collapsed")

    if st.button("Submit quiz", type="primary"):
        with st.spinner("Grading…"):
            results = [grade_answer(q, S.quiz_answers.get(n, ""))
                       for n, q in enumerate(S.quiz)]
            summary = ses.score_summary()
            report = build_report(ctx.plan, results, session_weak=summary["weak"])
            store = ProfileStore()
            store.record_session(
                S.get("student", "student1"), ctx.plan.title,
                language=ses.language, level=ctx.plan.level,
                score=report["raw_score"], out_of=report["out_of"],
                strong=report["strong_areas"], weak=report["needs_improvement"],
            )
            S.next_topic = store.recommend_next_topic(
                S.get("student", "student1"), ctx.plan.title
            )
            store.close()
            S.report = report
            S.quiz_results = results
        S.stage = "report"
        st.rerun()

# ===================== 5. REPORT ========================================
elif S.stage == "report":
    ses: TeachingSession = S.session
    st.subheader("5 · Learning feedback")
    st.code(format_report(S.report), language="text")

    st.markdown("**Per-concept during teaching**")
    st.json(ses.score_summary()["by_concept"])

    st.markdown(f"**Recommended next topic:** {S.next_topic['next_topic']}  \n"
                f"_{S.next_topic['reason']}_")

    with st.expander("Adaptation / transition log"):
        st.dataframe(ses.log_rows())

    if st.button("Start a new lesson"):
        reset()
        st.rerun()
