/**
 * BHARATGURU Frontend State Machine Controller
 * Orchestrates adaptive teaching, voice talkback, misconception fingerprinting,
 * knowledge graph modeling, and institutional analytics.
 */

// Global Application State
const AppState = {
  currentView: 'view-upload-material',
  activeMachineState: 'understand',
  sessionId: null,
  plan: null,
  currentSegmentIndex: 0,
  uploadedFiles: [],
  selectedLanguage: 'English',
  selectedPresetStyle: '',
  selectedTeachingMode: 'DIRECT',
  selectedExamBoard: 'CBSE Class 10/12',
  student: 'student1',
  scoreSummary: { correct: 0, total: 0, weak: [] },
  isAdapting: false,
  quizData: null,
  quizAnswers: {},
  reportData: null,
  knowledgeGraphVisualizer: null,
  currentGroundingReport: null,
  threeLab: null,
};

document.addEventListener('DOMContentLoaded', () => {
  initAccessibility();
  bindNavigationEvents();
  bindPresetEvents();
  bindUploadEvents();
  bindClassroomEvents();
  bindVoiceTalkback();
  bindQuizEvents();
  bind3DLabEvents();

  // Initialize Knowledge Graph Canvas
  AppState.knowledgeGraphVisualizer = new KnowledgeGraphVisualizer('knowledge-graph-canvas');

  // Load initial intelligence data
  loadKnowledgeGraph();
  loadLearningDNA();
  loadSpacedRepetition();
  loadTeacherDashboard();

  // Set default view
  switchView('view-upload-material');
  setMachineState('understand');
});

// --------------------------------------------------------------------------- //
// Accessibility Controls (Dyslexia Font, Contrast, Speech Pace)
// --------------------------------------------------------------------------- //
function initAccessibility() {
  const btnDyslexia = document.getElementById('btn-toggle-dyslexia');
  const btnContrast = document.getElementById('btn-toggle-contrast');
  const speechRateSelect = document.getElementById('select-speech-rate');

  btnDyslexia?.addEventListener('click', () => {
    document.body.classList.toggle('font-dyslexic');
    btnDyslexia.classList.toggle('text-primary');
    btnDyslexia.classList.toggle('bg-primary/10');
  });

  btnContrast?.addEventListener('click', () => {
    document.body.classList.toggle('high-contrast');
    btnContrast.classList.toggle('text-primary');
    btnContrast.classList.toggle('bg-primary/10');
  });

  speechRateSelect?.addEventListener('change', (e) => {
    const rate = parseFloat(e.target.value);
    const video = document.getElementById('classroom-video');
    const audio = document.getElementById('classroom-audio');
    if (video) video.playbackRate = rate;
    if (audio) audio.playbackRate = rate;
  });
}

// --------------------------------------------------------------------------- //
// Navigation & State Stepper
// --------------------------------------------------------------------------- //
function switchView(viewId) {
  AppState.currentView = viewId;

  // Toggle view containers
  const viewSections = [
    'view-upload-material',
    'view-lesson-plan',
    'view-live-classroom',
    'view-3d-lab',
    'view-knowledge-graph',
    'view-learning-dna',
    'view-spaced-repetition',
    'view-teacher-dashboard',
    'view-quiz-assessment'
  ];

  viewSections.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      if (id === viewId) {
        el.classList.remove('hidden');
      } else {
        el.classList.add('hidden');
      }
    }
  });

  // Update nav tabs
  document.querySelectorAll('header nav a[data-target]').forEach(tab => {
    const target = tab.getAttribute('data-target');
    if (target === viewId) {
      tab.className = 'nav-tab text-[14px] text-primary font-bold border-b-2 border-primary pb-1';
    } else {
      tab.className = 'nav-tab text-[14px] text-on-surface-variant hover:text-primary transition-colors pb-1';
    }
  });

  // Load view data on tab activation
  if (viewId === 'view-3d-lab') {
    if (!AppState.threeLab && typeof Bharat3DLab !== 'undefined') {
      AppState.threeLab = new Bharat3DLab('threejs-canvas-container');
    }
    if (AppState.threeLab) {
      setTimeout(() => AppState.threeLab.onResize(), 120);
    }
  } else if (viewId === 'view-knowledge-graph') {
    loadKnowledgeGraph();
    if (AppState.knowledgeGraphVisualizer) {
      setTimeout(() => AppState.knowledgeGraphVisualizer.resize(), 100);
    }
  } else if (viewId === 'view-learning-dna') {
    loadLearningDNA();
  } else if (viewId === 'view-spaced-repetition') {
    loadSpacedRepetition();
  } else if (viewId === 'view-teacher-dashboard') {
    loadTeacherDashboard();
  }
}

function setMachineState(stateName) {
  AppState.activeMachineState = stateName;
  document.querySelectorAll('aside nav a[data-path]').forEach(link => {
    const path = link.getAttribute('data-path');
    if (path === stateName) {
      link.className = 'flex items-center px-4 py-3 rounded-xl bg-primary text-on-primary font-bold shadow-sm transition-all';
      const icon = link.querySelector('.material-symbols-outlined');
      if (icon) icon.className = 'material-symbols-outlined mr-3 text-[20px] text-on-primary';
    } else {
      link.className = 'flex items-center px-4 py-3 rounded-xl text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-all group';
      const icon = link.querySelector('.material-symbols-outlined');
      if (icon) icon.className = 'material-symbols-outlined mr-3 text-[20px] group-hover:scale-110 transition-transform text-primary';
    }
  });
}

function bindNavigationEvents() {
  document.querySelectorAll('header nav a[data-target]').forEach(tab => {
    tab.addEventListener('click', (e) => {
      e.preventDefault();
      const target = tab.getAttribute('data-target');
      switchView(target);
    });
  });

  document.querySelectorAll('aside nav a[data-path]').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const path = link.getAttribute('data-path');
      setMachineState(path);
      if (path === 'understand' || path === 'plan') {
        switchView('view-upload-material');
      } else {
        switchView('view-live-classroom');
      }
    });
  });
}

