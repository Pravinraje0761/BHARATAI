# 🎓 BHARATGURU — Adaptive Multilingual AI Learning System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Three.js](https://img.shields.io/badge/3D%20Engine-Three.js%20WebGL-black.svg)](https://threejs.org/)
[![Tailwind CSS](https://img.shields.io/badge/UI-Tailwind%20CSS-38bdf8.svg)](https://tailwindcss.com/)
[![Gemini 2.5](https://img.shields.io/badge/LLM-Google%20Gemini%20%7C%20Groq%20%7C%20NVIDIA-orange.svg)](https://aistudio.google.com/)
[![Indic Languages](https://img.shields.io/badge/Languages-12%20Indian%20Languages-green.svg)](#10-12-indian-languages--multilingual-neural-voice)
[![CPU Video](https://img.shields.io/badge/Avatar-Zero%20GPU%20Lip--Sync-purple.svg)](#11-pure-cpu-amplitude-driven-avatar--video-compositing)

> **BHARATGURU (AI Teacher)** is an enterprise-grade, autonomous pedagogical AI learning platform engineered specifically for Indian learners. It takes uploaded curriculum documents (PDF, DOCX, PPTX, TXT, MD) or a raw syllabus topic, builds a structured adaptive lesson plan, and teaches it segment-by-segment using an amplitude-driven lip-synced avatar and neural voice.
>
> As the student learns, BHARATGURU questions them, **fingerprints cognitive misconceptions**, dynamically shifts teaching strategies, anchors explanations in familiar **Indian cultural metaphors**, checks citations with a **Hallucination Shield**, visualizes complex STEM concepts in an **interactive Three.js 3D Lab**, tracks cognitive mastery on a **Student Knowledge Graph**, computes an empirical **Learning DNA profile**, schedules reviews via **Ebbinghaus Spaced Repetition**, and equips educators with an **Institutional Teacher Dashboard**.

---

## 📑 Table of Contents

1. [Architectural Overview & Philosophy](#-architectural-overview--philosophy)
2. [Exhaustive Feature Breakdown](#-exhaustive-feature-breakdown)
   - [1. Multi-Format Document Ingestion & Chunking](#1-multi-format-document-ingestion--chunking)
   - [2. Hybrid RAG Engine (Dense Semantic + Sparse BM25 + RRF)](#2-hybrid-rag-engine-dense-semantic--sparse-bm25--rrf)
   - [3. Multi-Tiered Cascading LLM Engine & Offline Mock](#3-multi-tiered-cascading-llm-engine--offline-mock)
   - [4. Bharat Context Engine™ (Indian Cultural & Real-World Anchors)](#4-bharat-context-engine-indian-cultural--real-world-anchors)
   - [5. Hallucination Shield & Citation Grounding Verifier](#5-hallucination-shield--citation-grounding-verifier)
   - [6. Misconception Engine™ & Cognitive Fingerprinter](#6-misconception-engine--cognitive-fingerprinter)
   - [7. Adaptive Pedagogy Policy Selector](#7-adaptive-pedagogy-policy-selector)
   - [8. Socratic Dialogue Engine](#8-socratic-dialogue-engine)
   - [9. Pedagogical State Machine Loop & Dynamic Difficulty](#9-pedagogical-state-machine-loop--dynamic-difficulty)
   - [10. 12 Indian Languages & Multilingual Neural Voice](#10-12-indian-languages--multilingual-neural-voice)
   - [11. Pure-CPU Amplitude-Driven Avatar & Video Compositing](#11-pure-cpu-amplitude-driven-avatar--video-compositing)
   - [12. Bharat 3D Lab™ — Universal WebGL Science Visualizer](#12-bharat-3d-lab--universal-webgl-science-visualizer)
   - [13. Student Knowledge Graph & Prerequisite Dependency Engine](#13-student-knowledge-graph--prerequisite-dependency-engine)
   - [14. Learning DNA Profiler (5-Dimensional Cognitive Spectrum)](#14-learning-dna-profiler-5-dimensional-cognitive-spectrum)
   - [15. Cognitive Spaced Repetition Retention Engine (SM-2)](#15-cognitive-spaced-repetition-retention-engine-sm-2)
   - [16. Institutional Teacher Dashboard & Class Intervention Engine](#16-institutional-teacher-dashboard--class-intervention-engine)
   - [17. Formative Assessment, Automated Grading & Diagnostic Report Cards](#17-formative-assessment-automated-grading--diagnostic-report-cards)
   - [18. Cross-Session Profile Store & AI Next-Topic Recommender](#18-cross-session-profile-store--ai-next-topic-recommender)
   - [19. Dual User Interface Ecosystem](#19-dual-user-interface-ecosystem)
     - [A. Primary Modern Stitch Web SPA (FastAPI + HTML5/Canvas/Three.js)](#a-primary-modern-stitch-web-spa)
     - [B. Secondary Streamlit Dashboard](#b-secondary-streamlit-dashboard)
   - [20. Inclusive Accessibility Suite](#20-inclusive-accessibility-suite)
   - [21. Comprehensive Verification & Testing Suite](#21-comprehensive-verification--testing-suite)
3. [System Architecture Diagram](#-system-architecture-diagram)
4. [Complete Project File Manifest](#-complete-project-file-manifest)
5. [Complete REST API Specification](#-complete-rest-api-specification)
6. [Installation & Quickstart Guide](#-installation--quickstart-guide)
7. [Environment Variables & Configuration](#-environment-variables--configuration)

---

## 🏛 Architectural Overview & Philosophy

Traditional ed-tech delivers static videos or generic chatbots that regurgitate text. **BHARATGURU** operates on six core pedagogical pillars:

1. **Active Checking, Not Passive Streaming**: The system never lectures uninterrupted. Every segment (60–95 words) halts for a conceptual checkpoint question.
2. **Cognitive Root-Cause Diagnosis**: When a student fails a question, the platform identifies *why* they failed (misconception fingerprinting) rather than just stating "incorrect".
3. **Dynamic Pedagogical Shifts**: If a student is confused by an analogy, repeating the same explanation fails. The system shifts to worked calculations, visual deconstruction, counterexamples, or Socratic inquiry.
4. **Cultural Grounding (Bharat Metaphors)**: Science concepts are mapped to Indian experiences (cricket ball impact, Mumbai local trains, ISRO rocket stages, Kirana stores, Rupee ₹ currency) rather than Western tropes.
5. **Zero-GPU Accessible Architecture**: Lip-synced avatar video runs entirely on CPU via RMS audio envelopes and PIL/OpenCV, eliminating expensive CUDA hardware barriers.
6. **Zero-Failure Resilience**: High-speed Groq LPU + NVIDIA NIM + Gemini cascading failover, backed by a deterministic offline pedagogical engine for 100% reliability.

---

## 🚀 Exhaustive Feature Breakdown

### 1. Multi-Format Document Ingestion & Chunking
*Implementation: `src/ingestion.py`*
- **Universal Multi-Format Parser**: Directly ingests `.pdf`, `.docx`, `.pptx`, `.txt`, and `.md` files without external SaaS parsers.
  - **PDF Parser (`pypdf`)**: Extracts text per physical page with page-number metadata (`p.1`, `p.2`, etc.).
  - **Word DOCX Parser (`python-docx`)**: Identifies heading hierarchies (`Heading 1`, `Heading 2`) and structures text into clean numbered sections (`section 1`, `section 2`).
  - **PowerPoint PPTX Parser (`python-pptx`)**: Traverses slide shapes, extracts text frames, and preserves slide boundaries (`slide 1`, `slide 2`).
  - **Plaintext & Markdown Parser**: Detects chapter/unit/lesson patterns with regex and preserves block structure.
- **Context-Aware Semantic Chunking**:
  - Implements word-bounded chunk packing (configurable via `config.CHUNK_MIN_WORDS = 220` and `config.CHUNK_MAX_WORDS = 480`).
  - Strict paragraph and sentence boundary splitting (`_split_units`) avoids mid-sentence truncation.
- **Permanent Citation Tagging**: Every chunk retains `doc_name`, `source_page`, and `source_label` (`[notes.pdf p.4]`). Metadata is permanently attached and threaded into prompt context blocks and UI modals.

---

### 2. Hybrid RAG Engine (Dense Semantic + Sparse BM25 + RRF)
*Implementation: `src/hybrid_rag.py`, `src/retrieval.py`*
- **Dense Semantic Embeddings**:
  - Uses `sentence-transformers/all-MiniLM-L6-v2` locally to project document text into 384-dimensional unit-normalized vector spaces.
  - Instant in-memory cosine ranking using matrix-vector multiplication (`_matrix @ q`), eliminating heavyweight vector DB service dependencies for lesson-scale corpora.
- **Sparse BM25 Keyword Search (`BM25Index`)**:
  - Built-in zero-dependency BM25 tokenizer and ranker.
  - Computes Term Frequency (TF) with document length normalization ($k_1 = 1.5, b = 0.75$) and Robertson-Spärck Jones Inverse Document Frequency (IDF).
- **Reciprocal Rank Fusion (RRF)**:
  - Fuses dense semantic vector ranks and sparse BM25 keyword ranks into a unified score using $RRF(d) = \sum \frac{1}{60 + r(d)}$.
  - Outperforms pure vector search on technical formulas, chemical notations, and exact chapter references.
- **Citation-Tagged Prompt Formatting**: `context_block()` produces structured, bracketed citation excerpts for the lesson planning agent and hallucination shield.

---

### 3. Multi-Tiered Cascading LLM Engine & Offline Mock
*Implementation: `src/llm.py`, `config.py`*
- **Multi-Provider LLM Cascade**:
  1. **Ultra-Fast LPU Tier (Groq)**: Sub-second (~0.9s) lightning generation using `qwen/qwen3.8-27b`, `groq/compound-mini`, or `openai/gpt-oss-20b`.
  2. **High-Performance GPU Tier (NVIDIA NIM)**: Cloud GPU inference using `meta/llama-3.2-11b-vision-instruct` and `meta/llama-3.1-70b-instruct`.
  3. **Cloud Reasoning Tier (Google Gemini)**: Deep reasoning via `gemini-2.5-flash` and `gemini-1.5-flash` using `google-generativeai`.
- **Automatic Fault Recovery**:
  - Automatically catches and bypasses HTTP 429 Quota Exceeded (rate limits) and HTTP 404 model deprecation errors.
  - Request timeouts (`_call_with_timeout`) prevent hanging requests.
- **Robust JSON Extraction**: `_extract_json()` strips markdown fences, extracts nested objects/arrays, and enforces schema compliance.
- **Deterministic Offline Pedagogical Engine (`LLM_MOCK=1`)**:
  - Full-featured offline fallback covering instruction parsing, curriculum planning, spoken explanations, few-shot grading, misconception fingerprinting, quiz creation, and report generation.
  - Guarantees 0% pipeline crashes even with zero internet or no API keys configured.

---

### 4. Bharat Context Engine™ (Indian Cultural & Real-World Anchors)
*Implementation: `src/bharat_context.py`*
- **Cultural Pedagogy Directives**: Automatically converts abstract Western STEM concepts into relatable Indian physical anchors:
  - Baseball / Football $\rightarrow$ 140 km/h Jasprit Bumrah leather cricket ball, Rohit Sharma cover drive, Kabaddi.
  - Subways / US Trains $\rightarrow$ Crowded Mumbai local train, AC Chennai Metro, yellow-line Delhi Metro, red BEST bus.
  - Supermarkets $\rightarrow$ Local neighborhood Kirana store, vegetable mandi.
  - Currency $\rightarrow$ Always Indian Rupees (₹), paise.
  - Snow / Blizzard $\rightarrow$ Heavy Western Ghats monsoon rainfall, Cherrapunji downpours.
  - Space Flight $\rightarrow$ ISRO Chandrayaan-3 lander, PSLV payload staging.
- **5 Regional Anchor Flavors**:
  - **Hindi**: Delhi Metro, Yamuna expressway, Gully cricket, Varanasi ghats.
  - **Tamil**: Chennai MRTS, Chepauk Stadium CSK match, Marina Beach, Nilgiris estates.
  - **Telugu**: Hyderabad Metro, Godavari rail bridge, Charminar market, Gymkhana grounds.
  - **Bengali**: Kolkata Tram, Howrah Ferry across Hooghly, Eden Gardens, Darjeeling tea slopes.
  - **Marathi**: Mumbai Local Train, Pune PMPML bus, Sahyadri ghat road curves, Wankhede stadium.
- **Automated Text Indianizer (`indianize_text`)**: Post-generation regex filter purging Western idioms and enforcing ₹ currency symbols.

---

### 5. Hallucination Shield & Citation Grounding Verifier
*Implementation: `src/hallucination_shield.py`*
- **Real-Time Claim Grounding**: Cross-references generated explanations against ingested document chunks using lexical term overlap and semantic containment.
- **Multi-Tiered Verification Status**:
  - `VERIFIED` ($\ge 45\%$ overlap): 100% faithful to uploaded text with zero conflicting claims.
  - `PARTIALLY_GROUNDED` ($\ge 25\%$ overlap): Core principles anchored in source text with supplementary analogies added.
  - `UNSUPPORTED`: Flagged when explanations drift into ungrounded external concepts.
  - `GENERAL_KNOWLEDGE`: Automatically assigned when teaching from a bare topic without document uploads.
- **Interactive UI Modal & Audit**: The web interface displays a real-time badge (`100% GROUNDED`) with an **Inspect Source** modal revealing the exact document name, page number, and verbatim passage snippet.

---

### 6. Misconception Engine™ & Cognitive Fingerprinter
*Implementation: `src/misconception_engine.py`*
- **Cognitive Diagnosis Beyond Right/Wrong**: Analyzes student errors to isolate flawed mental models, incomplete analogies, or false intuitions.
- **Curated High-Frequency STEM Misconception Knowledgebase**:
  - *Current Depletion Fallacy*: The belief that electric current is "consumed" or "drained" by lightbulbs (resolved via closed water-pipe loop, bicycle chain analogy, and ammeter proofs).
  - *Ohm's Law Proportionality Bias*: Believing current increases with resistance at fixed voltage (resolved via crowded hallway friction analogy and ratio calculation).
  - *Aristotelian Force Fallacy*: Believing steady motion requires continuous forward force (resolved via deep-space Voyager probe vacuum thought experiment).
  - *Gravitational Mass Fallacy*: Believing heavier objects fall faster in vacuum (resolved via Galileo Pisa derivation and Apollo 15 lunar hammer-feather drop).
- **LLM Cognitive Diagnosis Fallback**: Generalizes to any subject domain (chemistry, biology, mathematics, history) to produce:
  - Cognitive Root Cause description
  - Diagnosis Confidence score ($0.50 - 0.99$)
  - Prescribed Pedagogical Intervention
  - Concrete Illuminating Counterexample

---

### 7. Adaptive Pedagogy Policy Selector
*Implementation: `src/pedagogy.py`*
- **6 Dynamic Pedagogical Strategies**:
  1. `ANALOGY`: Introduces an intuitive physical scenario (water pressure, bicycle gears, traffic flow).
  2. `COUNTEREXAMPLE`: Presents an extreme boundary case that directly breaks the student's assumption.
  3. `WORKED_EXAMPLE`: Step-by-step mathematical calculation with clean numbers ($V=10\text{V}, R=2\Omega \implies I=5\text{A}$).
  4. `VISUAL_DECONSTRUCTION`: Spatial layer-by-layer anatomical walkthrough of the physical system.
  5. `SOCRATIC_QUESTIONING`: Refuses to reveal the answer; asks a leading question prompting self-discovery.
  6. `SIMPLIFIED_INTUITION`: Strips away all jargon, math, and formulas to explain the qualitative physical truth.
- **Automatic Policy Selection (`select_adaptive_strategy`)**:
  - 1st wrong answer $\rightarrow$ Counterexample or fresh physical analogy.
  - 2nd wrong answer $\rightarrow$ Step-by-step worked numerical calculation.
  - 3rd+ wrong answer $\rightarrow$ Zero-jargon simplified intuitive core.
  - Socratic mode $\rightarrow$ Guided inquiry dialogue.

---

### 8. Socratic Dialogue Engine
*Implementation: `src/pedagogy.py`, `server.py`*
- **Interactive Multi-Turn Inquiry (`socratic_dialogue_turn`)**:
  - Engages students in exploratory conversation instead of one-way lecturing.
  - Validates partial truths in student responses before posing a targeted guiding question.
  - Preserves dialogue history and responds in natural conversational tone within 2–3 sentences.

---

### 9. Pedagogical State Machine Loop & Dynamic Difficulty
*Implementation: `src/teaching.py`*
- **Deterministic 5-Stage Machine**: `EXPLAIN` $\rightarrow$ `QUESTION` $\rightarrow$ `EVALUATE` $\rightarrow$ `ADAPT` $\rightarrow$ `DONE`.
- **Checkpoint Question Generator**:
  - Alternates by segment index between 4-option MCQs and short-answer conceptual checks.
  - Tests genuine conceptual reasoning rather than rote keyword recall.
- **Few-Shot Formative Grader**:
  - Strict JSON evaluation returning `verdict` (`correct`, `partial`, `incorrect`), diagnosed `misconception`, and targeted `feedback`.
- **Dynamic Depth Bump & Streaks**:
  - Tracks consecutive correct answers (`_streak`).
  - Achieving 2 correct answers in a row triggers a **Depth Bump**, automatically injecting subtle edge cases, deeper mechanisms, and higher academic rigor into subsequent segments.
- **Complete Transition Logging**: Every step, score, timestamp, and adaptation decision is recorded in `session.log` for debugging and analytics.

---

### 10. 12 Indian Languages & Multilingual Neural Voice
*Implementation: `src/tts.py`, `config.py`*
- **12 Supported Indian Languages**:
  1. **English** (`en-US-AriaNeural`)
  2. **Hindi / हिन्दी** (`hi-IN-SwaraNeural`)
  3. **Hinglish** (Conversational Hindi in Latin script with English scientific terms)
  4. **Tamil / தமிழ்** (`ta-IN-PallaviNeural`)
  5. **Telugu / తెలుగు** (`te-IN-ShrutiNeural`)
  6. **Kannada / ಕನ್ನಡ** (`kn-IN-SapnaNeural`)
  7. **Malayalam / മലയാളം** (`ml-IN-SobhanaNeural`)
  8. **Bengali / বাংলা** (`bn-IN-TanishaaNeural`)
  9. **Marathi / मराठी** (`mr-IN-AarohiNeural`)
  10. **Gujarati / ગુજરાતી** (`gu-IN-DhwaniNeural`)
  11. **Punjabi / ਪੰਜਾਬੀ** (`pa-IN-GurpreetNeural`)
  12. **Odia / ଓଡ଼ିଆ** (`hi-IN-SwaraNeural`)
- **Native Script Directives**: Generates fluent text directly in native scripts (Devanagari, Tamil, Bengali, etc.) while preserving standard scientific formulas in Latin script.
- **Multi-Tier Audio Fallback**:
  1. High-fidelity neural voice synthesis via `edge-tts`.
  2. Graceful fallback to `gTTS` (`hi`/`en`).
  3. Automatic silent WAV placeholder sized to speaking pace ($0.35\text{s}$ per word) ensuring video rendering never fails offline.
- **Mid-Lesson Language Switching**: Switch languages mid-stream without resetting segment progress, test scores, or adaptation history.

---

### 11. Pure-CPU Amplitude-Driven Avatar & Video Compositing
*Implementation: `src/avatar.py`, `src/visuals.py`, `src/video.py`*
- **Zero-GPU Amplitude Mouth-Swap Avatar**:
  - Replaces heavy, GPU-dependent neural models (SadTalker) with a CPU-friendly solution.
  - Three distinct mouth states (`closed`, `half`, `open`).
  - Audio analysis via `librosa`: computes Root-Mean-Square (RMS) volume envelope, samples at video FPS (12 fps), thresholds into mouth states, and eliminates single-frame jitter.
- **Subject-Tinted Visual Slides (`render_slide`)**:
  - PIL-based slide generation with clean title and bullet-point hierarchy.
  - Keyword-driven theme tinting (Physics/Electricity: Navy `#1c2842`, Chemistry: Forest `#1e372c`, Biology: Plum `#2c2036`, History: Terracotta `#422e1c`, Math: Slate `#181818`).
- **Video Compositing & Subtitles**:
  - OpenCV renders a silent 720p MP4 featuring the slide, picture-in-picture framed avatar, and burned-in progressive captions.
  - Audio/video muxing via `ffmpeg` (automatically uses bundled `imageio-ffmpeg` binary if OS-level ffmpeg is not installed).
- **Full Lesson Concatenation**: `concat_videos()` stitches individual segment MP4s into a single downloadable master video.

---

### 12. Bharat 3D Lab™ — Universal WebGL Science Visualizer
*Implementation: `src/model_3d.py`, `static/three_lab.js`*
- **Interactive Three.js 3D WebGL Engine**:
  - OrbitControls: Drag to rotate, scroll to zoom, right-click to pan.
  - Studio directional and ambient lighting, auto-rotation toggle, and camera reset.
  - Raycaster-based interactive annotation pins: Click any element to highlight it and reveal conceptual descriptions.
- **8 Curated Procedural Science Models**:
  1. **DNA Double Helix**: 3-turn double helix, 36 base pairs (Adenine-Thymine with 2 H-bonds, Guanine-Cytosine with 3 H-bonds), sugar-phosphate backbones, interactive base pair color legend, and unwinding ladder mode.
  2. **Bohr Atomic Model (Carbon-12)**: Densely packed nucleus of 6 protons and 6 neutrons, K-Shell ($n=1$, 2 electrons), and L-Shell ($n=2$, 4 valence electrons) orbiting in tilted quantized planes.
  3. **DC Electric Motor & Lorentz Force**: Permanent North/South magnets, rotating copper armature coil, split-ring commutator, and magnetic flux field lines illustrating $F = I \times L \times B$.
  4. **Inner Solar System & Orbits**: Sun and terrestrial planets (Mercury, Venus, Earth with orbiting Moon, Mars) demonstrating Kepler's laws.
  5. **Polar Water Molecule ($H_2O$)**: Bent geometry ($104.5^\circ$), central electronegative oxygen with partial negative charge ($\delta^-$), hydrogen atoms with partial positive charge ($\delta^+$), and polar covalent bond vectors.
  6. **Methane Molecule ($CH_4$)**: Tetrahedral $sp^3$ hybridised geometry with symmetrical $109.5^\circ$ bond angles.
  7. **Mitochondria Organelle**: Semi-transparent outer phospholipid membrane, deep inner cristae folds, and glowing green ATP synthase enzyme spheres.
  8. **Motor Neuron**: Soma cell body, dendrite cones, central axon core, insulating myelin sheaths with Nodes of Ranvier, and synaptic terminal knob.
- **Generative 3D Model Constructor (`generate_custom_3d_concept`)**:
  - Natural language prompt bar: Students can type queries (e.g., *"Human Eye anatomy"*, *"Plant Cell"*, *"Diamond lattice"*).
  - LLM dynamically generates procedural 3D elements (spheres, cylinders, boxes, toruses, cones) and interconnecting bonds as a valid Three.js specification on the fly.

---

### 13. Student Knowledge Graph & Prerequisite Dependency Engine
*Implementation: `src/knowledge_graph.py`, `static/knowledge_graph.js`*
- **Persistent SQLite Cognitive Graph Store**: Tracks mastery across a curriculum dependency tree (e.g., *Electric Current* $\rightarrow$ *Voltage* $\rightarrow$ *Ohm's Law* $\rightarrow$ *Parallel Networks* $\rightarrow$ *Joule Heating*).
- **Ebbinghaus Memory Retention Decay**:
  - Dynamically decays concept mastery over elapsed days:
    $$R = M \cdot e^{-0.08 \cdot \Delta t}$$
- **Cognitive Node States**:
  - `mastered`: $\ge 75\%$ retention mastery.
  - `in-progress`: Attempted with ongoing practice.
  - `needs-remediation`: Misconceptions detected.
  - `ready-to-learn`: All prerequisite concepts mastered.
  - `locked`: Unmet upstream prerequisites.
- **Interactive HTML5 Canvas Visualizer**:
  - Physics-based spring-embedder simulation with velocity damping and repulsive forces.
  - Draggable nodes, color-coded mastery rings, and pulsating dependency links.
  - Click-to-inspect **Concept Diagnostics Drawer** showing attempts, accuracy, confidence, and misconception history.

---

### 14. Learning DNA Profiler (5-Dimensional Cognitive Spectrum)
*Implementation: `src/learning_dna.py`*
- **Empirical Cognitive Profiling**: Measures student learning preferences across five distinct axes ($0 - 100\%$):
  1. **Visual Deconstruction**: Affinity for 3D spatial models, diagrams, and animations.
  2. **Real-World Analogies**: Breakthrough speed when mapped to tangible Indian analogies.
  3. **First-Principles Conceptual**: Rigor in starting from definitions and mathematical derivations.
  4. **Targeted Recall & Practice**: Acceleration through rapid checkpoints and numerical problems.
  5. **Active Socratic Dialogue**: Retention via guided exploratory questioning.
- **Dominant Trait Detection & Personalization**: Identifies the student's highest-affinity dimension and tailors subsequent prompt explanations to optimize learning speed.

---

### 15. Cognitive Spaced Repetition Retention Engine (SM-2)
*Implementation: `src/spaced_repetition.py`*
- **Ebbinghaus Forgetting Curve Countermeasure**:
  - Computes elapsed time since last study session and schedules SM-2 review checkpoints:
    - **Day 0**: Initial Mastery Acquired.
    - **Day 1**: 60-second rapid concept flash question.
    - **Day 3**: 1 targeted numerical application checkpoint.
    - **Day 7**: 3-question mini-assessment checkpoint.
    - **Day 14 / Day 30**: Long-term mastery verification.
- **Prioritized Queue Cards**:
  - Urgency Tiers: `OVERDUE` (Red alert), `DUE_TODAY` (Amber), `RETAINED` (Green).
  - Supplies concrete recommended actions and targeted recall questions.

---

### 16. Institutional Teacher Dashboard & Class Intervention Engine
*Implementation: `src/teacher_dashboard.py`*
- **Classroom Cohort Analytics**: Aggregates metrics for schools, teachers, and administrators (e.g., Class 10-A Science, 42 enrolled students).
- **Concept Risk Heatmap**: Tracks average cohort mastery and flags high-risk and critical-risk concepts (e.g., Series & Parallel Resistors at 41% mastery with 22 students at risk).
- **Shared Misconception Clusters**: Aggregates common errors across multiple students, displaying percentage impact, cognitive root cause, and recommended classroom interventions.
- **1-Click Targeted Remediation Micro-Lessons**:
  - Generates ready-to-launch 5-minute targeted remediation modules for struggling cohorts in bilingual languages (e.g., Hinglish / Tamil).

---

### 17. Formative Assessment, Automated Grading & Diagnostic Report Cards
*Implementation: `src/assessment.py`*
- **Taught-Only Quiz Generation**: Generates 3–6 mixed MCQ and short-answer questions strictly confined to concepts taught in the current session.
- **Two-Stage Intelligent Grading**:
  - *Stage 1*: Fast deterministic match for MCQs (exact string, letter option, or substring match).
  - *Stage 2*: Few-shot JSON LLM evaluation returning score ($0.0 - 1.0$), verdict, and constructive feedback.
- **Standardized Diagnostic Report Card**:
  - Outputs overall score (`X/Y`), percentage, list of strong areas, list of concepts needing improvement, and a concrete revision recommendation.
  - Automatically merges in concepts the student struggled with during the live teaching session.

---

### 18. Cross-Session Profile Store & AI Next-Topic Recommender
*Implementation: `src/profile_store.py`*
- **SQLite Progress Persistence (`profiles.sqlite3`)**: Records student name, topic title, language, level, score, strong concepts, weak concepts, and timestamps.
- **AI Next-Topic Recommendation Engine**:
  - Analyzes longitudinal session history, recurring weak concepts, and current topic.
  - Generates a tailored recommendation for the next curriculum topic, explicitly addressing persistent weak areas.

---

### 19. Dual User Interface Ecosystem

#### A. Primary Modern Stitch Web SPA
*Implementation: `server.py`, `static/index.html`, `static/app.js`, `static/styles.css`*
- Built with **FastAPI**, **Tailwind CSS**, and **HTML5 Canvas / Three.js**.
- **8 Dedicated Full-Featured Views**:
  1. *Upload & Plan View*: File dropzone, topic input, duration selector, and "Teach Me Like..." preset bar.
  2. *Lesson Plan Preview View*: Concept segments, source citation badges, and checkpoint previews.
  3. *Live Interactive Classroom View*: Synchronized video/audio player, Hallucination Shield badge, spoken transcript, checkpoint question card, answer submission, and Misconception Engine diagnosis card.
  4. *Bharat 3D Lab™ View*: Three.js WebGL canvas, 8 model presets, prompt generator, and annotation inspector.
  5. *Knowledge Graph View*: Interactive physics network canvas, KPI mastery cards, and concept diagnostic drawer.
  6. *Learning DNA View*: 5-dimensional progress bars and personalized cognitive insight card.
  7. *Spaced Repetition View*: Prioritized SM-2 review cards and flash question triggers.
  8. *Teacher Dashboard View*: Cohort mastery heatmap, shared misconception clusters, and 1-click remediation triggers.
  9. *Assessment & Report Card View*: Interactive quiz submission and formatted report card.
- **"Teach Me Like..." 1-Click Pedagogical Presets**:
  - 👶 **Like I'm 10**: Playful everyday analogies, zero jargon.
  - 🏏 **Using Cricket**: Explains forces, momentum, and electricity using cricket mechanics.
  - 🎓 **Like My Professor**: Formal academic rigor, boundary conditions, and derivations.
  - 🇮🇳 **Tanglish (Tamil + Eng)**: Conversational Tamil with English technical terms.
  - ⚡ **5-Minute Blitz**: Rapid high-impact conceptual summary and formula punchline.
  - 🏛️ **Socratic Guide**: Pure question-led exploratory deduction.
- **Interactive Voice Talkback**:
  - Built-in microphone button leveraging the browser Web Speech API for voice answer dictation.

#### B. Secondary Streamlit Dashboard
*Implementation: `app.py`*
- Lightweight secondary interface for rapid testing and headless verification.
- Complete 5-stage interactive wizard: `Setup` $\rightarrow$ `Plan` $\rightarrow$ `Teach` $\rightarrow$ `Quiz` $\rightarrow$ `Report`.

---

### 20. Inclusive Accessibility Suite
*Implementation: `static/index.html`, `static/app.js`*
- **Dyslexia-Friendly Font Toggle**: Instantly switches typography to `OpenDyslexic` across the application.
- **High-Contrast Visual Mode**: High-contrast theme toggle for visually impaired learners.
- **Audio Speed Controller**: Dropdown to adjust teacher speech pace ($0.85\times$, $1.0\times$, $1.2\times$).

---

### 21. Comprehensive Verification & Testing Suite
*Implementation: `scripts/`*
- `scripts/test_day1.py`: Verifies multi-format ingestion, chunk metadata, MiniLM retrieval, and lesson planning.
- `scripts/test_day2.py`: Tests the teaching state machine, adaptation loop, error recovery, and MP4 video generation.
- `scripts/test_day3.py`: Validates end-to-end lesson flows, quiz generation, automated grading, reporting, and SQLite profile persistence.
- `scripts/test_server_api.py`: Tests all FastAPI REST endpoints using the TestClient.
- `scripts/test_bharatguru.py`: Comprehensive test suite verifying Knowledge Graph transitions, Misconception Engine diagnostics, Bharat Context injection, 3D model specifications, Hallucination Shield calculations, and Spaced Repetition queue generation.

---

## 📐 System Architecture Diagram

```
                       STUDY MATERIAL / TOPIC INPUT
                         (PDF, DOCX, PPTX, TXT, MD)
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │   Multi-Format Ingestion & Boundary-Aware Chunking     │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │                  HYBRID RAG RETRIEVER                  │
       │  Dense MiniLM Embeddings + Sparse BM25 + Reciprocal    │
       │                   Rank Fusion (RRF)                    │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
       ┌────────────────────────────────────────────────────────┐
       │           Instruction Parser & Lesson Planner          │
       │  (Level, Time Budget, Language, Bharat Presets)        │
       └────────────────────────────┬───────────────────────────┘
                                    │
                                    ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    TEACHING SESSION STATE MACHINE LOOP                       │
│                                                                              │
│   ┌───────────┐      ┌────────────┐      ┌────────────┐      ┌───────────┐   │
│   │  EXPLAIN  │ ───► │  QUESTION  │ ───► │  EVALUATE  │ ───► │   ADAPT   │   │
│   └─────┬─────┘      └────────────┘      └─────┬──────┘      └─────┬─────┘   │
│         │                                      │                   │         │
│         ▼                                      ▼                   ▼         │
│  Bharat Context       Few-Shot Formative Grader       Pedagogy Selector      │
│  Hallucination Shield Misconception Engine™           (Analogy, Counter-     │
│  (Citation Guard)     (Cognitive Diagnosis)            example, Socratic)    │
└─────────┬──────────────────────────────────────────────────────────┬─────────┘
          │                                                          │
          ▼                                                          ▼
┌──────────────────────────────┐                         ┌───────────────────────┐
│     SYNTHESIS & MEDIA        │                         │  INTELLIGENCE LAYER   │
│ • edge-tts Neural Voice      │                         │ • Knowledge Graph     │
│ • CPU Amplitude Lip-Sync     │                         │ • Learning DNA        │
│ • Subject-Tinted Slides      │                         │ • Spaced Repetition   │
│ • Burned-in Subtitles MP4    │                         │ • Teacher Dashboard   │
│ • Bharat 3D Lab™ (Three.js)  │                         │ • Next-Topic Engine   │
└──────────────────────────────┘                         └───────────────────────┘
```

---

## 📂 Complete Project File Manifest

```
BHARAT_AI/
├── config.py                      # Central configuration, paths, model selectors & .env loader
├── server.py                      # FastAPI REST API server & static file host (Primary Web Backend)
├── app.py                         # Secondary Streamlit dashboard application
├── requirements.txt               # Complete Python project dependencies
├── .env.example                   # Template environment variables file
├── README.md                      # Comprehensive project documentation
├── DOCUMENTATION.md               # Technical documentation & sprint architecture notes
│
├── src/                           # Core Engine Modules
│   ├── __init__.py                # Package initializer
│   ├── assessment.py              # Quiz generation, few-shot grading & diagnostic reports
│   ├── avatar.py                  # Pure-CPU amplitude-driven mouth-swap avatar generator
│   ├── bharat_context.py          # Bharat Context Engine (Indian cultural & real-world anchors)
│   ├── hallucination_shield.py    # Hallucination Shield & citation grounding verifier
│   ├── hybrid_rag.py              # Hybrid retrieval (MiniLM dense + BM25 sparse + RRF)
│   ├── ingestion.py               # Universal multi-format document parser (PDF/DOCX/PPTX/TXT)
│   ├── knowledge_graph.py         # Student Knowledge Graph & Ebbinghaus retention decay engine
│   ├── learning_dna.py            # Learning DNA 5-dimensional cognitive profiler
│   ├── lesson_planner.py          # Free-text instruction parser & curriculum planning agent
│   ├── llm.py                     # Multi-tier cascading LLM wrapper (Groq + NVIDIA + Gemini + Mock)
│   ├── misconception_engine.py    # Misconception Engine™ & cognitive error fingerprinter
│   ├── model_3d.py                # Bharat 3D Lab procedural Three.js science model generator
│   ├── pedagogy.py                # Adaptive pedagogy policy selector & Socratic dialogue engine
│   ├── pipeline.py                # End-to-end pipeline orchestrator & headless runner
│   ├── profile_store.py           # SQLite session store & AI next-topic recommendation engine
│   ├── retrieval.py               # Dense MiniLM vector embedding store & cosine ranking
│   ├── spaced_repetition.py       # Spaced repetition review queue scheduler (SM-2 intervals)
│   ├── teacher_dashboard.py       # Institutional teacher dashboard & class intervention engine
│   ├── teaching.py                # 5-stage pedagogical state machine & transition logger
│   ├── tts.py                     # 12-language neural voice synthesizer (edge-tts + gTTS fallback)
│   ├── video.py                   # Slide rendering, PiP avatar, subtitle burn-in & ffmpeg muxer
│   └── visuals.py                 # Subject-tinted slide generation with PIL
│
├── static/                        # Modern Web SPA Frontend (Tailwind + Three.js + Canvas)
│   ├── index.html                 # 8-view Single Page Application shell & layout
│   ├── app.js                     # Frontend state machine, event bindings, and Web Speech talkback
│   ├── knowledge_graph.js         # Interactive physics-based HTML5 canvas knowledge graph
│   ├── three_lab.js               # Interactive Three.js WebGL 3D science viewer & raycaster
│   └── styles.css                 # Custom animations, high-contrast & dyslexia typography rules
│
├── sample_data/                   # Demo Materials
│   └── electricity_chapter.txt    # Bundled physics curriculum notes for instant 1-click testing
│
├── assets/                        # Persona & Static Media
│   └── avatar/                    # Generated persona mouth states (mouth_closed, mouth_half, mouth_open)
│
├── output/                        # Runtime Workdir (Auto-created)
│   ├── profiles.sqlite3           # SQLite database for knowledge graph and student sessions
│   ├── web_media/                 # Segment MP3s and composited MP4 video files
│   └── uploads/                   # Uploaded study documents
│
└── scripts/                       # Automated Test & Verification Scripts
    ├── test_day1.py               # Verification: Ingestion, chunking, retrieval & lesson planning
    ├── test_day2.py               # Verification: Teaching state machine, adaptation & video export
    ├── test_day3.py               # Verification: End-to-end lesson, quiz, grading & report cards
    ├── test_server_api.py         # Verification: FastAPI REST API endpoints test suite
    ├── test_bharatguru.py         # Verification: Knowledge graph, 3D lab, shield & misconception engine
    └── make_avatar.py             # Utility to generate default avatar mouth PNG assets
```

---

## 🔌 Complete REST API Specification

All endpoints are hosted by `server.py` at `http://localhost:8000`:

| Method | Endpoint | Description | Request Body / Parameters |
|:---|:---|:---|:---|
| `GET` | `/api/languages` | Lists all 12 supported Indian languages, ISO codes, and neural voices | None |
| `GET` | `/api/presets` | Returns "Teach Me Like..." presets, teaching modes, and exam boards | None |
| `GET` | `/api/sample-files` | Returns bundled demo documents in `sample_data/` | None |
| `POST` | `/api/upload` | Uploads PDF, DOCX, PPTX, TXT, or MD documents | `Multipart/form-data` (`file`) |
| `POST` | `/api/plan` | Ingests documents, retrieves context, and builds structured lesson plan | `{ topic, instruction, upload_paths, language, preset_style, mode, exam_board, student }` |
| `POST` | `/api/session/explain` | Generates explanation, synthesized voice, and begins video rendering | `{ session_id, segment_index, render_video }` |
| `GET` | `/api/session/video-status/{session_id}/{segment_index}` | Polls video rendering status (`ready` / `rendering`) | Path params |
| `POST` | `/api/session/answer` | Evaluates student answer, fingerprints misconceptions, updates knowledge graph | `{ session_id, segment_index, answer, is_followup, student }` |
| `POST` | `/api/session/adapt` | Triggers pedagogical re-explanation with counterexample/analogy | `{ session_id, segment_index, render_video }` |
| `POST` | `/api/session/advance` | Advances session to the next concept segment | `{ session_id }` |
| `POST` | `/api/session/language` | Switches teaching language mid-lesson without losing progress | `{ session_id, language }` |
| `POST` | `/api/session/socratic` | Executes an interactive Socratic dialogue turn | `{ session_id, concept, student_input, history }` |
| `POST` | `/api/quiz/generate` | Generates formative assessment questions limited to taught concepts | `{ session_id }` |
| `POST` | `/api/quiz/submit` | Grades quiz answers, stores session in SQLite, and generates report card | `{ session_id, student, answers: { "0": "...", "1": "..." } }` |
| `GET` | `/api/knowledge-graph/{student}` | Returns cognitive knowledge graph nodes, links, and retention scores | Path param (`student`) |
| `GET` | `/api/student/dna/{student}` | Returns 5-dimensional Learning DNA profile and pedagogical insight | Path param (`student`) |
| `GET` | `/api/spaced-repetition/{student}` | Returns prioritized SM-2 spaced repetition review queue cards | Path param (`student`) |
| `GET` | `/api/teacher/class-overview` | Returns cohort mastery heatmap, shared misconceptions, and remediations | None |
| `GET` | `/api/profile/{student}` | Retrieves historical learning sessions and recurring weak concepts | Path param (`student`) |
| `GET` | `/api/3d/model` | Fetches Three.js WebGL specification for preset models (`dna`, `atom`, `motor`, etc.) | Query param (`concept`) |
| `POST` | `/api/3d/generate` | Dynamically constructs procedural 3D model from natural language prompt | `{ query: "Human Eye" }` |

---

## ⚡ Installation & Quickstart Guide

### Prerequisites
- **Python 3.10+**
- (Optional) `ffmpeg` installed on your system. If not present, the bundled `imageio-ffmpeg` binary is utilized automatically with zero manual installation required.

### 1. Setup Virtual Environment & Dependencies
```bash
# Clone or navigate to the repository directory:
cd c:\Users\pravi\OneDrive\Desktop\BHARAT_AI

# Create virtual environment:
python -m venv .venv

# Activate virtual environment:
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

# Install required dependencies:
pip install -r requirements.txt
```

### 2. Configure API Keys (or Run 100% Offline)
```bash
# Copy example environment file:
copy .env.example .env     # On Linux/macOS: cp .env.example .env
```
Open `.env` and add your preferred provider key:
- **Google Gemini**: Get key from [Google AI Studio](https://aistudio.google.com/app/apikey) $\rightarrow$ `GEMINI_API_KEY=...`
- **Groq LPU (Sub-second inference)**: Get key from [Groq Console](https://console.groq.com/) $\rightarrow$ `GROQ_API_KEY=...`
- **NVIDIA NIM**: Get key from [NVIDIA Build](https://build.nvidia.com/) $\rightarrow$ `NVIDIA_API_KEY=...`

> **100% Offline Mode**: If you have no API keys or wish to run completely offline with zero tokens, set `LLM_MOCK=1` in your `.env` file or environment. The entire pedagogical engine will run locally using built-in diagnostic mocks.

### 3. Launch the Applications

#### Option A: Launch Primary Modern Web Application (Recommended)
```bash
python server.py
```
Open your browser and navigate to **`http://localhost:8000`**.

#### Option B: Launch Secondary Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🧪 Verification & Offline Testing

You can verify all components locally without spending tokens using `LLM_MOCK=1`:

```bash
# On Windows PowerShell:
$env:LLM_MOCK="1"

# 1. Verify Day 1 (Ingestion, Chunking, MiniLM Retrieval & Lesson Planning):
python scripts/test_day1.py

# 2. Verify Day 2 (Teaching Loop, Misconception Adaptation & MP4 Video Compositing):
python scripts/test_day2.py

# 3. Verify Day 3 (End-to-End Lesson, Quiz, Grading, Diagnostic Report & SQLite Profile):
python scripts/test_day3.py --video

# 4. Verify FastAPI REST API Server Endpoints:
python scripts/test_server_api.py

# 5. Verify BharatGuru Intelligence Stack (Knowledge Graph, 3D Lab, Shield & Misconception Engine):
python scripts/test_bharatguru.py
```
Every test script outputs a step-by-step checklist and concludes with `OK`.

---

## ⚙️ Environment Variables & Configuration

All settings are configured via `config.py` and `.env`:

| Variable | Default Value | Description |
|:---|:---|:---|
| `GEMINI_API_KEY` | `""` | Google Gemini API key for deep reasoning & planning |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model variant (`gemini-2.5-flash`, `gemini-1.5-flash`) |
| `GROQ_API_KEY` | `""` | Groq API key for sub-second LPU text generation |
| `GROQ_MODEL` | `qwen/qwen3.8-27b` | Groq model selection |
| `NVIDIA_API_KEY` | `""` | NVIDIA NIM API key for GPU accelerated generation |
| `NVIDIA_MODEL` | `meta/llama-3.2-11b-vision-instruct` | NVIDIA NIM model selection |
| `LLM_MOCK` | `0` | Set to `1` to run all pipelines completely offline with zero API calls |
| `EMBED_MODEL` | `all-MiniLM-L6-v2` | SentenceTransformer model for dense vector embeddings |
| `AITEACHER_WORKDIR` | `./output` | Directory where videos, audio, uploads, and SQLite database are saved |
| `VIDEO_FPS` | `12` | Frame rate for composited MP4 avatar video |
| `VIDEO_W` | `1280` | Video width in pixels (720p HD) |
| `VIDEO_H` | `720` | Video height in pixels (720p HD) |

---

## 🏆 Summary of Key Innovations

| Feature | Standard AI Chatbots | BHARATGURU (AI Teacher) |
|:---|:---|:---|
| **Teaching Model** | Passive walls of text | Active segment-by-segment check-and-teach cycle |
| **Error Handling** | Simple "Incorrect, here is the answer" | **Misconception Engine™**: Identifies cognitive root cause & prescribes counterexamples |
| **Pedagogical Shifts** | Repeats the same explanation | **Adaptive Policy Selector**: Switches to worked examples, analogies, or Socratic inquiry |
| **Cultural Relevance** | Generic Western examples ($ and baseball) | **Bharat Context Engine**: Authentic Indian metaphors, cricket mechanics, and regional anchors |
| **Hallucination Protection** | Unchecked generative output | **Hallucination Shield**: Real-time document lexical overlap scoring & passage inspector |
| **Visuals & Avatars** | None or heavy multi-gigabyte GPU models | **Pure-CPU Lip-Sync Avatar**: Real-time RMS volume envelope mouth swapping (Zero GPU) |
| **3D Interactivity** | None | **Bharat 3D Lab™**: Interactive Three.js WebGL models & dynamic generative 3D constructor |
| **Long-Term Memory** | Session resets on refresh | **Knowledge Graph & Learning DNA**: Ebbinghaus decay curve, mastery tracking & SM-2 review queue |
| **Institutional Use** | None | **Teacher Dashboard**: Cohort mastery heatmap, shared misconception clusters & 1-click remediations |

---

*Built for Indian Students, Teachers, and Schools.*
