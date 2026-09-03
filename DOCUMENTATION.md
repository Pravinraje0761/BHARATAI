# AI Teacher — Technical Documentation

## 1. Problem statement

Students need a tutor that can take *their own* study material or a topic name,
teach it the way a good human teacher would — explain, check, notice where the
student is confused, and re-teach differently — and do it in the student's
language with voice and a presenter on screen, not just a wall of text. It must
also assess the student and track progress across sessions.

## 2. Solution overview

A pipeline of small, single-responsibility modules wired together by
`src/pipeline.py`:

```
upload / topic + free-text instruction
        │
        ▼
 ingestion ──► chunks (text + page/slide/section)
        │
        ▼
 retrieval  (MiniLM embeddings, in-memory cosine)
        │
        ▼
 instruction parser ─┐
                     ├─► lesson-plan agent ─► LessonPlan(segments[])
 retrieved context ──┘
        │
        ▼
 TeachingSession state machine, per segment:
     EXPLAIN ─► QUESTION ─► EVALUATE ─► ADAPT ─┐
        ▲                                      │ advance
        └──────────── reinforce/simplify ◄─────┘
        │
        ▼  (per segment)
 tts ─► audio ;  avatar+visuals ─► frames ;  video ─► MP4 (voice+captions+avatar)
        │
        ▼
 assessment: quiz from taught concepts ─► grade ─► report (their format)
        │
        ▼
 profile_store (SQLite): session history ─► recommended next topic
```

## 3. Key features

- Learns from PDF / DOCX / PPTX / TXT, or from a topic string alone.
- Citation-grounded: every retrieved chunk carries `p.N` / `slide N` / `section N`,
  and the planner copies that tag into each segment.
- Personalization: a parsed `{level, time_minutes, language, style, focus}`
  profile is threaded into every generation prompt.
- Explicit adaptive teaching loop with misconception diagnosis and a *different*
  analogy on re-explanation, plus a difficulty bump after two correct in a row.
- Narrated video per segment: subject-tinted slide, picture-in-picture avatar
  lip-synced to audio amplitude, burned-in progressive captions.
- English / Hindi / Hinglish, switchable mid-lesson without losing progress.
- End-of-lesson quiz limited to concepts actually taught; report in the exact
  requested format; cross-session progress store with a next-topic suggestion.

## 4. Architecture — the state machine

`src/teaching.py :: TeachingSession`