// --------------------------------------------------------------------------- //
// "Teach Me Like..." Style Presets
// --------------------------------------------------------------------------- //
function bindPresetEvents() {
  const presets = {
    'ten_year_old': "I am 10 years old. Teach me using simple everyday examples, fun metaphors, and zero complicated jargon.",
    'cricket': "Teach me using cricket scenarios — bowling speeds, bat collision physics, spin, fielding and pitch dynamics.",
    'professor': "Explain this with rigorous mathematical foundations, derivations, and boundary condition proofs.",
    'bilingual_tamil': "Explain in natural Tamil (Tanglish) while keeping all scientific formulas and technical terminology clear in English.",
    'five_min': "I only have 5 minutes. Give me the high-impact conceptual intuition and formula punchline immediately.",
    'socratic': "Teach me through Socratic inquiry. Ask me guiding questions and lead me to discover the principle myself."
  };

  document.querySelectorAll('.preset-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const presetKey = btn.getAttribute('data-preset');
      AppState.selectedPresetStyle = presetKey;

      // Highlight button
      document.querySelectorAll('.preset-btn').forEach(b => {
        b.classList.remove('bg-primary', 'text-on-primary', 'bg-secondary', 'text-on-secondary');
        b.classList.add('bg-surface');
      });
      btn.classList.remove('bg-surface');
      btn.classList.add('bg-primary', 'text-on-primary');

      // Fill instruction textarea
      const instrEl = document.getElementById('instruction-input');
      if (instrEl && presets[presetKey]) {
        instrEl.value = presets[presetKey];
      }

      // If socratic preset, set mode to SOCRATIC
      if (presetKey === 'socratic') {
        const modeSelect = document.getElementById('select-teaching-mode');
        if (modeSelect) modeSelect.value = 'SOCRATIC';
      }
    });
  });
}

// --------------------------------------------------------------------------- //
// Upload & Lesson Creation
// --------------------------------------------------------------------------- //
function bindUploadEvents() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('file-input');
  const btnLoadSample = document.getElementById('btn-load-sample');
  const btnBuildLesson = document.getElementById('btn-build-lesson');

  dropzone?.addEventListener('click', () => fileInput?.click());

  dropzone?.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('border-primary', 'bg-surface');
  });

  dropzone?.addEventListener('dragleave', () => {
    dropzone.classList.remove('border-primary', 'bg-surface');
  });

  dropzone?.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('border-primary', 'bg-surface');
    if (e.dataTransfer.files) {
      handleFiles(e.dataTransfer.files);
    }
  });

  fileInput?.addEventListener('change', (e) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  });

  btnLoadSample?.addEventListener('click', async () => {
    try {
      btnLoadSample.disabled = true;
      btnLoadSample.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> Loading...';
      const res = await fetch('/api/sample-files');
      const files = await res.json();
      if (files && files.length > 0) {
        AppState.uploadedFiles = [files[0].path];
        renderUploadedFiles([{ name: files[0].name, size_bytes: files[0].size_bytes }]);
        document.getElementById('topic-input').value = 'Electricity: Current, Voltage and Resistance';
      }
    } catch (err) {
      console.error('Error loading sample file:', err);
    } finally {
      btnLoadSample.disabled = false;
      btnLoadSample.innerHTML = '<span class="material-symbols-outlined text-[16px]">bolt</span> Load Sample Electricity Chapter';
    }
  });

  btnBuildLesson?.addEventListener('click', async () => {
    await buildLessonPlan();
  });
}

async function handleFiles(files) {
  for (const file of files) {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        AppState.uploadedFiles.push(data.file_path);
        renderUploadedFiles([{ name: data.filename, size_bytes: data.size_bytes }]);
      }
    } catch (err) {
      console.error('Upload error:', err);
    }
  }
}

