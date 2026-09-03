# 🎓 BHARATGURU — Comprehensive Features Specification & Architecture Manual

> **System Overview**: BHARATGURU is an autonomous, adaptive, multilingual pedagogical AI learning platform engineered specifically for Indian students and curricula. It ingests academic study materials (PDF, DOCX, PPTX, TXT, MD) or syllabus topics, constructs citation-grounded lesson plans, teaches segment-by-segment with an amplitude-driven lip-synced avatar and neural Indian voices, detects and fingerprints student misconceptions, dynamically adapts teaching strategies, provides interactive 3D WebGL simulations, models prerequisite knowledge graphs, computes empirical cognitive Learning DNA, schedules spaced repetition reviews, and provides class-level teacher analytics.

---

## 📑 Table of Contents

1. [Architectural Overview & Core Pedagogy](#1-architectural-overview--core-pedagogy)
2. [Document Ingestion & Multi-Format Parsing](#2-document-ingestion--multi-format-parsing)
3. [Hybrid RAG Retrieval Engine](#3-hybrid-rag-retrieval-engine)
4. [Multi-Tiered Cascading LLM Architecture](#4-multi-tiered-cascading-llm-architecture)
5. [Bharat Context Engine™ (Cultural Metaphors)](#5-bharat-context-engine-cultural-metaphors)
6. [Hallucination Shield & Citation Grounding Verifier](#6-hallucination-shield--citation-grounding-verifier)
7. [Adaptive Pedagogical State Machine & Teaching Loop](#7-adaptive-pedagogical-state-machine--teaching-loop)
8. [Misconception Engine™ & Cognitive Fingerprinting](#8-misconception-engine--cognitive-fingerprinting)
9. [Adaptive Pedagogy Policy Selector & Socratic Dialogue](#9-adaptive-pedagogy-policy-selector--socratic-dialogue)
10. [12 Indian Languages Multilingual Neural TTS](#10-12-indian-languages-multilingual-neural-tts)
11. [Pure-CPU Lip-Synced Avatar & Ultrafast Video Compositing](#11-pure-cpu-lip-synced-avatar--ultrafast-video-compositing)
12. [Bharat 3D Lab™ — Universal WebGL Science Visualizer](#12-bharat-3d-lab--universal-webgl-science-visualizer)
13. [Student Knowledge Graph & Dependency Modeler](#13-student-knowledge-graph--dependency-modeler)
14. [Learning DNA Profiler (5D Cognitive Spectrum)](#14-learning-dna-profiler-5d-cognitive-spectrum)
15. [Ebbinghaus Spaced Repetition Retention Engine (SM-2)](#15-ebbinghaus-spaced-repetition-retention-engine-sm-2)
16. [Institutional Teacher Dashboard & Cohort Analytics](#16-institutional-teacher-dashboard--cohort-analytics)
17. [Formative Assessment, Dynamic Quizzing & Report Cards](#17-formative-assessment-dynamic-quizzing--report-cards)
18. [Cross-Session Profile Store & Next-Topic Recommender](#18-cross-session-profile-store--next-topic-recommender)
19. [Dual Frontend Interfaces (Modern Stitch Web SPA & Streamlit)](#19-dual-frontend-interfaces-modern-stitch-web-spa--streamlit)
20. [Complete REST API Reference](#20-complete-rest-api-reference)
21. [Verification & Automated Test Suite](#21-verification--automated-test-suite)

---

## 1. Architectural Overview & Core Pedagogy

BHARATGURU is designed around active learning rather than passive content consumption:
- **Segmented Cognitive Load**: Instead of overwhelming students with 30-minute lectures, lessons are partitioned into bite-sized segments (60–95 words per concept).
- **Mandatory Conceptual Checkpoints**: Every segment concludes with an evaluative question checking comprehension before the student can advance.
- **Root-Cause Flaw Diagnosis**: Student mistakes are not merely categorized as "wrong"; the system extracts cognitive misconceptions and prescribes pedagogical remedies.
- **Zero-GPU Accessible Delivery**: High-fidelity animated avatars, neural audio, and 3D visualizers run locally and efficiently on commodity CPU hardware without requiring high-end GPUs.

```
Upload (PDF/DOCX/PPTX/TXT) or Topic
               │
               ▼
   [Multi-Format Ingestion] ──► Chunks tagged with [doc p.N / slide N / section N]
               │
               ▼
   [Hybrid RAG Engine] ─────► Dense MiniLM + Sparse BM25 + Reciprocal Rank Fusion
               │
               ▼
   [Lesson Planner] ────────► Segmented LessonPlan mapped to student constraints
               │
               ▼
   ┌────────────────── TeachingSession State Machine ───────────────────┐
   │                                                                    │
   │  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌────────┐  │
   │  │ EXPLAIN  │ ───► │ QUESTION │ ───► │ EVALUATE │ ───► │ ADAPT  │  │
   │  └──────────┘      └──────────┘      └──────────┘      └────────┘  │
   │       ▲                                                     │      │
   │       └────────── Re-explain with new analogy ──────────────┘      │
   │                     or Advance on mastery                          │
   └────────────────────────────────────────────────────────────────────┘
               │
   ┌───────────┴───────────────────────┬────────────────────────┐
   ▼                                   ▼                        ▼
[Media & Video]                 [Cognitive Models]       [Assessment & Store]
- Neural TTS (12 Indic Langs)   - Knowledge Graph        - Dynamic Quizzing
- 3-State Mouth Lip-Sync        - Learning DNA Profiler  - Diagnostic Reports
- Ultrafast MP4 Compositor      - Spaced Repetition SM-2 - Teacher Dashboard
- Bharat 3D Lab (WebGL Three.js)- Hallucination Shield   - SQLite Profiles
```

---

## 2. Document Ingestion & Multi-Format Parsing
*Source: `src/ingestion.py`*

- **Universal Multi-Format Support**:
  - **PDF Documents (`pypdf`)**: Extracts text while mapping each chunk to physical page numbers (`p.1`, `p.2`, etc.).
  - **Word DOCX Documents (`python-docx`)**: Parses heading hierarchy (`Heading 1`, `Heading 2`) to preserve logical document sections (`section 1`, `section 2`).
  - **PowerPoint PPTX Presentations (`python-pptx`)**: Traverses slide shapes and text frames, tagging chunks with exact slide numbers (`slide 1`, `slide 2`).
  - **Plaintext & Markdown (`.txt`, `.md`)**: Detects chapters, units, and headers via pattern matching.
- **Word-Bounded Contextual Chunking**:
  - Segments documents using strict sentence and paragraph boundaries without mid-word or mid-sentence truncation.
  - Configurable chunk thresholds (`CHUNK_MIN_WORDS = 220`, `CHUNK_MAX_WORDS = 480`).
- **Permanent Citation Metadata**:
  - Every chunk retains immutable metadata: `doc_name`, `source_page`, and `source_label`.
  - Enables full trace-back verification across every explanation and generated quiz question.

---

## 3. Hybrid RAG Retrieval Engine
*Source: `src/hybrid_rag.py`, `src/retrieval.py`*

- **Dense Semantic Embeddings**:
  - Utilizes `sentence-transformers/all-MiniLM-L6-v2` locally (cached offline via `HF_HUB_OFFLINE=1`).
  - Generates 384-dimensional unit-normalized embeddings.
  - High-speed in-memory cosine ranking using vectorized matrix-vector multiplication (`_matrix @ q`).
- **Sparse BM25 Keyword Search (`BM25Index`)**:
  - Zero-dependency custom BM25 tokenizer and ranker.
  - Uses standard parameters ($k_1 = 1.5, b = 0.75$) with length normalization and Inverse Document Frequency (IDF).
- **Reciprocal Rank Fusion (RRF)**:
  - Merges dense semantic vector search with sparse keyword search using formula:
    $$RRF(d) = \sum \frac{1}{60 + r(d)}$$
  - Delivers superior accuracy on domain-specific scientific terminology, chemical formulas, and mathematical notation.
- **Citation-Tagged Prompt Formatting**:
  - Generates structured, bracketed context blocks directly consumed by the Lesson Planner and Hallucination Shield.

---

## 4. Multi-Tiered Cascading LLM Architecture
*Source: `src/llm.py`, `config.py`*

- **Tri-Tier Inference Cascade**:
  1. **Tier 1: Groq LPU (Sub-Second Lightning Inference)**:
     - Leverages ultra-fast LPU inference (Groq OpenAI-compatible endpoint) using `qwen/qwen3.8-27b`, `groq/compound-mini`, or `llama3-70b-8192` with ~0.8s time-to-first-token.
  2. **Tier 2: NVIDIA NIM (High-Performance GPU Inference)**:
     - Cloud GPU inference using `meta/llama-3.2-11b-vision-instruct` or `meta/llama-3.1-70b-instruct`.
  3. **Tier 3: Google Gemini API**:
     - Direct multimodal integration via `google-generativeai` (`gemini-2.5-flash` or `gemini-1.5-flash`).
- **Offline Deterministic Pedagogical Mock**:
  - Toggleable via `LLM_MOCK=1`.
  - Provides instant, offline-capable responses for unit tests, offline demos, and air-gapped evaluation.
- **Robust JSON Extraction**:
  - Employs regex recovery and schema validation (`generate_json`) to guarantee valid JSON outputs even in the event of minor model syntax variations.

---

## 5. Bharat Context Engine™ (Cultural Metaphors)
*Source: `src/bharat_context.py`*

- **Localized Indian Real-World Anchors**:
  - Systematically grounds abstract science and math concepts in relatable Indian phenomena:
    - **Physics / Mechanics**: Cricket ball impact, bowling spin, Mumbai local train momentum, auto-rickshaw braking distance, ISRO launch stages.
    - **Electricity / Circuits**: Inverter battery backup, Diwali string lights in series vs. parallel, domestic electric meter units.
    - **Chemistry / Biology**: Chai boiling & sugar saturation, turmeric acid-base indicator, monsoon crop cycles, camphor sublimation in puja.
    - **Economics / Math**: Kirana store ledgers, UPI transactions, Rupee (₹) unit calculations, Indian railway timetable distance-speed problems.
- **Indianized Tone & Terminology**:
  - Replaces Western examples (e.g., baseball, dollars, snow plows) with familiar Indian contexts across all 12 supported languages.

---

## 6. Hallucination Shield & Citation Grounding Verifier
*Source: `src/hallucination_shield.py`*

- **Real-Time Fact Verification**:
  - Compares every generated explanation against the retrieved document chunks.
  - Uses an N-gram sliding window and claim containment checker.
- **Metric Confidence Scoring**:
  - Calculates a mathematical grounding confidence score (0.0 to 1.0).
  - Flags claims not directly supported by uploaded syllabus materials.
- **User-Facing Inspection Modal**:
  - The UI displays a `100% GROUNDED` badge.
  - Students and educators can click "Inspect Source" to view the verbatim text chunk, document filename, and page number backing each explanation.

---

## 7. Adaptive Pedagogical State Machine & Teaching Loop
*Source: `src/teaching.py`*

- **Five Explicit States**:
  - `EXPLAIN`: Synthesizes concise conceptual explanations anchored in real-world examples.
  - `QUESTION`: Poses Socratic checkpoint questions to test conceptual understanding.
  - `EVALUATE`: Analyzes the student's free-text or selected answer.
  - `ADAPT`: Chooses an alternative pedagogical strategy if the student has a misconception.
  - `DONE`: Concludes the segment and updates longitudinal mastery records.
- **Dynamic Difficulty Escalation**:
  - Tracks consecutive correct answers.
  - After 2 consecutive correct answers, automatically increases conceptual depth (`depth: standard -> deep`).
- **Audit Trail & Transition Logging**:
  - Records every state transition timestamp, evaluated answer, misconception tag, and strategy selection for verifiable learning telemetry.

---

## 8. Misconception Engine™ & Cognitive Fingerprinting
*Source: `src/misconception_engine.py`*

- **Empirical Flaw Taxonomy**:
  - Automatically classifies student errors into distinct cognitive failure modes:
    - `INVERSION`: Confusing direct vs. inverse proportionality (e.g., claiming current increases when resistance increases).
    - `CONFLATION`: Blending two distinct physical quantities (e.g., confusing voltage with current, or speed with acceleration).
    - `OVERGENERALIZATION`: Applying a specific rule to invalid contexts (e.g., assuming Ohm's law applies to non-ohmic conductors).
    - `OMISSION`: Neglecting critical variables or boundary conditions.
- **Targeted Feedback Generation**:
  - Explains the exact reasoning flaw to the student without generic "Try Again" messages.

---

## 9. Adaptive Pedagogy Policy Selector & Socratic Dialogue
*Source: `src/pedagogy.py`*

- **Adaptive Policy Selection**:
  - When re-explaining, the system never repeats the prior explanation verbatim. It dynamically shifts between:
    1. `ANALOGY`: Introduces a completely new physical metaphor.
    2. `COUNTEREXAMPLE`: Presents a thought experiment demonstrating where the student's misconception breaks down.
    3. `FIRST_PRINCIPLES`: Strips away analogies and explains the fundamental physical law.
    4. `SCAFFOLDED_BREAKDOWN`: Deconstructs the concept into smaller, progressive sub-steps.
    5. `VISUAL_METAPHOR`: Outlines an intuitive geometric or schematic representation.
- **Socratic Dialogue Mode**:
  - Supports conversational inquiry guiding the student toward the answer through leading questions rather than simply revealing the solution.
- **Student-Initiated Follow-Up Questions (`POST /api/session/ask`)**:
  - **Live Doubt Interrupt**: Students can interrupt the lesson at any time with arbitrary free-text questions or choose quick doubts (*"Another real-world example?"*, *"Why does this happen in real life?"*, *"Link to previous concept?"*).
  - **Hybrid RAG Contextual Grounding**: Retrieves curriculum chunks scoped to the current segment, full lesson plan, and prior segments to answer doubts with verified citations.
  - **State Preservation**: Answers doubts without advancing or losing the student's lesson state (`state` and `segment_index` remain strictly preserved).
  - **Spoken Neural Audio Response**: Automatically synthesizes neural voice audio clarification in the active language and renders inline.
  - **Audit Trail Logging**: Logs all doubts, teacher answers, and confidence scores into the transition audit trail for demo inspection.

---

## 10. 12 Indian Languages Multilingual Neural TTS
*Source: `src/tts.py`*

- **Comprehensive Indic Language Coverage**:
  - Fully supports 12 languages:
    1. **English (Indian Accent - `en-IN`)**
    2. **Hindi (`hi-IN`)**
    3. **Hinglish (Colloquial Hindi-English hybrid)**
    4. **Tamil (`ta-IN`)**
    5. **Telugu (`te-IN`)**
    6. **Kannada (`kn-IN`)**
    7. **Malayalam (`ml-IN`)**
    8. **Bengali (`bn-IN`)**
    9. **Marathi (`mr-IN`)**
    10. **Gujarati (`gu-IN`)**
    11. **Punjabi (`pa-IN`)**
    12. **Urdu (`ur-IN`)**
- **Neural Synthesis with Fallback**:
  - Primary: `edge-tts` utilizing high-quality Microsoft Neural Indic speech models.
  - Secondary: `gTTS` fallback for zero-downtime offline/network resilience.
- **Mid-Lesson Language Switching**:
  - Students can switch languages mid-session with a single click without losing their progress or segment state.

---

## 11. Pure-CPU Lip-Synced Avatar & Ultrafast Video Compositing
*Source: `src/avatar.py`, `src/video.py`, `src/visuals.py`*

- **Amplitude-Driven Lip-Sync Avatar**:
  - Operates on pure CPU without requiring heavy neural avatars or CUDA dependencies.
  - Analyzes audio volume envelope RMS using high-speed `soundfile` and vectorized NumPy.
  - Dynamically drives 3 persona mouth states: `closed`, `half`, and `open`.
- **Ultrafast Video Compositor (< 2.5 seconds)**:
  - Pre-renders composite base frames for all 3 mouth states and progressive caption steps into an in-memory BGR lookup table.
  - Eliminates per-frame PIL image copies and NumPy allocations.
  - Employs FFmpeg with `-preset ultrafast -tune stillimage -crf 26 -movflags +faststart`.
  - Atomic file writing ensures the web frontend never receives a partially encoded video.
- **Synchronized Progressive Subtitles**:
  - Automatically burns readable, progressive subtitles matching the audio narration timing.
- **Subject-Aware Visual Slide Generator**:
  - Dynamically generates branded slides with color tints reflecting the subject matter (Navy for Physics/Electricity, Emerald for Chemistry, Plum for Biology, Terracotta for History, Charcoal for Math).

---

## 12. Bharat 3D Lab™ — Universal WebGL Science Visualizer
*Source: `src/model_3d.py`, `static/three_lab.js`*

- **Interactive 3D WebGL Simulation Canvas**:
  - Integrated directly into the web UI via Three.js with orbit controls, pan, zoom, and lighting.
- **Pre-Built Interactive Scientific Models**:
  - **Bohr Atom Model**: Multi-shell electron orbits, nucleus particle cluster, real-time orbital rotations.
  - **DNA Double Helix**: Intertwined helical strands, connecting base pairs with color-coded hydrogen bonds.
  - **Electric Motor & Magnetic Field**: Dual magnetic poles (N/S), rotating wire armature, dynamic magnetic flux field lines.
  - **Projectile Motion & Bowling Trajectory**: Parabolic flight paths, vector velocity indicators, ground plane grid.
- **Natural Language-to-3D Generator (`/api/3d/generate`)**:
  - Converts arbitrary science queries into Three.js 3D scene specifications (geometries, materials, rotation speeds, particle clouds, labels).

---

## 13. Student Knowledge Graph & Dependency Modeler
*Source: `src/knowledge_graph.py`, `static/knowledge_graph.js`*

- **Prerequisite Dependency Modeling**:
  - Models syllabus topics as directed acyclic graphs (DAGs) capturing prerequisite relationships (e.g., `Electric Charge -> Potential Difference -> Ohm's Law -> Series & Parallel Circuits`).
- **Dynamic Mastery Tracking**:
  - Updates node states in real-time as students answer questions:
    - 🟢 `Mastered` (Score $\ge 80\%$)
    - 🟡 `Learning` (Attempted, progressing)
    - 🔴 `Struggling` (Misconception identified)
    - ⚪ `Unvisited` (Upcoming in curriculum)
- **Interactive Force-Directed Visualizer**:
  - Visualized in the web interface with zoomable, draggable SVG/Canvas nodes and real-time status highlights.

---

## 14. Learning DNA Profiler (5D Cognitive Spectrum)
*Source: `src/learning_dna.py`*

- **Five-Dimensional Cognitive Metrics**:
  1. **Learning Pace**: Speed of concept assimilation and answer response latency.
  2. **Conceptual vs. Procedural Balance**: Ratio of theoretical understanding to formulaic calculation skill.
  3. **Retention Index**: Empirical score tracking recall stability across recurring concepts.
  4. **Confidence Index**: First-attempt accuracy vs. multi-turn hint dependency.
  5. **Visual vs. Verbal Preference**: Engagement ratio with 3D models/slides vs. text/audio narration.
- **Radar Chart Visualization**:
  - Rendered dynamically in the frontend to give learners transparent insight into their cognitive profile.

---

## 15. Ebbinghaus Spaced Repetition Retention Engine (SM-2)
*Source: `src/spaced_repetition.py`*

- **SuperMemo-2 (SM-2) & Leitner-Box Algorithm**:
  - Calculates optimal review intervals using empirical memory decay curves:
    $$I(n) = I(n-1) \times EF$$
  - Adjusts Easiness Factor (EF) based on response accuracy and response time.
- **Automated Review Queue**:
  - Surfaces concepts due for revision at 1-day, 3-day, 7-day, and 14-day intervals.
  - Directly feeds into personalized warm-up quizzes for subsequent sessions.

---

## 16. Institutional Teacher Dashboard & Cohort Analytics
*Source: `src/teacher_dashboard.py`*

- **Classroom Intervention Insights**:
  - Aggregates individual learner telemetry across an entire classroom or cohort.
- **Key Administrative Features**:
  - **Cohort Mastery Heatmap**: Overview of concept proficiency across all enrolled students.
  - **Class-Wide Misconception Distribution**: Identifies topics where the majority of students are failing (e.g., "65% of Class 10-A inverted current vs. resistance").
  - **At-Risk Student Alerts**: Highlights learners requiring human teacher intervention.
  - **Curriculum Pacing Tracking**: Measures syllabus completion rate against academic deadlines.

---

## 17. Formative Assessment, Dynamic Quizzing & Report Cards
*Source: `src/assessment.py`*

- **Strict Taught-Concept Quizzing**:
  - Generates diagnostic end-of-lesson quizzes restricted *strictly* to concepts taught during the active session, eliminating out-of-scope testing.
- **Natural Language Answer Grading**:
  - Evaluates student free-text answers using rubric-based semantic grading (Correct, Partial, Incorrect) with constructive feedback.
- **Comprehensive Diagnostic Report Cards**:
  - Emits formal performance assessments containing:
    - Numerical & percentage scores (e.g., `Score: 80% (4/5)`).
    - Concept-by-concept breakdown.
    - Diagnosed misconceptions with specific remediation notes.
    - Algorithmic recommendation for the next lesson topic.

---

## 18. Cross-Session Profile Store & Next-Topic Recommender
*Source: `src/profile_store.py`*

- **Persistent SQLite Datastore (`profiles.sqlite3`)**:
  - Stores student history, lesson plans, quiz attempts, mastery transitions, and weak/strong concept lists across sessions.
- **Algorithmic Curriculum Progression**:
  - Computes weak concept prerequisites and recommends the optimal next lesson topic to maintain momentum without leaving learning gaps.

---

## 19. Dual Frontend Interfaces

### A. Primary Modern Stitch Web SPA (FastAPI + HTML5/Canvas/Three.js)
*Source: `static/index.html`, `static/app.js`, `static/styles.css`*
- **Google Stitch Design System**: Dark-themed, high-contrast, accessibility-compliant typography and glassmorphic cards.
- **Integrated Learning Suite**:
  - Real-time video/audio narration player with instant streaming fallback.
  - Live interactive 3D WebGL laboratory canvas.
  - Interactive Student Knowledge Graph visualizer.
  - Student Learning DNA radar chart.
  - Real-time speech rate adjustment (0.75x to 1.5x).
  - Quick-preset learning modes: 🏏 Cricket Analogy, 🎓 Professor Style, ⚡ 5-Minute Blitz, 🏛️ Socratic Guide, 🇮🇳 Tanglish.

### B. Secondary Streamlit Dashboard
*Source: `app.py`*
- Rapid prototyping and inspection interface allowing teachers and developers to inspect chunking, run ad-hoc evaluations, test avatar video generation, and examine prompt payloads.

---

## 20. Complete REST API Reference
*Source: `server.py`*

| Method | Endpoint | Description | Payload / Parameters |
|:---|:---|:---|:---|
| `GET` | `/` | Serves Primary Modern Web SPA | None |
| `POST` | `/api/upload` | Ingests uploaded PDF/DOCX/PPTX/TXT files | Multipart file uploads |
| `GET` | `/api/sample-files` | Retrieves bundled NCERT/CBSE sample chapters | None |
| `POST` | `/api/plan` | Generates personalized, citation-grounded lesson plan | `{ topic, instruction, upload_paths, language, student }` |
| `POST` | `/api/session/start` | Initializes state machine for a session | `{ session_id, language }` |
| `POST` | `/api/session/explain` | Generates segment explanation, audio, and avatar video | `{ session_id, segment_index, render_video }` |
| `POST` | `/api/session/ask` | Answers student-initiated follow-up doubt without state loss | `{ session_id, segment_index, question }` |
| `GET` | `/api/session/video-status/{session_id}/{segment_index}` | Polls video compositing status (`rendering` / `ready`) | Path parameters |
| `POST` | `/api/session/answer` | Evaluates student answer & fingerprints misconceptions | `{ session_id, segment_index, answer, student }` |
| `POST` | `/api/session/adapt` | Triggers pedagogical re-explanation with new analogy | `{ session_id, segment_index, render_video }` |
| `POST` | `/api/session/language` | Switches lesson language mid-session | `{ session_id, language }` |
| `POST` | `/api/quiz/generate` | Generates quiz from taught concepts | `{ session_id }` |
| `POST` | `/api/quiz/submit` | Submits answers, grades quiz, saves report | `{ session_id, answers, student }` |
| `GET` | `/api/profile/{student}` | Retrieves historical learning progress | Path parameter |
| `GET` | `/api/knowledge-graph/{student}` | Fetches prerequisite knowledge graph nodes & edges | Path parameter |
| `GET` | `/api/student/dna/{student}` | Computes 5D Learning DNA cognitive metrics | Path parameter |
| `GET` | `/api/spaced-repetition/{student}` | Returns SM-2 review queue & retention decay items | Path parameter |
| `GET` | `/api/teacher/class-overview` | Class-wide mastery, misconceptions & struggling alerts | None |
| `GET` | `/api/3d/model` | Fetches Three.js WebGL scene specification | `?concept=dna` / `bohr` / `motor` |
| `POST` | `/api/3d/generate` | Generates 3D model spec from natural language query | `{ query }` |

---

## 21. Verification & Automated Test Suite
*Source: `scripts/`*

The platform includes a comprehensive, deterministic verification suite:
- `scripts/test_server_api.py`: Validates all REST API endpoints end-to-end (index, upload, planner, explain, evaluate, adapt, quiz, profiles).
- `scripts/test_followup_ask.py`: Validates student follow-up doubt endpoint (`/api/session/ask`), RAG grounding, audio synthesis, and strict state preservation.
- `scripts/test_12_languages_tts.py`: Spot-checks neural audio synthesis and fallback across all 12 Indian languages.
- `scripts/test_llm_cascade.py`: Tests tri-tier LLM cascade (Groq -> NVIDIA NIM -> Gemini -> deterministic offline mock engine).
- `scripts/test_3d_generator.py`: Verifies natural-language-to-3D scene generation across arbitrary scientific queries.
- `scripts/test_intelligence_layers.py`: Verifies live student data reflection in Knowledge Graph, Learning DNA, Spaced Repetition, and Teacher Dashboard.
- `scripts/test_day1.py`: Ingestion, chunking, MiniLM embeddings, and citation tracking verification.
- `scripts/test_day2.py`: Teaching state machine loop, misconception detection, multilingual rendering, and avatar generation.
- `scripts/test_day3.py`: Formative assessment, grading rubric, SQLite persistence, and next-topic recommendation.
- `scripts/test_bharatguru.py`: Enterprise integration test verifying all 18 pedagogical features.

---

*Authored for BHARATGURU — The Adaptive Multilingual AI Learning System.*
