"""AI Teacher — 3-day sprint build.

Package layout:
    llm             Gemini wrapper (+ deterministic offline mock)
    ingestion       PDF / DOCX / PPTX / TXT parsing into cited chunks
    retrieval       sentence-transformers embeddings + in-memory cosine search
    lesson_planner  learner-instruction parser + lesson-plan agent
    teaching        EXPLAIN -> QUESTION -> EVALUATE -> ADAPT state machine
    tts             edge-tts synthesis with gTTS fallback
    avatar          amplitude-driven mouth-swap avatar frames
    visuals         PIL slide rendering
    video           frame + audio compositing / muxing / caption burn-in
    assessment      end-of-lesson quiz + report
    profile_store   SQLite per-session progress store
    pipeline        end-to-end orchestrator used by the CLI scripts and app
"""

__version__ = "1.0.0"