| State | Method | What it does |
|---|---|---|
| `EXPLAIN` | `explain()` | Generates a 90–140 word spoken explanation grounded in the segment's cited source chunk, in the requested example style and language. Adds a subtlety if the depth bump is active. |
| `QUESTION` | `question()` | One checkpoint question — alternates MCQ / short-answer by segment index — testing understanding, not recall. |
| `EVALUATE` | `evaluate(answer, followup=False)` | Gemini JSON grader with 2–3 baked-in few-shot examples (the resistance / Ohm's-law case from the brief). Returns `{verdict: correct|partial|incorrect, misconception, feedback}`. |
| `ADAPT` | `adapt()` | `correct` → advance (and, on a 2-streak, raise depth). `partial`/`incorrect` → re-explain with a **new analogy** that names the misconception, then ask a **related but different** follow-up question. |

Every transition is appended to `session.log` and dumped via `log_rows()` — this
is both the debug trace and the demo evidence of real adaptation.

Mid-lesson language switch: `set_language()` only changes the language used by
subsequent prompts; `idx`, `runs`, streak and depth bump are untouched.

## 5. RAG implementation

`src/ingestion.py` extracts text per page/slide/section and packs it into
220–480-word chunks on paragraph/heading boundaries, keeping a `source_label`
and `source_page` on every `Chunk`.

`src/retrieval.py` embeds all chunks once with `sentence-transformers`
`all-MiniLM-L6-v2` (normalized vectors), and `retrieve(query, k)` is a single
matrix–vector product plus `argsort` — exact cosine ranking. `context_block()`
formats the top-k as citation-tagged text for the planner and the teaching
prompts. At one-lesson scale (tens of chunks) this is instant; a vector DB would
add a service to run without changing the answers.

## 6. Prompt / agent architecture

Four Gemini call sites, all via `src/llm.py`:

- **instruction parser** — free text → `{level, time_minutes, language, style, focus}` JSON.
- **lesson-plan agent** — retrieved context (or none) + learner profile + a
  duration template (`5/20/60 min → segment count + depth`) → ordered
  `segments[]` JSON with `concept, depth, example, checkpoint_question,
  source_label, source_quote`.
- **teaching prompts** — `explain` / `reexplain` / `question`, each with a
  language hint and the segment's grounding.
- **evaluation & assessment** — `evaluate` (few-shot grader), `generate_quiz`,
  `grade_answer`, `build_report`, `recommend_next_topic`.

`src/llm.py` centralises JSON extraction (handles code fences), a JSON-mode
request with a graceful fallback for older models, and an offline `LLM_MOCK`
stub that branches on a `tag` each caller passes — so the full pipeline and all
three test scripts run with no API key.

## 7. Personalization approach

`LearnerInstruction` is parsed once and then:
- selects the duration template (segment count + depth language),
- sets `level` and `style` text injected into the planner and every teaching prompt,
- sets the initial `language`,
- `focus` narrows the retrieval query and the plan's topic.

During teaching, performance feeds back: wrong answers change the *next*
explanation (new analogy, misconception named); two correct answers raise the
depth of the next segment.

## 8. Assessment methodology

`src/assessment.py`:
- `generate_quiz(plan, taught_concepts)` — 3–6 mixed MCQ/short questions
  restricted to concepts that were actually taught this session.
- `grade_answer` — deterministic match first for MCQ (exact / option letter /
  substring), else a Gemini JSON grader returning `verdict + score∈[0,1]`.
- `build_report` — aggregates per-concept scores, merges in the concepts the
  student struggled with *during teaching*, and returns
  `{topic, score "X/Y", strong_areas[], needs_improvement[], recommendation}` —
  the exact shape in the brief. `format_report` renders the plain-text version.

## 9. Multilingual implementation

`config.LANGUAGES` maps a display name to an ISO code and an `edge-tts` voice.
Text generation is native — Gemini is prompted with a per-language style hint
(`Devanagari` for Hindi, `Latin-script Hindi + English terms` for Hinglish); no
separate translation step. Voice uses the mapped neural voice. Adding a language
is one row plus a voice name.

## 10. Voice implementation

`src/tts.synthesize(text, language, out_path)`:
1. `edge-tts` with the mapped neural voice → MP3.
2. on failure, `gTTS` (`hi`/`en`) → MP3.
3. on failure, a silence WAV sized to the word count — the video pipeline still
   produces a captioned MP4 offline.

## 11. Avatar / video approach

`src/avatar.py` renders (or loads, if a designer replaces them) three
mouth-state PNGs. `librosa` computes the audio RMS envelope, sampled at the
video frame rate and thresholded into `closed / half / open`, with single-frame
jitter removed.

`src/video.compose_segment_video`:
- `src/visuals.render_slide` draws a subject-tinted title+bullets slide,
- each frame = slide + picture-in-picture avatar (mouth state for that frame) +
  a progressive caption drawn with PIL,
- OpenCV writes a silent MP4, then `ffmpeg` muxes the narration (`-shortest`,
  `libx264`/`aac`). `ffmpeg` is found on PATH or via bundled `imageio-ffmpeg`.
- `concat_videos` joins segment MP4s into one lesson video.

This is a deliberate substitute for SadTalker: no GPU, no 2 GB model download,
builds in hours, still satisfies "human-like avatar + natural voice".

## 12. Student profile / learning path

`src/profile_store.py` — SQLite table `sessions(student, topic, language, level,
score, out_of, strong, weak, created_at)`. `profile()` aggregates history;
`recommend_next_topic()` feeds the history (topics, recurring weak/strong
concepts, current topic) to Gemini for one `{next_topic, reason}` suggestion
whose reason cites a specific weak area when one exists. Running two sessions
back-to-back, the second recommendation reflects the first session's weak areas
(`scripts/test_day3.py` asserts this).

## 13. Models / APIs used (Section 16 disclosure)

| Component | Model / library | Where |
|---|---|---|
| Reasoning, planning, grading, reports | Google **Gemini** (`gemini-2.5-flash` / `gemini-1.5-flash`) via `google-generativeai` | `src/llm.py` |
| Text embeddings | `sentence-transformers` **all-MiniLM-L6-v2** | `src/retrieval.py` |
| Text-to-speech | **edge-tts** (primary neural voices), **gTTS** (fallback) | `src/tts.py` |
| Audio analysis | **librosa**, **soundfile** | `src/avatar.py` |
| Document parsing | **pypdf**, **python-docx**, **python-pptx** | `src/ingestion.py` |
| Image / video | **Pillow**, **OpenCV**, **ffmpeg** (`imageio-ffmpeg` fallback) | `src/visuals.py`, `src/video.py` |
| Primary Web UI & API Server | **FastAPI**, **Uvicorn**, **Tailwind CSS**, **HTML5 Canvas** (Stitch Design System) | `server.py`, `static/` |
| Secondary Dashboard | **Streamlit** | `app.py` |

No user data leaves the machine except the text sent to the Gemini API.

## 14. Setup & deployment

- **Primary Web Interface**: `python server.py` (Runs on `http://localhost:8000`)
- **Secondary Streamlit Dashboard**: `streamlit run app.py`
- All verification test scripts (`test_day1.py`, `test_day2.py`, `test_day3.py`, `test_server_api.py`) run locally and completely offline with `LLM_MOCK=1`.
- For cloud deployment, deploy via Docker or Uvicorn container: add `GEMINI_API_KEY` to environment variables; bundled `imageio-ffmpeg` handles video compositing automatically.

## 15. Known limitations

Stated plainly, each a 3-day time-budget decision rather than an oversight:

- **Avatar** is amplitude-driven mouth-swap, not neural lip-sync (SadTalker).
  Chosen to remove the GPU / CUDA / 2 GB-download risk from a 3-day build.
- **Retrieval** is brute-force cosine over an in-memory list, not a production
  vector DB (Chroma). Exact and instant at one-lesson scale; would need
  replacing only for cross-corpus / millions-of-chunks use.
- **Languages** are English / Hindi / Hinglish, not the full Indian-language
  set. Extensible via `config.LANGUAGES`.
- **Voice** is `edge-tts`. **Bhashini** is named as a planned upgrade but not
  integrated — its onboarding/registration does not fit a 3-day window.
- **7-day revision-plan mode** is not built; the 5 / 20 / 60-minute duration
  templates cover the time-based requirement.