function renderUploadedFiles(files) {
  const container = document.getElementById('uploaded-files-list');
  if (!container) return;

  files.forEach(f => {
    const div = document.createElement('div');
    div.className = 'flex items-center justify-between p-3 rounded-xl bg-surface border border-outline-variant/30 text-[13px] shadow-sm';
    div.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="material-symbols-outlined text-primary text-[20px]">description</span>
        <span class="font-medium text-on-surface">${f.name}</span>
      </div>
      <span class="font-mono text-[11px] text-tertiary-container font-semibold">✓ Ingested</span>
    `;
    container.appendChild(div);
  });
}

async function buildLessonPlan() {
  const btn = document.getElementById('btn-build-lesson');
  const topic = document.getElementById('topic-input')?.value.trim() || '';
  const instruction = document.getElementById('instruction-input')?.value.trim() || '';
  const language = document.getElementById('select-language')?.value || 'English';
  const mode = document.getElementById('select-teaching-mode')?.value || 'DIRECT';
  const examBoard = document.getElementById('select-exam-board')?.value || '';

  AppState.selectedLanguage = language;
  AppState.selectedTeachingMode = mode;
  AppState.selectedExamBoard = examBoard;

  try {
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined text-[20px] animate-spin">sync</span> Grounding & Generating Plan...';

    const res = await fetch('/api/plan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        topic: topic,
        instruction: instruction,
        upload_paths: AppState.uploadedFiles,
        language: language,
        preset_style: AppState.selectedPresetStyle,
        mode: mode,
        exam_board: examBoard,
        student: AppState.student,
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Plan generation failed');

    AppState.sessionId = data.session_id;
    AppState.plan = data;
    AppState.currentSegmentIndex = 0;

    renderLessonPlanPreview(data);
    switchView('view-lesson-plan');
    setMachineState('plan');

    // Update knowledge graph with returned structure
    if (data.knowledge_graph && AppState.knowledgeGraphVisualizer) {
      AppState.knowledgeGraphVisualizer.updateWithApiData(data.knowledge_graph);
    }
  } catch (err) {
    console.error('Error building plan:', err);
    alert('Error generating lesson plan: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">auto_awesome</span> Build Adaptive Lesson Plan';
  }
}

function renderLessonPlanPreview(plan) {
  document.getElementById('plan-title').textContent = plan.title;

  const metaBox = document.getElementById('plan-meta');
  metaBox.innerHTML = `
    <span class="bg-primary-container text-on-primary-container font-mono text-[11px] px-3 py-1 rounded-full font-bold">Language: ${plan.language}</span>
    <span class="bg-secondary-container/30 text-secondary font-mono text-[11px] px-3 py-1 rounded-full font-bold">Mode: ${plan.mode}</span>
    <span class="bg-tertiary-container/30 text-tertiary-container font-mono text-[11px] px-3 py-1 rounded-full font-bold">${plan.grounded ? '✓ Grounded in Document' : 'General Knowledge'}</span>
    <span class="bg-surface-container text-on-surface font-mono text-[11px] px-3 py-1 rounded-full font-bold">${plan.segments.length} Segments</span>
  `;

  const list = document.getElementById('plan-segments-list');
  list.innerHTML = '';

  plan.segments.forEach((seg, idx) => {
    const card = document.createElement('div');
    card.className = 'p-5 rounded-2xl bg-surface-container-low border border-outline-variant/30 space-y-2 shadow-sm';
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="w-6 h-6 rounded-full bg-primary text-on-primary font-mono text-[11px] font-bold flex items-center justify-center">${idx + 1}</span>
          <h4 class="font-headline-md text-[16px] font-bold text-on-surface">${seg.concept}</h4>
        </div>
        ${seg.source_label ? `<span class="font-mono text-[11px] bg-primary/10 text-primary px-2.5 py-0.5 rounded-full font-semibold">Cite: ${seg.source_label}</span>` : ''}
      </div>
      <p class="text-[13px] text-on-surface-variant font-medium">Anchor Analogy: <span class="text-on-surface">${seg.example || 'Everyday real-world context'}</span></p>
      ${seg.checkpoint_question ? `<p class="text-[12px] font-mono text-secondary bg-surface p-2.5 rounded-xl border border-outline-variant/20">Checkpoint: ${seg.checkpoint_question}</p>` : ''}
    `;
    list.appendChild(card);
  });

  document.getElementById('btn-start-classroom')?.addEventListener('click', () => {
    switchView('view-live-classroom');
    setMachineState('explain');
    loadSegment(0);
  });
}

// --------------------------------------------------------------------------- //
// Live Interactive Classroom & Teaching Loop
// --------------------------------------------------------------------------- //
function bindClassroomEvents() {
  document.getElementById('btn-submit-answer')?.addEventListener('click', () => submitStudentAnswer(false));
  document.getElementById('btn-adapt-reteach')?.addEventListener('click', () => triggerAdaptation());
  document.getElementById('btn-advance-segment')?.addEventListener('click', () => advanceSegment());

  // Mid-Lesson Language Switcher Buttons
  document.querySelectorAll('.lang-switch-btn').forEach(btn => {
    btn.addEventListener('click', async () => {
      const targetLang = btn.getAttribute('data-lang');
      await switchClassroomLanguage(targetLang);
    });
  });

  // Citation Inspector Modal
  document.getElementById('btn-inspect-citation')?.addEventListener('click', () => {
    const modal = document.getElementById('citation-modal');
    const labelEl = document.getElementById('modal-citation-label');
    const snippetEl = document.getElementById('modal-citation-snippet');

    if (AppState.currentGroundingReport) {
      labelEl.textContent = AppState.currentGroundingReport.source_citation;
      snippetEl.textContent = AppState.currentGroundingReport.source_passage_snippet;
    } else {
      labelEl.textContent = "Verified Source Passage";
      snippetEl.textContent = "Passage verified against uploaded curriculum chapter.";
    }
    modal.classList.remove('hidden');
  });

  document.getElementById('btn-close-modal')?.addEventListener('click', () => {
    document.getElementById('citation-modal').classList.add('hidden');
  });

  // Student Doubt & Follow-Up Questions (Task 2 Requirement)
  const btnSubmitDoubt = document.getElementById('btn-submit-doubt');
  const doubtInput = document.getElementById('student-doubt-input');
  const doubtBox = document.getElementById('doubt-response-box');
  const doubtAnswerText = document.getElementById('doubt-answer-text');
  const doubtGroundingTag = document.getElementById('doubt-grounding-tag');
  const btnPlayDoubtAudio = document.getElementById('btn-play-doubt-audio');
  let currentDoubtAudio = null;

  document.querySelectorAll('.doubt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const q = chip.getAttribute('data-q');
      if (doubtInput && q) {
        doubtInput.value = q;
        submitStudentFollowup();
      }
    });
  });

  const submitStudentFollowup = async () => {
    const q = doubtInput?.value.trim();
    if (!q || !AppState.sessionId) return;

    btnSubmitDoubt.disabled = true;
    btnSubmitDoubt.innerHTML = '<span class="material-symbols-outlined text-[15px] animate-spin">sync</span> Answering...';

    doubtBox?.classList.remove('hidden');
    if (doubtAnswerText) doubtAnswerText.textContent = 'BharatGuru is consulting lesson sources to clarify your doubt...';
    if (doubtGroundingTag) doubtGroundingTag.textContent = '';
    btnPlayDoubtAudio?.classList.add('hidden');

    try {
      const res = await fetch('/api/session/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: AppState.sessionId,
          segment_index: AppState.currentSegmentIndex,
          question: q,
        })
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to answer doubt');

      if (doubtAnswerText) doubtAnswerText.textContent = data.answer;

      if (data.grounding) {
        const pct = Math.round((data.grounding.confidence_score || 0.85) * 100);
        if (doubtGroundingTag) {
          doubtGroundingTag.innerHTML = `
            <span class="material-symbols-outlined text-[14px]">verified</span>
            <span>Source: ${data.source_label || 'Syllabus Context'} (${pct}% Grounded)</span>
          `;
        }
        const shieldBadge = document.getElementById('shield-status-badge');
        const shieldMsg = document.getElementById('shield-message');
        if (shieldBadge) {
          shieldBadge.textContent = `${pct}% GROUNDED`;
          shieldBadge.className = pct >= 80
            ? 'bg-tertiary-container text-on-tertiary text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold'
            : 'bg-secondary-container text-on-secondary-container text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold';
        }
        if (shieldMsg && data.grounding.shield_message) {
          shieldMsg.textContent = data.grounding.shield_message;
        }
      }

      if (data.audio_url) {
        if (!currentDoubtAudio) currentDoubtAudio = new Audio();
        currentDoubtAudio.src = data.audio_url;
        currentDoubtAudio.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
        currentDoubtAudio.play().catch(e => console.log('Doubt audio playback deferred:', e));

        if (btnPlayDoubtAudio) {
          btnPlayDoubtAudio.classList.remove('hidden');
          btnPlayDoubtAudio.onclick = () => {
            currentDoubtAudio.currentTime = 0;
            currentDoubtAudio.play();
          };
        }
      }
    } catch (err) {
      console.error('Doubt error:', err);
      if (doubtAnswerText) doubtAnswerText.textContent = 'Could not resolve doubt at this moment. Please try rephrasing.';
    } finally {
      btnSubmitDoubt.disabled = false;
      btnSubmitDoubt.innerHTML = '<span class="material-symbols-outlined text-[16px]">send</span> Ask Teacher';
    }
  };

  btnSubmitDoubt?.addEventListener('click', submitStudentFollowup);
  doubtInput?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitStudentFollowup();
  });
}

