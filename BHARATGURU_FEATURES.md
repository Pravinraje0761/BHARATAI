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
19. [Dual Frontend Interfaces & Authentication Architecture](#19-dual-frontend-interfaces--authentication-architecture)
20. [Complete REST API Reference](#20-complete-rest-api-reference)
21. [Verification & Automated Test Suite](#21-verification--automated-test-suite)
22. [Lesson Completion Celebration & Official Certificate](#22-lesson-completion-celebration--official-certificate)
23. [Credit-Based Realistic Teacher Studio (Express vs. Ultra Realistic)](#23-credit-based-realistic-teacher-studio-express-vs-ultra-realistic)
24. [Lockstep Video & Audio Synchronization Architecture](#24-lockstep-video--audio-synchronization-architecture)
25. [Clean Slate Policy & Demo Data Isolation](#25-clean-slate-policy--demo-data-isolation)

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
     - Leverages ultra-fast LPU inference (Groq OpenAI-compatible endpoint) using `qwen/qwen3.8-27b` (`config.GROQ_MODEL`), with `openai/gpt-oss-20b` and `groq/compound-mini` as in-tier fallbacks. Groq's free-tier model lineup rotates fairly often — if these 404 for a given key, check `GET {GROQ_BASE_URL}/models` to see what that key currently has access to.
  2. **Tier 2: NVIDIA NIM (High-Performance GPU Inference)**:
     - Cloud GPU inference using `meta/llama-3.2-11b-vision-instruct` (`config.NVIDIA_MODEL`).
  3. **Tier 3: Google Gemini API**:
     - Direct multimodal integration via `google-generativeai` (`gemini-flash-latest`, `config.GEMINI_MODEL` — a rolling alias, chosen over a dated snapshot so it doesn't silently go stale when Google retires a specific model version).
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
  - Integrated directly into the web UI via Three.js with orbit controls, pan, zoom, custom lighting, and responsive viewport sizing.
- **Pre-Built Curated Scientific Models**:
  - **Human Eye (Anatomy & Optics of Vision)**: Anatomical 3/4 cutaway sclera shell, crystal-clear refractive cornea dome, pigmented azure iris with radial striations, pupil aperture, crystalline biconvex lens with flattening accommodation geometry, ciliary body ring with suspensory zonular ligaments, posterior sensory retina with yellow Fovea Centralis, myelinated optic nerve bundle, and animated multi-segment light rays converging to a focal point on the retina.
  - **DNA Double Helix**: Intertwined helical sugar-phosphate strands, purine-pyrimidine base pairs with color-coded hydrogen bonds.
  - **Bohr Atom Model**: Quantum nucleus cluster of protons and neutrons orbited by electrons in discrete quantized K and L energy levels.
  - **Electric Motor & Lorentz Force**: Dual magnetic poles (N/S), rotating rectangular wire armature, split-ring commutator, and magnetic flux field lines.
  - **Water Molecule ($H_2O$) & Dipole**: Bent geometry with 104.5° bond angle and polar covalent bond vectors.
  - **Methane Molecule ($CH_4$)**: Symmetrical sp³ regular tetrahedral geometry with 109.5° bond angles.
  - **Mitochondrion**: Double-membrane organelle with deep inner cristae folds and ATP synthase complexes.
  - **Neuron Cell**: Soma body, branching dendrites, myelinated axon with Nodes of Ranvier, and synaptic terminal knob.
  - **Inner Solar System**: Central Sun with Keplerian orbital paths for Mercury, Venus, Earth with Moon, and Mars.
  - **Human Heart**: Four chambers (LV, RV, LA, RA), thick muscular myocardium, systemic aortic arch, and pulmonary artery.
  - **Plant Cell**: Cellulose cell wall, large central sap vacuole, nucleus, and photosynthetic thylakoid chloroplasts.
  - **Glass Prism & Dispersion**: Refractive glass prism dispersing white light into the continuous VIBGYOR visible spectrum.
- **Natural Language-to-3D Generator (`/api/3d/generate`)**:
  - Fast-matches curated science presets or synthesizes procedural 3D scenes for novel student queries with domain-specific components, color schemes, and interactive annotations.
  - **Smart Offline Synthesizer**: Automatically generates structurally accurate 3D models (anatomy, chemistry, optics, electromagnetism) when cloud LLMs are rate-limited or offline — guaranteeing zero generic water fallbacks.
- **Dynamic Pedagogical Reflection Synchronization**:
  - Synchronizes an educational concept reflection card for every rendered model, explaining the core physical or biological principles in depth.

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

- **Five-Dimensional Cognitive Metrics** (`LearningDNAProfile`, `src/learning_dna.py`):
  1. **Visual Affinity** (`visual_affinity`): Engagement ratio with 3D models/slides vs. text/audio narration.
  2. **Example-Driven** (`example_driven`): Preference for worked examples and analogies over abstract theory.
  3. **Conceptual Depth** (`conceptual_depth`): Ratio of theoretical understanding to formulaic calculation skill.
  4. **Recall Retention** (`recall_retention`): Empirical score tracking recall stability across recurring concepts.
  5. **Socratic Engagement** (`socratic_engagement`): Responsiveness to guided-question vs. direct-answer teaching.
  - Each dimension is scored 0–100%, with a computed `dominant_trait` and `personalized_insight`. Students with no session history yet receive an explicit empty profile (all-zero, "Not enough learning activity yet") rather than synthesized placeholder numbers.
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
*Source: `src/teacher_dashboard.py`, `server.py`*

- **Classroom Intervention Insights**:
  - Aggregates individual learner telemetry across an entire classroom or cohort to assist educators with targeted pedagogical intervention.
- **Key Administrative Features**:
  - **Cohort Mastery Heatmap**: Overview of concept proficiency across all enrolled students, highlighting high-risk and low-retention topics.
  - **Class-Wide Misconception Distribution**: Radar visualizer identifying common cognitive pitfalls across the class (e.g., "65% of Class 10-A inverted current vs. resistance").
  - **At-Risk Student Alerts**: Automatically flags learners requiring human teacher intervention.
  - **Enrolled Student Roster (`GET /api/teacher/students-roster`)**: Displays student profiles, learning boards, mastery scores, and urgency badges (`HIGH_RISK`, `NEEDS_REVIEW`, `ON_TRACK`).
- **Personalized "How to Teach Them" Pedagogical Blueprint Engine (`GET /api/teacher/student-guidance/{student}`)**:
  - Empirically analyzes each student's Learning DNA, tracked misconceptions, and accuracy history to generate an individual teaching blueprint for the human instructor:
    - **Optimal Teaching Mode**: (e.g., `ANALOGY_FIRST`, `SOCRATIC_DISCOVERY`, `FIRST_PRINCIPLES`, `VISUAL_DECONSTRUCTION`).
    - **Recommended Action**: (e.g., *"Launch 5-min Socratic intervention on Electric Current"*).
    - **Actionable Instructional Tips**: Direct teacher cues extracted from the student's cognitive model (e.g., *"Use the Water Pipe Analogy: Voltage is water pressure at the tap, Current is the flow rate, Resistance is pipe narrowing"*).
- **Strict Role-Based Security**:
  - All institutional teacher endpoints (`/api/teacher/class-overview`, `/api/teacher/students-roster`, `/api/teacher/student-guidance/{student}`) enforce token-based role verification and return `403 Forbidden` if invoked by student accounts.

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

## 19. Dual Frontend Interfaces & Authentication Architecture

### A. Primary Modern Stitch Web SPA (FastAPI + HTML5/Canvas/Three.js)
*Source: `static/index.html`, `static/app.js`, `static/styles.css`*
- **Google Stitch Design System**: Light navy-and-saffron Bharat theme (`--surface: #f8f9ff`, `--primary: #002045`), high-contrast, accessibility-compliant typography, glassmorphic cards, and smooth CSS view transitions (`view-enter`). A dedicated `body.high-contrast` mode is available via the accessibility toolbar.
- **Integrated Learning Suite**:
  - Real-time video/audio narration player with instant streaming fallback.
  - Live interactive 3D WebGL laboratory canvas (`three_lab.js`).
  - Interactive Student Knowledge Graph visualizer (`knowledge_graph.js`).
  - Student Learning DNA radar chart.
  - Credit Balance Badge (`🪙 100 Credits`) with micro-animations.
  - Real-time speech rate adjustment (0.75x to 1.5x).
  - Multi-step Lesson Planning progress modal with 4 real-time animated phases (`Ingesting & Grounding`, `Cognitive Diagnostics`, `Socratic Milestones`, `3D STEM Lab Synthesis`).
  - Quick-preset learning modes: 🏏 Cricket Analogy, 🎓 Professor Style, ⚡ 5-Minute Blitz, 🏛️ Socratic Guide, 🇮🇳 Tanglish.
- **Accessibility Suite**:
  - OpenDyslexic typeface toggle for neurodivergent learners.
  - High-contrast visual mode.
  - Audio speed pacing control.

### B. Dual Authentication System & Role-Based Portals
*Source: `src/auth.py`, `src/firebase_backend.py`, `static/login.html`, `static/login.js`*
- **100% Free SQLite Authentication**:
  - Salted PBKDF2 password hashing (100,000 iterations with SHA-256).
  - Bearer token session manager with automatic token expiry and revocation.
  - Zero external cloud/SaaS billing dependencies required to run local or self-hosted instances.
- **Dual Firebase Authentication Bridge**:
  - Client-side Firebase Web SDK integration with Google Sign-In button.
  - Token relay verification (`/api/firebase/verify-token`) with seamless fallback to local session tokens.
- **Dual Dedicated Portals**:
  - **Student Portal**: Student-tailored login/registration with Board/Grade selection (CBSE Class 10/11/12, ICSE, JEE/NEET).
  - **Educator / Teacher Portal**: Faculty-tailored login/registration with Department/Specialization selection.
- **1-Click Instant Demo Logins**:
  - 👨‍🎓 **Demo Student** (`aarav` - Aarav Patel, CBSE Class 10).
  - 👩‍🏫 **Demo Teacher** (`priya` - Dr. Priya Sharma, Senior Physics Faculty).
- **In-App 1-Click Role Switcher**:
  - Navigation bar button (`⇄ Switch to Teacher` / `⇄ Switch to Student`) enabling evaluators and teachers to swap perspectives instantly without re-entering credentials.
- **Strict Role-Based UI Isolation**:
  - Student View strictly hides institutional analytics, student rosters, and pedagogical guidance.
  - Teacher View unlocks cohort diagnostics, risk heatmaps, and individual instructional blueprints.

### C. Secondary Streamlit Dashboard
*Source: `app.py`*
- Rapid prototyping and inspection interface allowing teachers and developers to inspect chunking, run ad-hoc evaluations, test avatar video generation, and examine prompt payloads.

---

## 20. Complete REST API Reference
*Source: `server.py`*

| Method | Endpoint | Description | Payload / Parameters |
|:---|:---|:---|:---|
| `GET` | `/` | Serves Primary Modern Web SPA (static mount) | None |
| `GET` | `/login`, `/login.html` | Serves dedicated Login & Registration page | None |
| `GET` | `/api/health` | Liveness probe | None |
| `GET` | `/api/backend/status` | Reports which LLM tier / TTS backend is currently active | None |
| `POST` | `/api/upload` | Ingests uploaded PDF/DOCX/PPTX/TXT files | Multipart file uploads |
| `GET` | `/api/sample-files` | Retrieves bundled NCERT/CBSE sample chapters | None |
| `GET` | `/api/languages` | Lists the 12 supported languages & voice codes | None |
| `GET` | `/api/presets` | Lists "Teach Me Like..." style presets | None |
| `POST` | `/api/auth/register` | Registers new student or teacher account | `{ username, password, full_name, role, grade_or_board }` |
| `POST` | `/api/auth/login` | Authenticates with username/password | `{ username, password }` |
| `POST` | `/api/auth/demo-login` | 1-Click instant login as Demo Student or Teacher | `{ role: "student" \| "teacher" }` |
| `GET` | `/api/auth/me` | Validates session token & returns user profile | `Authorization: Bearer <token>` |
| `POST` | `/api/auth/logout` | Revokes active user session token | `Authorization: Bearer <token>` |
| `PUT` | `/api/auth/profile` | Updates the signed-in user's profile fields | `Authorization: Bearer <token>` |
| `GET` | `/api/firebase/config` | Returns client-side Firebase web configuration | None |
| `GET` | `/api/firebase/status` | Reports whether Firebase Admin verification is configured | None |
| `POST` | `/api/auth/firebase-login` | Verifies a Google Firebase ID token and issues a local session | `{ id_token, role, full_name, email }` |
| `POST` | `/api/firebase/sync` | Syncs a Firebase-authenticated profile into the local store | `Authorization: Bearer <token>` |
| `POST` | `/api/plan` | Generates a citation-grounded lesson plan **and initializes the teaching session** | `{ topic, instruction, upload_paths, language, student, production_tier }` |
| `POST` | `/api/session/explain` | Generates segment explanation, audio, and avatar video | `{ session_id, segment_index, render_video, production_tier }` |
| `POST` | `/api/session/ask` | Answers student-initiated follow-up doubt without state loss | `{ session_id, segment_index, question }` |
| `POST` | `/api/session/socratic` | Advances a Socratic-mode guided-question dialogue turn | `{ session_id, segment_index, student_reply }` |
| `GET` | `/api/session/video-status/{session_id}/{segment_index}` | Polls video compositing status (`rendering` / `ready`) | Path parameters |
| `POST` | `/api/session/answer` | Evaluates student answer & fingerprints misconceptions | `{ session_id, segment_index, answer, student }` |
| `POST` | `/api/session/adapt` | Triggers pedagogical re-explanation with new analogy | `{ session_id, segment_index, render_video }` |
| `POST` | `/api/session/advance` | Advances state machine to next segment or marks end | `{ session_id }` |
| `GET` | `/api/session/complete/{session_id}` | Retrieves final lesson completion & certificate metadata | Path parameter |
| `POST` | `/api/session/language` | Switches lesson language mid-session | `{ session_id, language }` |
| `GET` | `/api/session/{session_id}/notes` | Returns a printable revision-notes summary of the session | Path parameter |
| `POST` | `/api/quiz/generate` | Generates quiz from taught concepts | `{ session_id }` |
| `POST` | `/api/quiz/submit` | Submits answers, grades quiz, saves report | `{ session_id, answers, student }` |
| `GET` | `/api/profile/{student}` | Retrieves historical learning progress | Path parameter |
| `GET` | `/api/knowledge-graph/{student}` | Fetches prerequisite knowledge graph nodes & edges | Path parameter |
| `GET` | `/api/student/dna/{student}` | Computes 5D Learning DNA cognitive metrics | Path parameter |
| `GET` | `/api/spaced-repetition/{student}` | Returns SM-2 review queue & retention decay items | Path parameter |
| `GET` | `/api/teacher/class-overview` | Class-wide mastery, misconceptions & struggling alerts | `Authorization: Bearer <teacher_token>` |
| `GET` | `/api/teacher/students-roster` | List of enrolled students, boards & risk classifications | `Authorization: Bearer <teacher_token>` |
| `GET` | `/api/teacher/student-guidance/{student}` | Individual pedagogical guidance & "How to Teach Them" blueprint | `Authorization: Bearer <teacher_token>` |
| `GET` | `/api/3d/model` | Fetches Three.js WebGL scene specification | `?concept=dna` / `bohr` / `motor` |
| `POST` | `/api/3d/generate` | Generates 3D model spec from natural language query | `{ query }` |

> Note: there is no separate `/api/session/start` route — `POST /api/plan` both plans the lesson and initializes the `TeachingSession` state machine in one call.

---

## 21. Verification & Automated Test Suite
*Source: `scripts/`*

The platform includes a comprehensive, deterministic verification suite:
- `scripts/test_credits_and_clean_state.py`: Validates credit deduction (Express: 1 Credit, Realistic Studio: 5 Credits), HTML credit badges, tier metadata passing, and demo account isolation.
- `scripts/test_role_isolation.py`: Validates 403 Forbidden role protections on teacher endpoints, student roster queries, and "How to Teach Them" personalized pedagogical blueprints.
- `scripts/test_completion_flow.py`: Validates segment advancement to the final milestone, celebratory completion metadata retrieval (`/api/session/complete/{id}`), quiz generation, and grading.
- `scripts/test_server_api.py`: Validates all core REST API endpoints end-to-end (upload, planner, explain, evaluate, adapt, quiz, profiles).
- `scripts/test_followup_ask.py`: Validates student follow-up doubt endpoint (`/api/session/ask`), RAG grounding, audio synthesis, and strict state preservation.
- `scripts/test_12_languages_tts.py`: Spot-checks neural audio synthesis and fallback across all 12 Indian languages.
- `scripts/test_llm_cascade.py`: Tests tri-tier LLM cascade (Groq -> NVIDIA NIM -> Gemini -> deterministic offline mock engine).
- `scripts/test_3d_generator.py`: Verifies natural-language-to-3D scene generation across arbitrary scientific queries.
- `scripts/test_intelligence_layers.py`: Verifies live student data reflection in Knowledge Graph, Learning DNA, Spaced Repetition, and Teacher Dashboard.
- `scripts/test_day1.py`: Ingestion, chunking, MiniLM embeddings, and citation tracking verification.
- `scripts/test_day2.py`: Teaching state machine loop, misconception detection, multilingual rendering, and avatar generation.
- `scripts/test_day3.py`: Formative assessment, grading rubric, SQLite persistence, and next-topic recommendation.
- `scripts/test_bharatguru.py`: Enterprise integration test suite (its own docstring calls it "19 architectural pillars"; the script currently enumerates 9 of them).
- `scripts/test_auth.py`: Validates local SQLite registration, login, PBKDF2 hashing, and session token lifecycle.
- `scripts/test_firebase.py`: Validates Firebase config/status endpoints and the `/api/auth/firebase-login` token relay.
- `scripts/test_pdf_ingestion.py`: Validates PDF-specific chunking and page-number citation mapping.

---

## 22. Lesson Completion Celebration & Official Certificate
*Source: `static/index.html`, `static/app.js`, `server.py`*

- **Automated Milestone Trigger**:
  - When the student successfully advances past the final concept segment, the classroom advance button transforms into `🎉 Complete Lesson & Claim Certificate` with glowing gradient styling.
  - Triggers transition to `#view-lesson-completed` and queries `/api/session/complete/{session_id}`.
- **Confetti Particle Engine**:
  - Lightweight HTML5 `<canvas id="completion-confetti-canvas">` animating 85 fluttering particles in Indian national colors (Saffron `#fe9832`, Emerald `#003e29`, Bharat Navy `#002045`, and Gold `#ffd700`) for 5+ seconds before settling.
- **Bouncing Trophy Hero & Milestone Banner**:
  - Celebratory hero header with bouncing 3D trophy icon and completion banner (`100% Milestones Conquered`).
- **4-Card Mastery Scoreboard**:
  - **Lessons Finished**: e.g., `5 / 5 (100% Milestones Conquered)`.
  - **Concept Mastery Index**: Live score synced directly with the student's synaptic Knowledge Graph.
  - **Checkpoint Accuracy**: Running tally of correct responses and active learning streak.
  - **Retention Status**: Confirms all concepts are indexed in the Ebbinghaus Spaced Repetition queue.
- **Conquered Concepts & Analogies Grid**:
  - Interactive grid displaying each concept taught, the anchor analogy learned, verified citation badges, and a 1-click **Inspect in 3D Lab** button.
- **Official Bharat Academix Certificate of Achievement**:
  - Double ornamental navy & gold borders, embossed seal (`certificate-seal`), background emblem watermark, student full name, lesson title, exam board, language, issue date, and unique verification token (`BG-CERT-[SessionId]`).
  - High-resolution `@media print` CSS optimization for border-to-border A4 printing and clean PDF export without browser chrome.
- **Retention Loop & Next Steps**:
  - 1-click launch buttons for Formative Mastery Quiz, Spaced Repetition Flashcards, Knowledge Graph, and Printable Revision Sheet.
  - **Recommended Next Lesson**: Surfaces the next sequential syllabus milestone from `ProfileStore` with a 1-click **Start Next Lesson 🚀** button.

---

## 23. Credit-Based Realistic Teacher Studio (Express vs. Ultra Realistic)
*Source: `static/index.html`, `static/app.js`, `server.py`*

- **Persistent Credit Balance**:
  - Prominently displayed in the top header toolbar: `🪙 100 Credits`.
  - Stored persistently in `localStorage.getItem('bharat_credits')`.
- **Selectable Production Tiers in Planning View**:
  - **⚡ Fast & Express Mode (1 Credit)**: Fast neural audio synthesis + dynamic concept diagram slides (~3 seconds).
  - **✨ Ultra Realistic Studio Mode (5 Credits)**: Realistic human teacher video avatar, 3D STEM interactive lab, and cinematic pedagogical pacing (~15 seconds).
  - Enforces credit balance validation prior to lesson building, deducting the respective credits on successful plan generation.
- **In-Classroom 1-Click Upgrade Button**:
  - `#btn-upgrade-realistic-studio`: Located in the live classroom header.
  - Allows students to upgrade mid-lesson to Ultra Realistic Studio for 5 credits with a confirmation modal, deducting credits and immediately re-synthesizing the current concept with 1080p realistic teacher avatar media.
- **Backend Tier Synchronization**:
  - `PlanRequest` and `ExplainRequest` accept `production_tier` (`"express"` or `"realistic"`), persisting tier preference in active session state and returning `credits_cost` and `is_realistic_studio` metadata.

---

## 24. Lockstep Video & Audio Synchronization Architecture
*Source: `static/app.js`*

- **Problem Addressed**:
  - Previously, when `<video id="classroom-video">` was paused by the user, the underlying `<audio id="classroom-audio">` narration continued streaming in the background, creating audio leaks and double-voice echo on resume.
- **Bi-Directional Event Synchronization**:
  - `video.onpause`: Halts `classroom-audio` and doubt audio immediately and hides the audio visualizer.
  - `video.onplay`: Pauses standalone audio to prevent dual voice playback, syncing the visualizer.
  - `video.onseeking`: Synchronizes `audio.currentTime = video.currentTime`.
  - `video.onended`: Halts audio and resets visualizer animations.
  - `video.onratechange`: Synchronizes `audio.playbackRate = video.playbackRate`.
- **Clean Media Handoff**:
  - In `loadSegment()` and `pollVideoReady()`, when video is ready, any active background standalone audio is cleanly paused and reset (`audio.pause(); audio.currentTime = 0;`) before video playback begins.

---

## 25. Clean Slate Policy & Demo Data Isolation
*Source: `static/index.html`, `static/app.js`, `static/login.js`, `static/knowledge_graph.js`*

- **Clean Slate Policy for Fresh Visitors & Standard Accounts**:
  - All input fields (`#topic-input`, `#instruction-input`, `#student-name-input`) start completely empty with clear placeholders.
  - Uploaded materials container starts blank (`AppState.uploadedFiles = []`).
  - **Knowledge Graph Tab**: Renders an uninitialized canvas watermark with `--%` overall mastery and `0 / 0` concepts until a chapter document is uploaded.
  - **Learning DNA Tab**: Renders an uncalibrated cognitive DNA empty state card guiding the user to complete their first lesson.
  - **Spaced Repetition Tab**: Renders an inactive review schedule empty state card.
  - **Dynamic Adaptation**: As soon as a user uploads a document or notes, all tabs dynamically adapt and populate based on that specific uploaded chapter.
- **Preloaded Demos Exclusively for Demo Logins**:
  - **👨‍🎓 Demo Student (`aarav` / `student_demo`)**: Automatically preloads the CBSE Class 10 Electricity chapter (`sample_electricity_cbse.pdf`, 12 pages, 18 chunks grounded), pre-populates topic and instructions, loads the 82% concept knowledge graph, and activates 3 Ebbinghaus review cards.
  - **👩‍🏫 Demo Teacher (`priya` / `teacher_demo`)**: Automatically loads full class cohort diagnostics, risk heatmap, shared misconceptions, and teacher guidance blueprints.

---

*Authored for BHARATGURU — The Adaptive Multilingual AI Learning System.*