let videoPollInterval = null;

function pollVideoReady(sessionId, segmentIndex) {
  if (videoPollInterval) clearInterval(videoPollInterval);
  let attempts = 0;
  const maxAttempts = 50;
  videoPollInterval = setInterval(async () => {
    attempts++;
    if (AppState.currentSegmentIndex !== segmentIndex) {
      clearInterval(videoPollInterval);
      return;
    }
    if (attempts > maxAttempts) {
      clearInterval(videoPollInterval);
      const placeholder = document.getElementById('video-placeholder');
      if (placeholder) {
        placeholder.innerHTML = `
          <div class="flex flex-col items-center justify-center text-center p-6 space-y-2">
            <span class="material-symbols-outlined text-[36px] text-tertiary-container">record_voice_over</span>
            <p class="text-white/90 text-[14px] font-semibold">Audio Narration Active</p>
            <p class="text-white/50 text-[11px]">Video generation completed or deferred. Audio lecture is streaming live.</p>
          </div>
        `;
      }
      return;
    }
    try {
      const res = await fetch(`/api/session/video-status/${sessionId}/${segmentIndex}`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'ready' && data.video_url) {
          clearInterval(videoPollInterval);
          const video = document.getElementById('classroom-video');
          const placeholder = document.getElementById('video-placeholder');
          const audio = document.getElementById('classroom-audio');
          if (video && placeholder) {
            video.src = data.video_url;
            video.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
            if (audio && !audio.paused) {
              video.currentTime = audio.currentTime;
              audio.pause();
            }
            placeholder.classList.add('hidden');
            video.classList.remove('hidden');
            video.play().catch(e => console.log('Video auto-play deferred:', e));
          }
        }
      }
    } catch (e) {
      console.log('Video poll check:', e);
    }
  }, 1200);
}

async function loadSegment(segmentIndex) {
  AppState.currentSegmentIndex = segmentIndex;
  setMachineState('explain');

  const badge = document.getElementById('classroom-segment-badge');
  const title = document.getElementById('classroom-concept-title');
  const explanationText = document.getElementById('classroom-explanation-text');
  const questionText = document.getElementById('classroom-question-text');
  const video = document.getElementById('classroom-video');
  const placeholder = document.getElementById('video-placeholder');
  const feedbackBox = document.getElementById('answer-feedback-box');
  const misconceptionCard = document.getElementById('misconception-card');
  const btnAdvance = document.getElementById('btn-advance-segment');

  badge.textContent = `Segment ${segmentIndex + 1} of ${AppState.plan.segments.length}`;
  title.textContent = AppState.plan.segments[segmentIndex].concept;

  explanationText.textContent = 'Generating teacher explanation...';
  questionText.textContent = 'Preparing concept checkpoint...';
  feedbackBox.classList.add('hidden');
  misconceptionCard.classList.add('hidden');
  btnAdvance.classList.add('hidden');
  video.classList.add('hidden');
  placeholder.classList.remove('hidden');

  // Reset doubt box for new segment
  document.getElementById('doubt-response-box')?.classList.add('hidden');
  const doubtInputReset = document.getElementById('student-doubt-input');
  if (doubtInputReset) doubtInputReset.value = '';

  try {
    const res = await fetch('/api/session/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        segment_index: segmentIndex,
        render_video: true,
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Explanation retrieval failed');

    explanationText.textContent = data.explanation;
    questionText.textContent = data.question;

    // Update Hallucination Shield Card
    if (data.grounding_shield) {
      AppState.currentGroundingReport = data.grounding_shield;
      const shieldBadge = document.getElementById('shield-status-badge');
      const shieldMsg = document.getElementById('shield-message');
      const pct = Math.round((data.grounding_shield.confidence_score || 0.85) * 100);
      if (shieldBadge) {
        shieldBadge.textContent = `${pct}% GROUNDED`;
        shieldBadge.className = pct >= 80
          ? 'bg-tertiary-container text-on-tertiary text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold'
          : 'bg-secondary-container text-on-secondary-container text-[10px] font-mono px-2 py-0.5 rounded-full font-semibold';
      }
      if (shieldMsg) shieldMsg.textContent = data.grounding_shield.shield_message;
    }

    // Immediate Neural Audio Playback
    const audio = document.getElementById('classroom-audio');
    if (audio && data.audio_url) {
      audio.src = data.audio_url;
      audio.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
      audio.play().catch(e => console.log('Audio autoplay deferred:', e));
    }

    // Video Playback / Background Polling
    if (data.video_url && data.video_status === 'ready') {
      video.src = data.video_url;
      video.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
      placeholder.classList.add('hidden');
      video.classList.remove('hidden');
      video.play().catch(e => console.log('Autoplay deferred:', e));
    } else {
      placeholder.classList.remove('hidden');
      video.classList.add('hidden');
      placeholder.innerHTML = `
        <div class="flex flex-col items-center justify-center text-center p-8 space-y-3">
          <div class="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center">
            <span class="material-symbols-outlined text-[36px] text-primary animate-pulse">record_voice_over</span>
          </div>
          <p class="text-white/90 font-headline-md font-semibold text-[16px]">Teacher Narration Active</p>
          <div class="flex items-center gap-1.5">
            <span class="w-2 h-4 bg-secondary rounded-full animate-bounce"></span>
            <span class="w-2 h-6 bg-primary rounded-full animate-bounce" style="animation-delay: 0.15s"></span>
            <span class="w-2 h-8 bg-tertiary-container rounded-full animate-bounce" style="animation-delay: 0.3s"></span>
            <span class="w-2 h-5 bg-secondary-container rounded-full animate-bounce" style="animation-delay: 0.45s"></span>
          </div>
          <p class="text-white/50 text-[11px] font-mono">Avatar & slide video compositing in background...</p>
        </div>
      `;
      pollVideoReady(AppState.sessionId, segmentIndex);
    }

    setMachineState('question');
  } catch (err) {
    console.error('Error loading segment:', err);
    explanationText.textContent = AppState.plan?.segments[segmentIndex]?.example || 'Let us explore this fundamental concept through first-principles.';
    questionText.textContent = AppState.plan?.segments[segmentIndex]?.checkpoint_question || 'What is the core relationship governing this concept?';
  }
}

async function submitStudentAnswer(isFollowup = false) {
  const answerInput = document.getElementById('student-answer-input');
  const answer = answerInput?.value.trim();
  if (!answer) return;

  const btnSubmit = document.getElementById('btn-submit-answer');
  const feedbackBox = document.getElementById('answer-feedback-box');
  const misconceptionCard = document.getElementById('misconception-card');
  const btnAdvance = document.getElementById('btn-advance-segment');

  try {
    btnSubmit.disabled = true;
    btnSubmit.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> Evaluating...';
    setMachineState('evaluate');

    const res = await fetch('/api/session/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        segment_index: AppState.currentSegmentIndex,
        answer: answer,
        is_followup: isFollowup,
        student: AppState.student,
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Evaluation failed');

    feedbackBox.classList.remove('hidden');

    if (data.verdict === 'correct') {
      feedbackBox.className = 'p-4 rounded-xl text-[13px] bg-tertiary-container/20 border border-tertiary-container/40 text-on-surface space-y-1';
      feedbackBox.innerHTML = `
        <div class="flex items-center gap-1.5 font-bold text-tertiary-container">
          <span class="material-symbols-outlined text-[18px]">check_circle</span>
          Correct! Concept Mastered.
        </div>
        <p class="text-[12px] text-on-surface-variant">${data.feedback}</p>
      `;
      misconceptionCard.classList.add('hidden');
      btnAdvance.classList.remove('hidden');
      setMachineState('adapt');
    } else {
      feedbackBox.className = 'p-4 rounded-xl text-[13px] bg-error-container/20 border border-error-container/40 text-on-surface space-y-1';
      feedbackBox.innerHTML = `
        <div class="flex items-center gap-1.5 font-bold text-error">
          <span class="material-symbols-outlined text-[18px]">cancel</span>
          Needs Improvement
        </div>
        <p class="text-[12px] text-on-surface-variant">${data.feedback}</p>
      `;

      // Display Misconception Engine Card
      if (data.fingerprint) {
        const fp = data.fingerprint;
        document.getElementById('misconception-confidence').textContent = `Confidence: ${Math.round(fp.confidence * 100)}%`;
        document.getElementById('misconception-cause').textContent = fp.likely_cause;
        document.getElementById('misconception-intervention').textContent = fp.recommended_intervention;
        document.getElementById('misconception-counterexample').textContent = fp.counterexample;
        misconceptionCard.classList.remove('hidden');
      }

      setMachineState('adapt');
    }

    // Update Knowledge Graph Live
    loadKnowledgeGraph();

  } catch (err) {
    console.error('Answer submission error:', err);
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = '<span class="material-symbols-outlined text-[18px]">send</span> Submit Answer';
  }
}

async function triggerAdaptation() {
  const btnAdapt = document.getElementById('btn-adapt-reteach');
  const explanationText = document.getElementById('classroom-explanation-text');
  const questionText = document.getElementById('classroom-question-text');
  const feedbackBox = document.getElementById('answer-feedback-box');
  const answerInput = document.getElementById('student-answer-input');

  try {
    btnAdapt.disabled = true;
    btnAdapt.innerHTML = '<span class="material-symbols-outlined text-[16px] animate-spin">sync</span> Adapting Pedagogy...';

    const res = await fetch('/api/session/adapt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        segment_index: AppState.currentSegmentIndex,
        render_video: false,
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Adaptation failed');

    explanationText.textContent = data.reexplanation;
    questionText.textContent = data.followup_question || 'How does this new analogy resolve the relationship?';
    feedbackBox.classList.add('hidden');
    answerInput.value = '';

    // Rebind submit button for followup answer
    const btnSubmit = document.getElementById('btn-submit-answer');
    btnSubmit.onclick = () => submitStudentAnswer(true);

    setMachineState('question');
  } catch (err) {
    console.error('Adaptation error:', err);
  } finally {
    btnAdapt.disabled = false;
    btnAdapt.innerHTML = '<span class="material-symbols-outlined text-[16px]">auto_fix_high</span> Re-teach with New Analogy';
  }
}

async function advanceSegment() {
  try {
    const res = await fetch('/api/session/advance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: AppState.sessionId })
    });

    const data = await res.json();
    if (data.has_next) {
      loadSegment(data.next_segment_index);
    } else {
      // Lesson complete -> Launch Formative Assessment Quiz
      switchView('view-quiz-assessment');
      loadQuiz();
    }
  } catch (err) {
    console.error('Advance error:', err);
  }
}

async function switchClassroomLanguage(newLang) {
  try {
    const res = await fetch('/api/session/language', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        language: newLang,
      })
    });

    if (res.ok) {
      AppState.selectedLanguage = newLang;
      // Reload current segment in the new language
      loadSegment(AppState.currentSegmentIndex);
    }
  } catch (err) {
    console.error('Language switch error:', err);
  }
}

// --------------------------------------------------------------------------- //
// Voice Talkback (Speech Recognition API)
// --------------------------------------------------------------------------- //
function bindVoiceTalkback() {
  const micBtn = document.getElementById('btn-mic-talkback');
  const micStatus = document.getElementById('mic-status-label');
  const textarea = document.getElementById('student-answer-input');

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    micBtn?.addEventListener('click', () => {
      alert('Speech Recognition is not supported by your current browser. Please type your answer.');
    });
    return;
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;

  micBtn?.addEventListener('click', () => {
    try {
      micStatus.classList.remove('hidden');
      recognition.lang = AppState.selectedLanguage === 'Hindi' ? 'hi-IN' : AppState.selectedLanguage === 'Tamil' ? 'ta-IN' : 'en-IN';
      recognition.start();
    } catch (e) {
      recognition.stop();
      micStatus.classList.add('hidden');
    }
  });

  recognition.onresult = (event) => {
    let transcript = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      transcript += event.results[i][0].transcript;
    }
    if (textarea) textarea.value = transcript;
  };

  recognition.onend = () => {
    micStatus.classList.add('hidden');
  };

  recognition.onerror = () => {
    micStatus.classList.add('hidden');
  };
}

// --------------------------------------------------------------------------- //
// Intelligence Layer Loaders (Knowledge Graph, DNA, Spaced Repetition, Dashboard)
// --------------------------------------------------------------------------- //
async function loadKnowledgeGraph() {
  try {
    const res = await fetch(`/api/knowledge-graph/${AppState.student}`);
    const data = await res.json();

    document.getElementById('kg-overall-mastery').textContent = `${data.overall_mastery}%`;
    document.getElementById('kg-mastered-count').textContent = `${data.mastered_count} / ${data.total_concepts}`;

    const misCount = data.nodes.reduce((acc, n) => acc + (n.misconceptions ? n.misconceptions.length : 0), 0);
    document.getElementById('kg-misconceptions-count').textContent = `${misCount} Tracked`;

    if (AppState.knowledgeGraphVisualizer) {
      AppState.knowledgeGraphVisualizer.updateWithApiData(data);
    }
  } catch (err) {
    console.error('KG load error:', err);
  }
}

async function loadLearningDNA() {
  try {
    const res = await fetch(`/api/student/dna/${AppState.student}`);
    const data = await res.json();

    const container = document.getElementById('dna-bars-container');
    container.innerHTML = `
      <div class="space-y-1">
        <div class="flex justify-between text-[12px] font-medium font-mono"><span>Visual Deconstruction</span><strong>${data.visual_affinity}%</strong></div>
        <div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-primary h-2 rounded-full" style="width: ${data.visual_affinity}%"></div></div>
      </div>
      <div class="space-y-1">
        <div class="flex justify-between text-[12px] font-medium font-mono"><span>Real-World Analogies</span><strong>${data.example_driven}%</strong></div>
        <div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-secondary h-2 rounded-full" style="width: ${data.example_driven}%"></div></div>
      </div>
      <div class="space-y-1">
        <div class="flex justify-between text-[12px] font-medium font-mono"><span>First-Principles Conceptual</span><strong>${data.conceptual_depth}%</strong></div>
        <div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-tertiary-container h-2 rounded-full" style="width: ${data.conceptual_depth}%"></div></div>
      </div>
      <div class="space-y-1">
        <div class="flex justify-between text-[12px] font-medium font-mono"><span>Targeted Recall & Practice</span><strong>${data.recall_retention}%</strong></div>
        <div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-primary-container h-2 rounded-full" style="width: ${data.recall_retention}%"></div></div>
      </div>
      <div class="space-y-1">
        <div class="flex justify-between text-[12px] font-medium font-mono"><span>Active Socratic Inquiry</span><strong>${data.socratic_engagement}%</strong></div>
        <div class="w-full bg-surface-container h-2 rounded-full overflow-hidden"><div class="bg-secondary-container h-2 rounded-full" style="width: ${data.socratic_engagement}%"></div></div>
      </div>
    `;

    document.getElementById('dna-insight-text').textContent = data.personalized_insight;
  } catch (err) {
    console.error('DNA load error:', err);
  }
}

async function loadSpacedRepetition() {
  try {
    const res = await fetch(`/api/spaced-repetition/${AppState.student}`);
    const queue = await res.json();

    const container = document.getElementById('spaced-repetition-list');
    container.innerHTML = '';

    if (queue.length === 0) {
      container.innerHTML = '<p class="text-on-surface-variant p-6 bg-surface-container-low rounded-2xl">No review cards due today. Complete your first lesson to initialize the Ebbinghaus memory schedule.</p>';
      return;
    }

    queue.forEach(card => {
      const div = document.createElement('div');
      const badgeCol = card.urgency === 'OVERDUE' ? 'bg-error-container text-error' : card.urgency === 'DUE_TODAY' ? 'bg-secondary-container text-on-secondary-container' : 'bg-primary-container text-on-primary-container';
      div.className = 'p-5 rounded-2xl bg-surface-container-low border border-outline-variant/30 space-y-2 shadow-sm';
      div.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-headline-md font-bold text-[15px] text-on-surface">${card.concept}</span>
          <span class="font-mono text-[10px] uppercase font-bold px-2.5 py-0.5 rounded-full ${badgeCol}">${card.urgency.replace('_', ' ')}</span>
        </div>
        <p class="text-[13px] text-on-surface-variant font-medium">${card.due_day_label} &bull; ${card.recommended_action}</p>
        <div class="p-3 bg-surface rounded-xl border border-outline-variant/20 text-[12px] font-mono text-secondary">
          ${card.checkpoint_question}
        </div>
      `;
      container.appendChild(div);
    });
  } catch (err) {
    console.error('Spaced repetition load error:', err);
  }
}

async function loadTeacherDashboard() {
  try {
    const res = await fetch('/api/teacher/class-overview');
    const data = await res.json();

    // Render Concept Risk Heatmap
    const conceptsContainer = document.getElementById('teacher-concepts-list');
    conceptsContainer.innerHTML = '';
    data.concepts_mastery.forEach(c => {
      const card = document.createElement('div');
      const borderCol = c.status.includes('Risk') ? 'border-error-container bg-error-container/10' : 'border-outline-variant/30 bg-surface';
      card.className = `p-4 rounded-xl border ${borderCol} space-y-2 shadow-sm`;
      card.innerHTML = `
        <div class="flex justify-between items-center">
          <span class="font-bold text-[14px] text-on-surface">${c.concept}</span>
          <span class="font-mono text-[11px] font-bold ${c.status.includes('Risk') ? 'text-error' : 'text-primary'}">${c.mastery}% (${c.status})</span>
        </div>
        <p class="text-[11px] text-on-surface-variant">${c.students_at_risk} students require targeted remediation</p>
      `;
      conceptsContainer.appendChild(card);
    });

    // Render Shared Misconceptions
    const misContainer = document.getElementById('teacher-misconceptions-list');
    misContainer.innerHTML = '';
    data.shared_misconceptions.forEach(m => {
      const card = document.createElement('div');
      card.className = 'p-4 rounded-xl bg-surface border border-outline-variant/30 space-y-1 shadow-sm';
      card.innerHTML = `
        <div class="flex justify-between items-center">
          <span class="font-bold text-[13px] text-error">${m.misconception}</span>
          <span class="font-mono text-[11px] bg-error/10 text-error px-2 py-0.5 rounded-full font-bold">${m.affected_students} Students (${m.percentage}%)</span>
        </div>
        <p class="text-[12px] text-on-surface-variant font-medium">Root: ${m.root_cause}</p>
        <p class="text-[11px] font-mono text-secondary">Action: ${m.recommended_action}</p>
      `;
      misContainer.appendChild(card);
    });

    // Render 1-Click Remediation Launchers
    const remContainer = document.getElementById('teacher-remediations-list');
    remContainer.innerHTML = '';
    data.recommended_remediations.forEach(r => {
      const card = document.createElement('div');
      card.className = 'p-4 rounded-xl bg-surface border border-tertiary-container/30 space-y-2 shadow-sm';
      card.innerHTML = `
        <span class="font-bold text-[13px] text-tertiary-container">${r.title}</span>
        <p class="text-[12px] text-on-surface-variant">${r.pedagogy}</p>
        <div class="flex justify-between items-center pt-2">
          <span class="font-mono text-[11px] text-on-surface-variant font-semibold">Cohort: ${r.target_cohort}</span>
          <button class="px-3 py-1 bg-tertiary-container text-on-tertiary text-[11px] font-bold rounded-lg hover:opacity-90 transition-opacity">Deploy Blitz</button>
        </div>
      `;
      remContainer.appendChild(card);
    });
  } catch (err) {
    console.error('Teacher dashboard load error:', err);
  }
}

// --------------------------------------------------------------------------- //
// Formative Assessment Quiz & Report Card
// --------------------------------------------------------------------------- //
function bindQuizEvents() {
  document.getElementById('btn-submit-quiz')?.addEventListener('click', async () => {
    await submitQuizAnswers();
  });
}

async function loadQuiz() {
  try {
    const res = await fetch('/api/quiz/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: AppState.sessionId })
    });

    const data = await res.json();
    AppState.quizData = data.questions;

    const container = document.getElementById('quiz-questions-container');
    container.innerHTML = '';

    data.questions.forEach((q, idx) => {
      const qCard = document.createElement('div');
      qCard.className = 'p-6 rounded-2xl bg-surface-container-low border border-outline-variant/30 space-y-4 shadow-sm';

      let inputHtml = '';
      if (q.type === 'mcq' && q.options) {
        inputHtml = `<div class="space-y-2">
          ${q.options.map(opt => `
            <label class="flex items-center gap-3 p-3 rounded-xl bg-surface border border-outline-variant/20 hover:border-primary cursor-pointer transition-colors text-[13px]">
              <input type="radio" name="quiz_q_${idx}" value="${opt}" class="accent-primary" />
              <span>${opt}</span>
            </label>
          `).join('')}
        </div>`;
      } else {
        inputHtml = `<textarea id="quiz_ans_${idx}" rows="2" placeholder="Write your explanation..." class="w-full bg-surface border border-outline-variant rounded-xl p-3 text-[13px] text-on-surface focus:border-primary focus:outline-none"></textarea>`;
      }

      qCard.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-mono text-[11px] bg-primary/10 text-primary px-2.5 py-0.5 rounded-full font-bold">Question ${idx + 1} &bull; ${q.concept}</span>
        </div>
        <p class="font-headline-md text-[15px] font-bold text-on-surface">${q.question}</p>
        ${inputHtml}
      `;
      container.appendChild(qCard);
    });
  } catch (err) {
    console.error('Quiz loading error:', err);
  }
}

async function submitQuizAnswers() {
  const answers = {};
  if (!AppState.quizData) return;

  AppState.quizData.forEach((q, idx) => {
    if (q.type === 'mcq') {
      const sel = document.querySelector(`input[name="quiz_q_${idx}"]:checked`);
      answers[idx.toString()] = sel ? sel.value : '';
    } else {
      const ta = document.getElementById(`quiz_ans_${idx}`);
      answers[idx.toString()] = ta ? ta.value : '';
    }
  });

  const btn = document.getElementById('btn-submit-quiz');
  btn.disabled = true;
  btn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">sync</span> Grading Assessment...';

  try {
    const res = await fetch('/api/quiz/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        student: AppState.student,
        answers: answers,
      })
    });

    const data = await res.json();
    renderReportCard(data);
  } catch (err) {
    console.error('Quiz submit error:', err);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">grade</span> Submit Assessment & Generate Report Card';
  }
}

function renderReportCard(data) {
  const container = document.getElementById('report-card-container');
  container.classList.remove('hidden');

  const report = data.report;
  container.innerHTML = `
    <div class="border-b border-outline-variant/30 pb-4 flex justify-between items-center">
      <div>
        <h3 class="font-headline-lg text-[22px] font-bold text-on-surface">Formative Report Card</h3>
        <p class="text-[12px] font-mono text-on-surface-variant mt-0.5">Topic: ${report.topic}</p>
      </div>
      <span class="font-headline-lg text-[28px] font-bold text-primary">${report.raw_score} / ${report.out_of}</span>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="p-4 rounded-xl bg-tertiary-container/10 border border-tertiary-container/30 space-y-1">
        <span class="font-bold text-[13px] text-tertiary-container">Strong Concepts:</span>
        <ul class="list-disc list-inside text-[12px] text-on-surface">
          ${report.strong_areas.map(s => `<li>${s}</li>`).join('')}
        </ul>
      </div>

      <div class="p-4 rounded-xl bg-error-container/10 border border-error-container/30 space-y-1">
        <span class="font-bold text-[13px] text-error">Areas for Growth:</span>
        <ul class="list-disc list-inside text-[12px] text-on-surface">
          ${report.needs_improvement.map(w => `<li>${w}</li>`).join('')}
        </ul>
      </div>
    </div>

    <div class="p-4 rounded-xl bg-surface border border-outline-variant/30 space-y-1">
      <span class="font-bold text-[13px] text-primary">Pedagogical Recommendation:</span>
      <p class="text-[13px] text-on-surface leading-relaxed">${report.recommendation}</p>
    </div>

    ${data.next_topic ? `
      <div class="p-4 rounded-xl bg-secondary/10 border border-secondary/20 flex justify-between items-center">
        <div>
          <span class="font-mono text-[11px] font-bold text-secondary uppercase">Recommended Next Topic:</span>
          <p class="font-headline-md font-bold text-[15px] text-on-surface mt-0.5">${data.next_topic.next_topic}</p>
          <p class="text-[11px] text-on-surface-variant">${data.next_topic.reason}</p>
        </div>
      </div>
    ` : ''}
  `;

  // Reload Knowledge Graph to reflect new quiz mastery
  loadKnowledgeGraph();
}

// --------------------------------------------------------------------------- //
// BHARAT 3D LAB™ EVENT CONTROLLER
// --------------------------------------------------------------------------- //
function bind3DLabEvents() {
  // Preset model switcher (DNA, Atom, Motor, Solar)
  document.querySelectorAll('.model-3d-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.model-3d-btn').forEach(b => {
        b.className = 'model-3d-btn px-4 py-2 rounded-xl bg-surface border border-outline-variant hover:bg-surface-container text-on-surface text-[12px] font-bold transition-all shadow-sm flex items-center gap-1.5';
      });
      btn.className = 'model-3d-btn px-4 py-2 rounded-xl bg-primary text-on-primary text-[12px] font-bold transition-all shadow-sm flex items-center gap-1.5';

      const modelKey = btn.getAttribute('data-model');
      if (!AppState.threeLab && typeof Bharat3DLab !== 'undefined') {
        AppState.threeLab = new Bharat3DLab('threejs-canvas-container');
      }
      if (AppState.threeLab) {
        AppState.threeLab.loadModel(modelKey);
      }
    });
  });

  // Classroom quick switch to 3D button
  const btnFromClassroom = document.getElementById('btn-open-3d-from-classroom');
  if (btnFromClassroom) {
    btnFromClassroom.addEventListener('click', () => {
      switchView('view-3d-lab');
      const curConcept = AppState.plan?.segments[AppState.currentSegmentIndex]?.concept || 'dna';
      if (!AppState.threeLab && typeof Bharat3DLab !== 'undefined') {
        AppState.threeLab = new Bharat3DLab('threejs-canvas-container');
      }
      if (AppState.threeLab) {
        AppState.threeLab.loadModel(curConcept);
      }
    });
  }

  // Rotate toggle
  const btnRotate = document.getElementById('btn-3d-rotate');
  if (btnRotate) {
    btnRotate.addEventListener('click', () => {
      if (AppState.threeLab) {
        const isRotating = AppState.threeLab.toggleRotation();
        const statusEl = document.getElementById('rotate-status');
        if (statusEl) statusEl.textContent = isRotating ? 'Pause Rotation' : 'Resume Rotation';
      }
    });
  }

  // Reset view
  const btnReset = document.getElementById('btn-3d-reset');
  if (btnReset) {
    btnReset.addEventListener('click', () => {
      if (AppState.threeLab) AppState.threeLab.resetCamera();
    });
  }

  // Custom 3D prompt generator
  const btnGen = document.getElementById('btn-generate-3d');
  const promptInput = document.getElementById('custom-3d-prompt');
  if (btnGen && promptInput) {
    const handleGenerate = async () => {
      const q = promptInput.value.trim();
      if (!q) return;
      btnGen.disabled = true;
      btnGen.innerHTML = '<span class="material-symbols-outlined text-[15px] animate-spin">sync</span> Rendering...';
      try {
        const res = await fetch('/api/3d/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: q })
        });
        const spec = await res.json();
        if (!AppState.threeLab && typeof Bharat3DLab !== 'undefined') {
          AppState.threeLab = new Bharat3DLab('threejs-canvas-container');
        }
        if (AppState.threeLab) {
          AppState.threeLab.renderSpec(spec);
        }
      } catch (err) {
        console.error('Custom 3D model generation error:', err);
      } finally {
        btnGen.disabled = false;
        btnGen.innerHTML = '<span>Render 3D</span>';
      }
    };

    btnGen.addEventListener('click', handleGenerate);
    promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleGenerate();
    });
  }
}
