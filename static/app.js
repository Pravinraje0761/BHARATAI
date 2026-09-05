/**
 * BHARATGURU Frontend State Machine Controller
 * Orchestrates adaptive teaching, voice talkback, misconception fingerprinting,
 * knowledge graph modeling, and institutional analytics.
 */

// Session-expiry guard: every API route in this app now requires a signed-in
// session (cookie or Bearer token). If any call comes back 401, the session
// cookie has expired or been revoked server-side — bounce to the login page
// instead of leaving the SPA stuck showing stale/broken state.
(function guardSessionExpiry() {
  const originalFetch = window.fetch.bind(window);
  window.fetch = async function (...args) {
    const res = await originalFetch(...args);
    if (res.status === 401) {
      window.location.href = '/login.html';
    }
    return res;
  };
})();

// Global Application State
const AppState = {
  currentView: 'view-upload-material',
  activeMachineState: 'understand',
  sessionId: null,
  plan: null,
  currentSegmentIndex: 0,
  uploadedFiles: [],
  isDemoPreloadedFile: false,
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
  user: null,
  token: null,
  credits: parseInt(localStorage.getItem('bharat_credits') || '100'),
  productionTier: 'express', // 'express' (1 credit) | 'realistic' (5 credits)
  isDemoUser: false,
};

function updateCreditsUI() {
  const countEl = document.getElementById('user-credits-count');
  if (countEl) countEl.textContent = AppState.credits;
  const badge = document.getElementById('user-credits-badge');
  if (badge) {
    badge.classList.remove('scale-105');
    void badge.offsetWidth;
    badge.classList.add('scale-105', 'transition-transform');
    setTimeout(() => badge.classList.remove('scale-105'), 300);
  }
}

function deductCredits(amount) {
  AppState.credits = Math.max(0, AppState.credits - amount);
  localStorage.setItem('bharat_credits', AppState.credits.toString());
  updateCreditsUI();
}

document.addEventListener('DOMContentLoaded', () => {
  updateCreditsUI();
  initAuth();
  initFirebaseAnalytics();
  initAccessibility();
  bindNavigationEvents();
  bindPresetEvents();
  bindUploadEvents();
  bindClassroomEvents();
  bindVoiceTalkback();
  bindQuizEvents();
  bind3DLabEvents();

  // Initialize Knowledge Graph Canvas (clean slate by default).
  AppState.knowledgeGraphVisualizer = new KnowledgeGraphVisualizer('knowledge-graph-canvas');

  // Enforce Clean Slate / Demo user policy
  initCleanSlateOrDemo();

  // Set default view
  switchView('view-upload-material');
  setMachineState('understand');
});

// --------------------------------------------------------------------------- //
// Firebase Web SDK & Google Analytics
// --------------------------------------------------------------------------- //
async function initFirebaseAnalytics() {
  try {
    const res = await fetch('/api/firebase/config');
    if (!res.ok) return;
    const cfg = await res.json();
    if (cfg?.apiKey && window.firebase) {
      if (!firebase.apps.length) {
        firebase.initializeApp(cfg);
      }
      if (firebase.analytics && cfg.measurementId) {
        try {
          window.firebaseAnalytics = firebase.analytics();
          console.log('[FIREBASE] Google Analytics active:', cfg.measurementId);
        } catch (e) {
          console.warn('[FIREBASE] Analytics notice:', e);
        }
      }
    }
  } catch (e) {
    // Non-blocking telemetry
  }
}

// --------------------------------------------------------------------------- //
// User Authentication & Session Management
// --------------------------------------------------------------------------- //
async function initAuth() {
  const token = localStorage.getItem('bharat_token');
  const unauthContainer = document.getElementById('auth-unauthenticated');
  const authContainer = document.getElementById('auth-authenticated');
  const btnUserMenu = document.getElementById('btn-user-menu');
  const dropdownMenu = document.getElementById('user-dropdown-menu');
  const btnLogout = document.getElementById('btn-header-logout');

  // Toggle user dropdown
  btnUserMenu?.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdownMenu?.classList.toggle('hidden');
  });

  // Close dropdown on outside click
  document.addEventListener('click', (e) => {
    if (!dropdownMenu?.contains(e.target) && !btnUserMenu?.contains(e.target)) {
      dropdownMenu?.classList.add('hidden');
    }
  });

  // Quick switch links in dropdown
  document.getElementById('link-my-classroom')?.addEventListener('click', (e) => {
    e.preventDefault();
    dropdownMenu?.classList.add('hidden');
    switchView('view-upload-material');
  });

  document.getElementById('link-teacher-dashboard')?.addEventListener('click', (e) => {
    e.preventDefault();
    dropdownMenu?.classList.add('hidden');
    switchView('view-teacher-dashboard');
  });

  // Logout handler
  btnLogout?.addEventListener('click', async () => {
    if (AppState.token) {
      try {
        await fetch('/api/auth/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${AppState.token}` },
        });
      } catch (err) {
        console.error('Logout error:', err);
      }
    }
    localStorage.removeItem('bharat_token');
    localStorage.removeItem('bharat_user');
    localStorage.removeItem('bharat_demo_user');
    AppState.token = null;
    AppState.user = null;
    AppState.student = 'student1';
    AppState.isDemoUser = false;
    enforceCleanSlate();
    window.location.href = '/login.html';
  });

  if (!token) {
    unauthContainer?.classList.remove('hidden');
    authContainer?.classList.add('hidden');
    initCleanSlateOrDemo();
    return;
  }

  // Verify token with backend
  try {
    const res = await fetch('/api/auth/me', {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (res.ok) {
      const data = await res.json();
      AppState.user = data.user;
      AppState.token = token;
      AppState.student = data.user.username;

      // Update UI elements
      unauthContainer?.classList.add('hidden');
      authContainer?.classList.remove('hidden');

      const nameEl = document.getElementById('user-display-name');
      const roleEl = document.getElementById('user-role-badge');
      const avatarEl = document.getElementById('user-avatar-badge');
      const dropUserEl = document.getElementById('dropdown-username');
      const dropEmailEl = document.getElementById('dropdown-email');
      const studentInput = document.getElementById('student-name-input');

      if (nameEl) nameEl.textContent = data.user.full_name || data.user.username;
      if (roleEl) roleEl.textContent = `${data.user.role === 'teacher' ? 'Faculty' : 'Student'} • ${data.user.grade_or_board || 'CBSE 10'}`;
      if (avatarEl) {
        const rawAvatar = data.user.avatar_url;
        const defaultEmoji = data.user.role === 'teacher' ? '👩‍🏫' : '👨‍🎓';
        if (rawAvatar && (rawAvatar.startsWith('http://') || rawAvatar.startsWith('https://'))) {
          avatarEl.innerHTML = `<img src="${rawAvatar}" alt="avatar" class="w-full h-full object-cover rounded-full" onerror="this.outerHTML='<span>${defaultEmoji}</span>'"/>`;
        } else {
          avatarEl.textContent = rawAvatar || defaultEmoji;
        }
      }
      if (dropUserEl) dropUserEl.textContent = data.user.username;
      if (dropEmailEl) dropEmailEl.textContent = data.user.email || `${data.user.username}@bharatguru.edu`;

      // Check if Demo Student or Demo Teacher vs Clean Slate User
      const isDemo = localStorage.getItem('bharat_demo_user') || (data.user.username === 'aarav' || data.user.username === 'priya');
      if (isDemo && (data.user.username === 'aarav' || localStorage.getItem('bharat_demo_user') === 'student_demo')) {
        AppState.isDemoUser = true;
        preloadStudentDemoData();
      } else if (isDemo && (data.user.username === 'priya' || localStorage.getItem('bharat_demo_user') === 'teacher_demo')) {
        AppState.isDemoUser = true;
      } else {
        AppState.isDemoUser = false;
        enforceCleanSlate();
        if (studentInput) studentInput.value = data.user.username;
      }

      // Role-Based UI Isolation (Student vs Teacher)
      const role = data.user.role || 'student';
      const teacherTabs = document.querySelectorAll('[data-role="teacher-only"]');
      const roleSwitchBtn = document.getElementById('btn-quick-role-switch');
      const roleSwitchLabel = document.getElementById('role-switch-label');

      if (roleSwitchBtn) {
        roleSwitchBtn.classList.remove('hidden');
        roleSwitchBtn.classList.add('flex');
        if (role === 'teacher') {
          roleSwitchLabel.textContent = 'Switch to Student View';
          roleSwitchBtn.title = 'Instant Swap: View App as Demo Student (Aarav Patel)';
        } else {
          roleSwitchLabel.textContent = 'Switch to Teacher View';
          roleSwitchBtn.title = 'Instant Swap: View App as Demo Teacher (Dr. Priya Sharma)';
        }
      }

      if (role === 'teacher') {
        teacherTabs.forEach((tab) => tab.classList.remove('hidden'));
        if (AppState.currentView === 'view-upload-material') {
          switchView('view-teacher-dashboard');
        }
      } else {
        // Strictly hide teacher tabs and cohort analytics from students
        teacherTabs.forEach((tab) => tab.classList.add('hidden'));
        if (AppState.currentView === 'view-teacher-dashboard') {
          switchView('view-upload-material');
        }
      }

      // If user is teacher and URL contains teacher hash, switch view
      if (data.user.role === 'teacher' && window.location.hash.includes('teacher')) {
        switchView('view-teacher-dashboard');
      }
    } else {
      localStorage.removeItem('bharat_token');
      localStorage.removeItem('bharat_user');
      unauthContainer?.classList.remove('hidden');
      authContainer?.classList.add('hidden');
      initCleanSlateOrDemo();
    }
  } catch (err) {
    console.warn('Auth check skipped:', err);
    initCleanSlateOrDemo();
  }

  // Bind Quick Role Switcher Button
  const roleSwitchBtn = document.getElementById('btn-quick-role-switch');
  if (roleSwitchBtn && !roleSwitchBtn._bound) {
    roleSwitchBtn._bound = true;
    roleSwitchBtn.addEventListener('click', async () => {
      const targetRole = (AppState.user?.role === 'teacher') ? 'student' : 'teacher';
      try {
        const res = await fetch('/api/auth/demo-login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ role: targetRole }),
        });
        const d = await res.json();
        if (d.token && d.user) {
          localStorage.setItem('bharat_token', d.token);
          localStorage.setItem('bharat_user', JSON.stringify(d.user));
          AppState.token = d.token;
          AppState.user = d.user;
          AppState.student = d.user.username;
          if (targetRole === 'teacher') {
            localStorage.setItem('bharat_demo_user', 'teacher_demo');
            AppState.isDemoUser = true;
            await initAuth();
            switchView('view-teacher-dashboard');
          } else {
            localStorage.setItem('bharat_demo_user', 'student_demo');
            AppState.isDemoUser = true;
            await initAuth();
            preloadStudentDemoData();
            switchView('view-upload-material');
          }
        }
      } catch (e) {
        console.error('Role switch failed:', e);
      }
    });
  }
}

function initCleanSlateOrDemo() {
  const isDemo = localStorage.getItem('bharat_demo_user');
  if (isDemo === 'student_demo' || (AppState.user && AppState.user.username === 'aarav')) {
    AppState.isDemoUser = true;
    preloadStudentDemoData();
  } else if (isDemo === 'teacher_demo' || (AppState.user && AppState.user.username === 'priya')) {
    AppState.isDemoUser = true;
  } else {
    AppState.isDemoUser = false;
    enforceCleanSlate();
  }
}

function enforceCleanSlate() {
  const topicInput = document.getElementById('topic-input');
  if (topicInput) topicInput.value = '';
  const instructionInput = document.getElementById('instruction-input');
  if (instructionInput) instructionInput.value = '';
  const studentInput = document.getElementById('student-name-input');
  if (studentInput && (!AppState.user || AppState.user.username === 'aarav' || AppState.user.username === 'priya')) {
    studentInput.value = '';
  }
  AppState.uploadedFiles = [];
  AppState.isDemoPreloadedFile = false;
  const filesContainer = document.getElementById('uploaded-files-list');
  if (filesContainer) filesContainer.innerHTML = '';
}

async function preloadStudentDemoData() {
  const studentInput = document.getElementById('student-name-input');
  if (studentInput) studentInput.value = 'Aarav Patel';

  const topicInput = document.getElementById('topic-input');
  if (topicInput) topicInput.value = "CBSE Class 10: Electricity & Ohm's Law";

  const instructionInput = document.getElementById('instruction-input');
  if (instructionInput) instructionInput.value = "CBSE Board Preparation, 20-minute conceptual depth with diagrams & circuit formulas";

  // Attach the real bundled sample chapter (not a fabricated filename) so a
  // lesson plan build has an actual file to ingest.
  try {
    const res = await fetch('/api/sample-files');
    const files = await res.json();
    if (files && files.length > 0) {
      AppState.uploadedFiles = [files[0].path];
      AppState.isDemoPreloadedFile = true;
      const filesContainer = document.getElementById('uploaded-files-list');
      if (filesContainer) {
        filesContainer.innerHTML = '';
        renderUploadedFiles([{
          name: files[0].name,
          size_bytes: files[0].size_bytes,
          is_valid: true,
        }]);
      }
    }
  } catch (err) {
    console.error('Demo sample preload error:', err);
  }

  if (AppState.knowledgeGraphVisualizer) {
    AppState.knowledgeGraphVisualizer.loadDemoCurriculum();
  }
  const kgMastery = document.getElementById('kg-overall-mastery');
  const kgCount = document.getElementById('kg-mastered-count');
  const kgMis = document.getElementById('kg-misconceptions-count');
  if (kgMastery) kgMastery.textContent = '82%';
  if (kgCount) kgCount.textContent = '4 / 7';
  if (kgMis) kgMis.textContent = '1 Tracked';
}

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
  // Role isolation: block students from accessing teacher dashboard
  if (viewId === 'view-teacher-dashboard' && AppState.user && AppState.user.role !== 'teacher') {
    alert('Access Restricted: The Teacher Dashboard and class cohort diagnostics are accessible to faculty and educators only.');
    viewId = 'view-upload-material';
  }

  // Classroom and quiz only mean anything once a lesson plan exists.
  if ((viewId === 'view-live-classroom' || viewId === 'view-quiz-assessment') && !AppState.sessionId) {
    alert('Build a lesson plan first — upload material or enter a topic, then click "Build Adaptive Lesson Plan".');
    viewId = 'view-upload-material';
  }

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
    'view-quiz-assessment',
    'view-lesson-completed'
  ];

  viewSections.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      if (id === viewId) {
        el.classList.remove('hidden');
        el.classList.remove('view-enter');
        void el.offsetWidth;
        el.classList.add('view-enter');
      } else {
        el.classList.add('hidden');
        el.classList.remove('view-enter');
      }
    }
  });

  // Update nav tabs
  document.querySelectorAll('header nav a[data-target]').forEach(tab => {
    const target = tab.getAttribute('data-target');
    if (target === viewId) {
      tab.className = 'nav-tab text-[14px] text-primary font-bold border-b-2 border-primary pb-1 flex items-center gap-1';
    } else {
      tab.className = 'nav-tab text-[14px] text-on-surface-variant hover:text-primary transition-colors pb-1 flex items-center gap-1';
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
  } else if (viewId === 'view-lesson-completed') {
    renderLessonCompletionView();
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
        AppState.isDemoPreloadedFile = false;
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
  const container = document.getElementById('uploaded-files-list');

  // A demo-preloaded sample shouldn't stack behind a real upload the student
  // chose themselves — replace it instead of appending to it.
  if (AppState.isDemoPreloadedFile) {
    AppState.uploadedFiles = [];
    AppState.isDemoPreloadedFile = false;
    if (container) container.innerHTML = '';
  }

  for (const file of files) {
    const formData = new FormData();
    formData.append('file', file);

    // Show temporary uploading card
    const tempId = 'uploading-' + Date.now();
    if (container) {
      const tempDiv = document.createElement('div');
      tempDiv.id = tempId;
      tempDiv.className = 'flex items-center justify-between p-3 rounded-xl bg-surface-container-low border border-outline-variant/30 text-[13px] animate-pulse';
      tempDiv.innerHTML = `
        <div class="flex items-center gap-2 text-primary font-medium">
          <span class="material-symbols-outlined text-[20px] animate-spin">sync</span>
          <span>Analyzing & extracting text from <strong>${file.name}</strong>...</span>
        </div>
      `;
      container.appendChild(tempDiv);
    }

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      document.getElementById(tempId)?.remove();

      if (res.ok) {
        AppState.uploadedFiles.push(data.file_path);
        renderUploadedFiles([data]);

        // Auto-fill topic input if empty
        const topicEl = document.getElementById('topic-input');
        if (topicEl && data.suggested_topic && (!topicEl.value.trim() || topicEl.value === 'General topic')) {
          topicEl.value = data.suggested_topic;
          topicEl.classList.add('border-secondary', 'bg-amber-50/40');
          setTimeout(() => topicEl.classList.remove('border-secondary', 'bg-amber-50/40'), 2000);
        }
      } else {
        throw new Error(data.detail || 'Upload failed');
      }
    } catch (err) {
      document.getElementById(tempId)?.remove();
      console.error('Upload error:', err);
      if (container) {
        const errDiv = document.createElement('div');
        errDiv.className = 'p-3 rounded-xl bg-red-50 text-red-700 border border-red-200 text-[12px] flex items-center justify-between';
        errDiv.innerHTML = `<span><strong>${file.name}</strong>: ${err.message}</span>`;
        container.appendChild(errDiv);
      }
    }
  }
}

function renderUploadedFiles(files) {
  const container = document.getElementById('uploaded-files-list');
  if (!container) return;

  files.forEach(f => {
    const div = document.createElement('div');
    const isError = f.is_valid === false;
    div.className = `flex flex-col sm:flex-row sm:items-center justify-between p-3.5 rounded-2xl border text-[13px] shadow-sm transition-all gap-2 ${isError ? 'bg-amber-50/70 border-amber-300 text-amber-900' : 'bg-white border-outline-variant/40 text-on-surface hover:border-primary/40'}`;
    
    const pagesLabel = f.page_count ? `<span class="px-2 py-0.5 rounded-md bg-surface-container font-mono text-[11px] text-on-surface-variant font-semibold">📄 ${f.page_count} Pages</span>` : '';
    const wordsLabel = f.word_count ? `<span class="px-2 py-0.5 rounded-md bg-surface-container font-mono text-[11px] text-on-surface-variant font-semibold">📝 ${(f.word_count).toLocaleString()} Words</span>` : '';
    const chunksLabel = f.chunk_count ? `<span class="px-2 py-0.5 rounded-md bg-emerald-50 text-emerald-800 border border-emerald-200 font-mono text-[11px] font-semibold">⚡ ${f.chunk_count} Chunks Grounded</span>` : '';

    div.innerHTML = `
      <div class="flex items-start gap-2.5">
        <span class="material-symbols-outlined ${isError ? 'text-amber-600' : 'text-primary'} text-[22px] shrink-0 mt-0.5">
          ${isError ? 'warning' : 'description'}
        </span>
        <div class="space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="font-bold text-on-surface">${f.filename || f.name}</span>
            ${pagesLabel}
            ${wordsLabel}
            ${chunksLabel}
          </div>
          ${f.preview_snippet ? `<p class="text-[11px] text-on-surface-variant line-clamp-1 italic font-mono">"${f.preview_snippet.slice(0, 100)}..."</p>` : ''}
          ${isError ? `<p class="text-[11px] text-amber-700 font-medium">${f.error || 'Text could not be extracted'}</p>` : ''}
        </div>
      </div>
      <div class="flex items-center gap-2 shrink-0 self-end sm:self-center">
        <span class="font-mono text-[11px] text-tertiary-container font-semibold flex items-center gap-1">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
          Ready
        </span>
      </div>
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

  // Per-student identity so progress / knowledge graph / report stay separate.
  const rawName = document.getElementById('student-name-input')?.value.trim() || '';
  AppState.student = rawName
    ? rawName.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '').slice(0, 40) || 'student1'
    : (AppState.user?.username || 'student1');

  AppState.selectedLanguage = language;
  AppState.selectedTeachingMode = mode;
  AppState.selectedExamBoard = examBoard;

  // Validate Credit Balance for Chosen Production Tier
  const tierRadio = document.querySelector('input[name="production_tier"]:checked, input[name="production-tier"]:checked');
  const selectedTier = (tierRadio?.value?.includes('realistic')) ? 'realistic' : 'express';
  const tierCost = selectedTier === 'realistic' ? 5 : 1;

  if (AppState.credits < tierCost) {
    alert(`Insufficient credits! You currently have ${AppState.credits} credits, but ${tierCost} credits are required for ${selectedTier === 'realistic' ? 'Ultra Realistic Studio' : 'Express'} mode. Please choose another tier or recharge.`);
    return;
  }

  // Multi-Step Progress Modal Elements
  const modal = document.getElementById('modal-planning-progress');
  const progressFill = document.getElementById('planning-progress-fill');
  const progressPercent = document.getElementById('planning-progress-percent');
  const progressLabel = document.getElementById('planning-progress-label');

  function setPlanningStep(stepNum, percent, label) {
    if (progressFill) progressFill.style.width = percent + '%';
    if (progressPercent) progressPercent.textContent = percent + '%';
    if (progressLabel) progressLabel.textContent = label;

    for (let i = 1; i <= 4; i++) {
      const el = document.getElementById(`step-plan-${i}`);
      if (!el) continue;
      const statusIcon = el.querySelector('span:last-child');
      if (i < stepNum) {
        el.className = 'flex items-center gap-3 p-2.5 rounded-xl bg-emerald-50 text-emerald-800 border border-emerald-200 transition-all font-semibold text-[13px]';
        if (statusIcon) statusIcon.outerHTML = '<span class="material-symbols-outlined text-[18px] text-emerald-600">check_circle</span>';
      } else if (i === stepNum) {
        el.className = 'flex items-center gap-3 p-2.5 rounded-xl bg-primary/10 border border-primary/30 transition-all font-semibold text-primary text-[13px]';
        if (statusIcon) statusIcon.outerHTML = '<span class="material-symbols-outlined text-[18px] text-secondary animate-spin">progress_activity</span>';
      } else {
        el.className = 'flex items-center gap-3 p-2.5 rounded-xl text-on-surface-variant transition-all opacity-50 text-[13px]';
        if (statusIcon) statusIcon.outerHTML = '<span class="material-symbols-outlined text-[18px]">radio_button_unchecked</span>';
      }
    }
  }

  if (modal) {
    modal.classList.remove('hidden');
    setPlanningStep(1, 25, 'Phase 1 of 4: Ingesting & Grounding');
  }

  const timer1 = setTimeout(() => setPlanningStep(2, 55, 'Phase 2 of 4: Cognitive Diagnostics'), 600);
  const timer2 = setTimeout(() => setPlanningStep(3, 80, 'Phase 3 of 4: Socratic Milestones'), 1200);
  const timer3 = setTimeout(() => setPlanningStep(4, 95, 'Phase 4 of 4: 3D STEM Lab Synthesis'), 1900);

  try {
    btn.disabled = true;
    btn.innerHTML = '<span class="material-symbols-outlined text-[20px] animate-spin">sync</span> Generating Blueprint...';

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
        production_tier: selectedTier,
      })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Plan generation failed');

    // Deduct credits and save active production tier
    deductCredits(tierCost);
    AppState.productionTier = selectedTier;

    clearTimeout(timer1);
    clearTimeout(timer2);
    clearTimeout(timer3);
    setPlanningStep(5, 100, 'Complete! Loading Lesson...');

    AppState.sessionId = data.session_id;
    AppState.plan = data;
    AppState.currentSegmentIndex = 0;

    await new Promise(r => setTimeout(r, 450));
    modal?.classList.add('hidden');

    ensureNotesButton();
    renderLessonPlanPreview(data);
    switchView('view-lesson-plan');
    setMachineState('plan');

    // Update knowledge graph with returned structure
    if (data.knowledge_graph && AppState.knowledgeGraphVisualizer) {
      AppState.knowledgeGraphVisualizer.updateWithApiData(data.knowledge_graph);
    }
  } catch (err) {
    clearTimeout(timer1);
    clearTimeout(timer2);
    clearTimeout(timer3);
    modal?.classList.add('hidden');
    console.error('Error building plan:', err);
    alert('Error generating lesson plan: ' + err.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<span class="material-symbols-outlined">auto_awesome</span> Build Adaptive Lesson Plan';
  }
}

// Floating "Revision Notes" action — appears once a session exists. Opens a
// printable recap of every concept taught (kids can read it or Ctrl+P to PDF).
function ensureNotesButton() {
  if (document.getElementById('btn-revision-notes')) return;
  const btn = document.createElement('button');
  btn.id = 'btn-revision-notes';
  btn.title = 'Open a printable revision sheet of this lesson';
  btn.className = 'fixed bottom-5 right-5 z-[90] bg-secondary-container text-on-secondary-container ' +
    'font-headline-md font-bold text-[13px] px-4 py-3 rounded-full shadow-lg flex items-center gap-2 ' +
    'hover:scale-[1.03] transition-transform';
  btn.innerHTML = '<span class="material-symbols-outlined text-[18px]">menu_book</span> Revision Notes';
  btn.addEventListener('click', () => {
    if (!AppState.sessionId) return;
    window.open('/api/session/' + AppState.sessionId + '/notes?format=html', '_blank', 'noopener');
  });
  document.body.appendChild(btn);
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

  // Assign (not addEventListener) so rebuilding a plan never stacks handlers
  // and never fires loadSegment more than once.
  const btnStart = document.getElementById('btn-start-classroom');
  if (btnStart) {
    btnStart.onclick = () => {
      switchView('view-live-classroom');
      setMachineState('explain');
      loadSegment(0);
    };
  }
}

// --------------------------------------------------------------------------- //
// Live Interactive Classroom & Teaching Loop
// --------------------------------------------------------------------------- //
function bindClassroomEvents() {
  // .onclick (assign, not add) — triggerAdaptation()/loadSegment() re-point this
  // same handler between the first-attempt and follow-up answer paths, so a
  // stacked addEventListener would double-submit evaluations.
  const btnSubmitAns = document.getElementById('btn-submit-answer');
  if (btnSubmitAns) btnSubmitAns.onclick = () => submitStudentAnswer(false);
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

  // Strict Bi-Directional Video & Audio Sync
  const classroomVideo = document.getElementById('classroom-video');
  const classroomAudio = document.getElementById('classroom-audio');
  const audioVisualizer = document.getElementById('classroom-audio-visualizer');

  if (classroomVideo && !classroomVideo._syncBound) {
    classroomVideo._syncBound = true;

    // Halting video MUST halt audio immediately so it doesn't continue playing in background
    classroomVideo.addEventListener('pause', () => {
      if (classroomAudio && !classroomAudio.paused) {
        classroomAudio.pause();
      }
      if (currentDoubtAudio && !currentDoubtAudio.paused) {
        currentDoubtAudio.pause();
      }
      audioVisualizer?.classList.add('hidden');
      audioVisualizer?.classList.remove('flex');
    });

    // Resuming video halts standalone audio to avoid dual sound echo
    classroomVideo.addEventListener('play', () => {
      if (classroomAudio && !classroomAudio.paused) {
        classroomAudio.pause();
      }
      audioVisualizer?.classList.remove('hidden');
      audioVisualizer?.classList.add('flex');
    });

    // Seeking video synchronizes audio currentTime
    classroomVideo.addEventListener('seeking', () => {
      if (classroomAudio) {
        classroomAudio.currentTime = classroomVideo.currentTime;
      }
    });

    // Video ending halts audio & visualizer
    classroomVideo.addEventListener('ended', () => {
      if (classroomAudio && !classroomAudio.paused) {
        classroomAudio.pause();
      }
      audioVisualizer?.classList.add('hidden');
      audioVisualizer?.classList.remove('flex');
    });

    // Speed change sync
    classroomVideo.addEventListener('ratechange', () => {
      if (classroomAudio) {
        classroomAudio.playbackRate = classroomVideo.playbackRate;
      }
    });
  }

  // Upgrade Button: Realistic Teacher Studio (5 Credits)
  const btnUpgradeStudio = document.getElementById('btn-upgrade-realistic-studio');
  if (btnUpgradeStudio && !btnUpgradeStudio._bound) {
    btnUpgradeStudio._bound = true;
    btnUpgradeStudio.addEventListener('click', async () => {
      if (AppState.productionTier === 'realistic') {
        alert('✨ Ultra Realistic Teacher Studio is already active for this lesson!');
        return;
      }
      if (AppState.credits < 5) {
        alert(`Insufficient credits! You currently have ${AppState.credits} credits, but Ultra Realistic Teacher Studio requires 5 credits.`);
        return;
      }
      const confirmed = confirm('Upgrade to Ultra Realistic Teacher Studio for 5 credits?\n\nThis will synthesize a realistic human teacher video avatar with 1080p cinematic STEM visuals and advanced pedagogical pacing.');
      if (!confirmed) return;

      deductCredits(5);
      AppState.productionTier = 'realistic';
      btnUpgradeStudio.innerHTML = '<span class="material-symbols-outlined text-[16px] text-amber-300 animate-pulse">stars</span><span>✨ Realistic Studio Active</span>';
      btnUpgradeStudio.className = 'px-3 py-1.5 rounded-xl bg-gradient-to-r from-amber-500/30 to-primary/30 border border-amber-400 text-[12px] font-mono font-bold text-amber-300 shadow-md flex items-center gap-1.5';

      showClassroomToast('✨ Upgraded to Ultra Realistic Studio! Re-synthesizing concept media with 1080p teacher avatar...');
      await loadSegment(AppState.currentSegmentIndex);
    });
  }
}

function showClassroomToast(msg) {
  const existing = document.getElementById('classroom-toast');
  if (existing) existing.remove();
  const toast = document.createElement('div');
  toast.id = 'classroom-toast';
  toast.className = 'fixed top-20 right-6 z-[100] bg-surface-container-highest border border-amber-500/50 text-on-surface px-4 py-3 rounded-2xl shadow-2xl flex items-center gap-3 font-headline-md text-[13px] animate-bounce';
  toast.innerHTML = `<span class="material-symbols-outlined text-amber-400 text-[20px]">auto_awesome</span><span>${msg}</span>`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
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
              audio.currentTime = 0;
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
  
  // Custom styling if this is the final concept segment
  const isFinalSegment = AppState.plan?.segments && (segmentIndex === AppState.plan.segments.length - 1);
  if (btnAdvance) {
    btnAdvance.classList.add('hidden');
    if (isFinalSegment) {
      btnAdvance.innerHTML = '<span>🎉 Complete Lesson & Claim Certificate</span><span class="material-symbols-outlined text-[18px]">workspace_premium</span>';
      btnAdvance.className = 'hidden w-full bg-gradient-to-r from-emerald-600 via-primary to-secondary text-white font-headline-md font-bold py-3.5 rounded-xl hover:scale-[1.01] transition-all text-[14px] shadow-md flex items-center justify-center gap-2 cursor-pointer';
    } else {
      btnAdvance.innerHTML = '<span>Next Concept Segment</span><span class="material-symbols-outlined text-[18px]">arrow_forward</span>';
      btnAdvance.className = 'hidden w-full bg-tertiary-container text-on-tertiary font-headline-md font-bold py-3 rounded-xl hover:opacity-95 transition-all text-[14px] shadow-sm flex items-center justify-center gap-2 cursor-pointer';
    }
  }

  video.classList.add('hidden');
  placeholder.classList.remove('hidden');

  // Reset doubt box + answer box for the new segment.
  document.getElementById('doubt-response-box')?.classList.add('hidden');
  const doubtInputReset = document.getElementById('student-doubt-input');
  if (doubtInputReset) doubtInputReset.value = '';
  const answerReset = document.getElementById('student-answer-input');
  if (answerReset) answerReset.value = '';
  const btnSubReset = document.getElementById('btn-submit-answer');
  if (btnSubReset) btnSubReset.onclick = () => submitStudentAnswer(false);

  try {
    const res = await fetch('/api/session/explain', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: AppState.sessionId,
        segment_index: segmentIndex,
        render_video: true,
        production_tier: AppState.productionTier || 'express',
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
    const visualizer = document.getElementById('classroom-audio-visualizer');
    if (audio && data.audio_url) {
      audio.src = data.audio_url;
      audio.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
      audio.onplay = () => {
        visualizer?.classList.remove('hidden');
        visualizer?.classList.add('flex');
      };
      audio.onpause = audio.onended = () => {
        visualizer?.classList.add('hidden');
        visualizer?.classList.remove('flex');
      };
      audio.play().catch(e => console.log('Audio autoplay deferred:', e));
    }

    // Video Playback / Background Polling
    if (data.video_url && data.video_status === 'ready') {
      if (audio && !audio.paused) {
        video.currentTime = audio.currentTime;
        audio.pause();
        audio.currentTime = 0;
      }
      video.src = data.video_url;
      video.playbackRate = parseFloat(document.getElementById('select-speech-rate')?.value || '1.0');
      video.onplay = () => {
        visualizer?.classList.remove('hidden');
        visualizer?.classList.add('flex');
      };
      video.onpause = video.onended = () => {
        visualizer?.classList.add('hidden');
        visualizer?.classList.remove('flex');
      };
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
      // All lessons in this lesson plan completed -> Transition to Completion Page!
      switchView('view-lesson-completed');
      renderLessonCompletionView();
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
  if (!AppState.isDemoUser && AppState.uploadedFiles.length === 0 && !AppState.plan) {
    const overallEl = document.getElementById('kg-overall-mastery');
    const countEl = document.getElementById('kg-mastered-count');
    const misEl = document.getElementById('kg-misconceptions-count');
    if (overallEl) overallEl.textContent = '--%';
    if (countEl) countEl.textContent = '0 / 0';
    if (misEl) misEl.textContent = '0 Tracked';
    if (AppState.knowledgeGraphVisualizer) {
      AppState.knowledgeGraphVisualizer.updateWithApiData({ nodes: [], links: [] });
    }
    return;
  }

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
  if (!AppState.isDemoUser && AppState.uploadedFiles.length === 0 && !AppState.plan) {
    const container = document.getElementById('dna-bars-container');
    if (container) {
      container.innerHTML = `
        <div class="p-8 text-center bg-surface-container-low rounded-2xl border border-outline-variant/30 space-y-3">
          <span class="material-symbols-outlined text-[40px] text-primary">psychology</span>
          <h4 class="font-headline-md font-bold text-[15px] text-on-surface">Cognitive DNA Uncalibrated</h4>
          <p class="text-[13px] text-on-surface-variant max-w-md mx-auto leading-relaxed">
            Upload your chapter notes or syllabus materials and complete your first adaptive lesson checkpoints to map your empirical cognitive modalities (visual deconstruction, conceptual depth, real-world analogies, and recall).
          </p>
        </div>
      `;
    }
    const insight = document.getElementById('dna-insight-text');
    if (insight) insight.textContent = 'Upload a curriculum chapter or notes to begin profiling your personalized cognitive DNA.';
    return;
  }

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
  if (!AppState.isDemoUser && AppState.uploadedFiles.length === 0 && !AppState.plan) {
    const container = document.getElementById('spaced-repetition-list');
    if (container) {
      container.innerHTML = `
        <div class="p-8 text-center bg-surface-container-low rounded-2xl border border-outline-variant/30 space-y-3">
          <span class="material-symbols-outlined text-[40px] text-secondary">history_edu</span>
          <h4 class="font-headline-md font-bold text-[15px] text-on-surface">Spaced Repetition Schedule Inactive</h4>
          <p class="text-[13px] text-on-surface-variant max-w-md mx-auto leading-relaxed">
            Upload chapter notes or a textbook section and complete concept checkpoints to activate your Ebbinghaus memory curve calendar and review cards.
          </p>
        </div>
      `;
    }
    return;
  }

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

    const conceptsContainer = document.getElementById('teacher-concepts-list');
    const misContainer = document.getElementById('teacher-misconceptions-list');
    const remContainer = document.getElementById('teacher-remediations-list');

    // Honest empty state — no student has attempted anything yet.
    if (data.data_available === false || !data.concepts_mastery.length) {
      const msg = '<p class="text-on-surface-variant p-6 bg-surface-container-low rounded-2xl">No class activity yet. Cohort analytics appear here once students complete lessons and checkpoint questions.</p>';
      if (conceptsContainer) conceptsContainer.innerHTML = msg;
      if (misContainer) misContainer.innerHTML = '';
      if (remContainer) remContainer.innerHTML = '';
      return;
    }

    // Render Concept Risk Heatmap
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

    // Load Student Roster and "How to Teach Them" Pedagogical Guidance
    await loadStudentRosterAndGuidance();
  } catch (err) {
    console.error('Teacher dashboard load error:', err);
  }
}

// --------------------------------------------------------------------------- //
// Student Roster & "How to Teach Them" Guidance Matrix (Teacher Exclusive)
// --------------------------------------------------------------------------- //
async function loadStudentRosterAndGuidance() {
  const rosterContainer = document.getElementById('teacher-roster-selector');
  if (!rosterContainer) return;

  try {
    const res = await fetch('/api/teacher/students-roster', {
      headers: AppState.token ? { Authorization: `Bearer ${AppState.token}` } : {},
    });
    const data = await res.json();
    const students = data.students || [];

    if (!students.length) {
      rosterContainer.innerHTML = '<span class="text-[12px] text-on-surface-variant">No enrolled students yet.</span>';
      return;
    }

    rosterContainer.innerHTML = '';
    students.forEach((s, idx) => {
      const btn = document.createElement('button');
      const isRisk = s.status.includes('Risk');
      const activeClass = idx === 0 ? 'bg-primary text-white border-primary shadow-sm' : 'bg-surface hover:bg-surface-container border-outline-variant/40 text-on-surface';
      btn.className = `student-roster-btn px-3 py-1.5 rounded-xl border text-[12px] font-medium flex items-center gap-2 transition-all cursor-pointer ${activeClass}`;
      btn.dataset.studentId = s.student_id;
      btn.innerHTML = `
        <span>${s.avatar}</span>
        <span class="font-bold">${s.full_name}</span>
        <span class="text-[10px] font-mono px-1.5 py-0.2 rounded-full ${isRisk ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-800'}">${s.average_mastery}%</span>
      `;

      btn.addEventListener('click', () => {
        document.querySelectorAll('.student-roster-btn').forEach(b => {
          b.className = 'student-roster-btn px-3 py-1.5 rounded-xl border text-[12px] font-medium flex items-center gap-2 transition-all cursor-pointer bg-surface hover:bg-surface-container border-outline-variant/40 text-on-surface';
        });
        btn.className = 'student-roster-btn px-3 py-1.5 rounded-xl border text-[12px] font-medium flex items-center gap-2 transition-all cursor-pointer bg-primary text-white border-primary shadow-sm';
        loadStudentPedagogicalGuidance(s.student_id);
      });

      rosterContainer.appendChild(btn);
    });

    // Auto-load first student
    if (students.length > 0) {
      loadStudentPedagogicalGuidance(students[0].student_id);
    }
  } catch (err) {
    console.error('Failed to load student roster:', err);
  }
}

async function loadStudentPedagogicalGuidance(studentId) {
  const card = document.getElementById('teacher-guidance-card');
  if (!card) return;

  try {
    card.innerHTML = '<div class="p-6 text-center text-on-surface-variant text-[13px]"><span class="material-symbols-outlined animate-spin text-[20px] mr-1">sync</span> Diagnosing student cognitive gaps...</div>';

    const res = await fetch(`/api/teacher/student-guidance/${studentId}`, {
      headers: AppState.token ? { Authorization: `Bearer ${AppState.token}` } : {},
    });
    const g = await res.json();

    const tipsHtml = g.how_to_teach_guidance.map(tip => `
      <div class="p-3.5 rounded-xl bg-surface-container-low border border-outline-variant/30 space-y-1">
        <div class="flex items-center gap-2 text-primary font-bold text-[13px]">
          <span class="material-symbols-outlined text-[18px] text-secondary">tips_and_updates</span>
          <span>${tip.type}</span>
        </div>
        <p class="text-[12px] text-on-surface font-medium">&bull; <strong>Observation</strong>: ${tip.insight}</p>
        <p class="text-[12px] text-emerald-800 bg-emerald-50/80 p-2 rounded-lg border border-emerald-200 mt-1 font-mono">
          &rarr; <strong>Instructional Prescription</strong>: ${tip.instructional_strategy}
        </p>
      </div>
    `).join('');

    const weakHtml = g.weak_concepts.length ? g.weak_concepts.map(w => `
      <span class="px-2.5 py-1 rounded-lg bg-red-50 text-red-700 border border-red-200 text-[11px] font-semibold">
        ${w.concept} (${w.mastery}%)
      </span>
    `).join(' ') : '<span class="text-[12px] text-emerald-700 font-semibold">No critical concept gaps identified.</span>';

    card.innerHTML = `
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-outline-variant/20 pb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center text-[20px] font-bold">
            👨‍🎓
          </div>
          <div>
            <h4 class="font-headline-md text-[16px] font-bold text-on-surface">${g.full_name} (${g.student})</h4>
            <span class="text-[12px] text-on-surface-variant font-mono">${g.grade_or_board} &bull; Preferred Language: ${g.preferred_language}</span>
          </div>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[11px] font-mono font-bold bg-secondary/10 text-secondary border border-secondary/30 px-3 py-1 rounded-full">
            Optimal Mode: ${g.optimal_teaching_mode}
          </span>
        </div>
      </div>

      <!-- Identified Gaps & Misconceptions -->
      <div class="space-y-1.5">
        <span class="block text-[11px] font-mono text-on-surface-variant uppercase font-bold">Identified Stumbling Blocks:</span>
        <div class="flex flex-wrap gap-2">
          ${weakHtml}
        </div>
      </div>

      <!-- "How to Teach This Student" Specific Action Plans -->
      <div class="space-y-2 pt-2">
        <span class="block text-[12px] font-headline-md font-bold text-primary flex items-center gap-1.5">
          <span class="material-symbols-outlined text-[18px] text-secondary">psychology</span>
          Pedagogical Guidance ("How to Teach Them"):
        </span>
        <div class="space-y-2.5">
          ${tipsHtml}
        </div>
      </div>

      <!-- 1-Click Launch Targeted Remediation -->
      <div class="pt-3 border-t border-outline-variant/20 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <span class="text-[12px] font-mono text-on-surface-variant">Recommended: ${g.recommended_action}</span>
        <button id="btn-launch-student-remediation" class="px-4 py-2 rounded-xl bg-primary hover:bg-primary-container text-on-primary text-[12px] font-bold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer">
          <span class="material-symbols-outlined text-[16px]">bolt</span>
          <span>Prepare Remediation Lesson for ${g.full_name.split(' ')[0]}</span>
        </button>
      </div>
    `;

    // Bind 1-click remediation launcher
    document.getElementById('btn-launch-student-remediation')?.addEventListener('click', () => {
      const topicInput = document.getElementById('topic-input');
      const studentInput = document.getElementById('student-name-input');
      if (topicInput && g.weak_concepts.length) {
        topicInput.value = g.weak_concepts[0].concept;
      }
      if (studentInput) {
        studentInput.value = g.student;
      }
      AppState.student = g.student;
      switchView('view-upload-material');
    });

  } catch (err) {
    card.innerHTML = `<div class="p-4 text-red-600 text-[12px]">Failed to load student guidance: ${err.message}</div>`;
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
  AppState.reportData = report;

  // Update quiz subtitle on completion page if rendered
  const quizSubtitle = document.getElementById('completion-quiz-btn-subtitle');
  if (quizSubtitle) {
    quizSubtitle.textContent = `Completed! Score: ${report.raw_score}/${report.out_of} (${Math.round((report.raw_score / report.out_of) * 100)}%)`;
  }

  container.innerHTML = `
    <div class="border-b border-outline-variant/30 pb-4 flex justify-between items-center">
      <div>
        <h3 class="font-headline-lg text-[22px] font-bold text-on-surface">Formative Report Card</h3>
        <p class="text-[12px] font-mono text-on-surface-variant mt-0.5">Topic: ${report.topic}</p>
      </div>
      <div class="text-right">
        <span class="font-headline-lg text-[28px] font-bold text-primary block">${report.raw_score} / ${report.out_of}</span>
        <span class="text-[11px] font-mono text-emerald-700 font-bold bg-emerald-100 px-2 py-0.5 rounded-full border border-emerald-300">Grade: Distinction</span>
      </div>
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

    <div class="pt-3 flex flex-wrap items-center justify-between gap-3 border-t border-outline-variant/20">
      <button id="btn-view-cert-from-quiz" class="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 via-primary to-secondary text-white font-headline-md font-bold text-[13px] flex items-center gap-2 shadow-md hover:scale-[1.01] transition-all cursor-pointer">
        <span class="material-symbols-outlined text-[18px]">workspace_premium</span>
        <span>View Official Completion Certificate</span>
      </button>

      ${data.next_topic ? `
        <span class="text-[12px] font-mono text-on-surface-variant">Recommended Next: <strong>${data.next_topic.next_topic}</strong></span>
      ` : ''}
    </div>
  `;

  document.getElementById('btn-view-cert-from-quiz')?.addEventListener('click', () => {
    switchView('view-lesson-completed');
    renderLessonCompletionView();
  });

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

        // Synchronize active preset button highlight
        const normQ = q.toLowerCase();
        document.querySelectorAll('.model-3d-btn').forEach(b => {
          const modelKey = b.getAttribute('data-model');
          const isMatch = (modelKey === 'eye' && (normQ.includes('eye') || spec.model_type === 'human_eye')) ||
                          (modelKey === 'dna' && spec.model_type === 'dna_helix') ||
                          (modelKey === 'atom' && spec.model_type === 'bohr_atom') ||
                          (modelKey === 'motor' && spec.model_type === 'electric_motor') ||
                          (modelKey === 'solar' && spec.model_type === 'solar_orbits') ||
                          (modelKey === 'water' && normQ.includes('water')) ||
                          (modelKey === 'mitochondria' && normQ.includes('mitochondria')) ||
                          (modelKey === 'neuron' && normQ.includes('neuron'));
          if (isMatch) {
            b.className = 'model-3d-btn px-3.5 py-1.5 rounded-xl bg-primary text-on-primary text-[12px] font-bold transition-all shadow-sm flex items-center gap-1.5';
          } else {
            b.className = 'model-3d-btn px-3.5 py-1.5 rounded-xl bg-surface border border-outline-variant hover:bg-surface-container text-on-surface text-[12px] font-bold transition-all shadow-sm flex items-center gap-1.5';
          }
        });
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

// --------------------------------------------------------------------------- //
// Lesson Completion & Certification Controller
// --------------------------------------------------------------------------- //
let confettiAnimationId = null;

function fireCelebrationConfetti() {
  const canvas = document.getElementById('completion-confetti-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const rect = canvas.parentElement ? canvas.parentElement.getBoundingClientRect() : { width: window.innerWidth, height: 800 };
  canvas.width = rect.width || window.innerWidth;
  canvas.height = rect.height || 850;

  // Particle parameters: colors (Saffron, Emerald, Navy, Gold, Coral)
  const colors = ['#fe9832', '#002045', '#003e29', '#f59e0b', '#10b981', '#ef4444', '#ffd700'];
  const particles = [];
  const particleCount = 85;

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: (Math.random() * -canvas.height * 0.4) - 20,
      size: Math.random() * 9 + 5,
      color: colors[Math.floor(Math.random() * colors.length)],
      speedY: Math.random() * 2.8 + 2.2,
      speedX: (Math.random() - 0.5) * 3.2,
      rotation: Math.random() * 360,
      rotationSpeed: (Math.random() - 0.5) * 7,
      opacity: 1,
    });
  }

  if (confettiAnimationId) cancelAnimationFrame(confettiAnimationId);
  const startTime = Date.now();

  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const elapsed = (Date.now() - startTime) / 1000;

    particles.forEach(p => {
      p.y += p.speedY;
      p.x += Math.sin(p.y * 0.02) + p.speedX;
      p.rotation += p.rotationSpeed;

      if (elapsed > 4.0) {
        p.opacity = Math.max(0, p.opacity - 0.025);
      }

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.globalAlpha = p.opacity;
      ctx.fillStyle = p.color;
      ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.65);
      ctx.restore();
    });

    if (elapsed < 6.5) {
      confettiAnimationId = requestAnimationFrame(animate);
    } else {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
  }

  animate();
}

async function renderLessonCompletionView() {
  // Reveal nav tab
  const navTab = document.getElementById('nav-tab-completion');
  if (navTab) {
    navTab.classList.remove('hidden');
    navTab.classList.add('flex');
  }

  // Trigger celebratory confetti burst
  fireCelebrationConfetti();

  const studentName = AppState.user?.full_name || (AppState.student ? AppState.student.replace(/_/g, ' ').toUpperCase() : 'Scholar');
  const lessonTitle = AppState.plan?.title || 'Science & Mathematics Adaptive Curriculum';
  const language = AppState.selectedLanguage || 'English';
  const examBoard = AppState.selectedExamBoard || 'CBSE Board Class 10';

  // Hero section updates
  const heroTitle = document.getElementById('completion-student-title');
  if (heroTitle) heroTitle.textContent = `Congratulations, ${studentName}! 🎉`;

  const heroSubtitle = document.getElementById('completion-lesson-subtitle');
  if (heroSubtitle) {
    heroSubtitle.innerHTML = `You've successfully completed all concept lessons and checkpoints in <strong class="text-primary font-bold">${lessonTitle}</strong>.`;
  }

  const badgeBoard = document.getElementById('completion-badge-board');
  if (badgeBoard) badgeBoard.textContent = examBoard;

  const badgeLang = document.getElementById('completion-badge-lang');
  if (badgeLang) badgeLang.textContent = `${language} (Neural Voice)`;

  // Fetch consolidated completion data from backend
  let completionData = null;
  if (AppState.sessionId) {
    try {
      const res = await fetch(`/api/session/complete/${AppState.sessionId}`);
      if (res.ok) {
        completionData = await res.json();
      }
    } catch (e) {
      console.log('Completion fetch fallback to local state:', e);
    }
  }

  const totalSegments = completionData?.total_segments || AppState.plan?.segments?.length || 5;
  const completedSegments = completionData?.completed_segments || totalSegments;
  const segments = completionData?.segments || AppState.plan?.segments || [];
  const masteryScore = completionData?.mastery_percentage || 96;

  // Scoreboard
  const statSegments = document.getElementById('completion-stat-segments');
  if (statSegments) statSegments.textContent = `${completedSegments} / ${totalSegments}`;

  const statMastery = document.getElementById('completion-stat-mastery');
  if (statMastery) statMastery.textContent = `${Math.round(masteryScore)}%`;

  const statAcc = document.getElementById('completion-stat-accuracy');
  if (statAcc) {
    const correctCount = completionData?.score_summary?.correct ?? completedSegments;
    statAcc.textContent = `${correctCount} / ${totalSegments} Correct 🔥`;
  }

  // Conquered concepts list
  const conceptsContainer = document.getElementById('completion-concepts-grid');
  if (conceptsContainer) {
    conceptsContainer.innerHTML = '';
    segments.forEach((seg, idx) => {
      const card = document.createElement('div');
      card.className = 'p-4 rounded-2xl bg-white border border-outline-variant/40 space-y-2 card-interactive shadow-xs';
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-6 h-6 rounded-full bg-primary text-on-primary font-mono text-[11px] font-bold flex items-center justify-center">${idx + 1}</span>
            <h4 class="font-headline-md text-[14px] font-bold text-on-surface">${seg.concept}</h4>
          </div>
          <span class="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-mono font-bold">✓ Mastered</span>
        </div>
        <p class="text-[12px] text-on-surface-variant font-medium">Analogy: <span class="text-on-surface font-semibold">${seg.example || 'Real-world experiential context'}</span></p>
        <div class="flex items-center justify-between pt-1">
          ${seg.source_label ? `<p class="text-[10px] font-mono text-tertiary-container">Source: ${seg.source_label}</p>` : '<span></span>'}
          <button class="inspect-3d-btn text-[11px] font-mono text-secondary hover:underline flex items-center gap-1 font-semibold cursor-pointer" data-concept="${seg.concept}">
            <span class="material-symbols-outlined text-[14px]">view_in_ar</span> 3D Lab
          </button>
        </div>
      `;
      conceptsContainer.appendChild(card);
    });

    // Bind 3D inspect buttons on each card
    conceptsContainer.querySelectorAll('.inspect-3d-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const concept = btn.getAttribute('data-concept') || 'dna';
        switchView('view-3d-lab');
        if (!AppState.threeLab && typeof Bharat3DLab !== 'undefined') {
          AppState.threeLab = new Bharat3DLab('threejs-canvas-container');
        }
        if (AppState.threeLab) {
          AppState.threeLab.loadModel(concept);
        }
      });
    });
  }

  // Certificate Fields
  const certName = document.getElementById('cert-student-name');
  if (certName) certName.textContent = studentName;

  const certTitle = document.getElementById('cert-lesson-title');
  if (certTitle) certTitle.textContent = lessonTitle;

  const certDate = document.getElementById('cert-issue-date');
  if (certDate) {
    const now = new Date();
    certDate.textContent = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  }

  const certBoard = document.getElementById('cert-board-name');
  if (certBoard) certBoard.textContent = examBoard;

  const certLang = document.getElementById('cert-language-name');
  if (certLang) certLang.textContent = language;

  const certId = document.getElementById('cert-verification-id');
  if (certId) {
    certId.textContent = `VERIFICATION ID: BG-CERT-${(AppState.sessionId || 'BG2026').slice(0, 8).toUpperCase()}`;
  }

  const certGrade = document.getElementById('cert-grade-badge');
  if (certGrade) {
    if (AppState.reportData) {
      certGrade.textContent = `Distinction (${AppState.reportData.raw_score}/${AppState.reportData.out_of})`;
    } else {
      certGrade.textContent = 'A+ (Mastered)';
    }
  }

  // Recommended Next Topic
  const nextTopic = completionData?.next_topic;
  if (nextTopic) {
    const nextTitle = document.getElementById('completion-next-topic-title');
    const nextReason = document.getElementById('completion-next-topic-reason');
    if (nextTitle) nextTitle.textContent = nextTopic.next_topic || 'Next STEM Syllabus Chapter';
    if (nextReason) nextReason.textContent = nextTopic.reason || 'Curriculum sequence continuation.';

    const btnStartNext = document.getElementById('btn-start-next-lesson');
    if (btnStartNext) {
      btnStartNext.onclick = () => {
        const topicInput = document.getElementById('topic-input');
        if (topicInput && nextTopic.next_topic) {
          topicInput.value = nextTopic.next_topic;
        }
        switchView('view-upload-material');
      };
    }
  }

  // Bind Actions
  const btnPrint = document.getElementById('btn-print-certificate');
  if (btnPrint) {
    btnPrint.onclick = () => window.print();
  }

  const btnShare = document.getElementById('btn-share-certificate');
  if (btnShare) {
    btnShare.onclick = async () => {
      const shareText = `🎓 I just completed "${lessonTitle}" with 100% mastery on BHARATGURU AI!`;
      if (navigator.share) {
        try {
          await navigator.share({
            title: 'BharatGuru Academix Certificate',
            text: shareText,
            url: window.location.href,
          });
        } catch (e) {
          // ignore share cancel
        }
      } else {
        try {
          await navigator.clipboard.writeText(shareText);
          alert('Certificate accomplishment copied to clipboard!');
        } catch (e) {
          alert(shareText);
        }
      }
    };
  }

  const btnQuiz = document.getElementById('btn-completion-quiz');
  if (btnQuiz) {
    btnQuiz.onclick = () => {
      switchView('view-quiz-assessment');
      if (!AppState.quizData) loadQuiz();
    };
  }

  const btnSpaced = document.getElementById('btn-completion-spaced-rep');
  if (btnSpaced) {
    btnSpaced.onclick = () => switchView('view-spaced-repetition');
  }

  const btnKG = document.getElementById('btn-completion-knowledge-graph');
  if (btnKG) {
    btnKG.onclick = () => switchView('view-knowledge-graph');
  }

  const btnNotes = document.getElementById('btn-completion-notes');
  if (btnNotes) {
    btnNotes.onclick = () => {
      if (AppState.sessionId) {
        window.open(`/api/session/${AppState.sessionId}/notes?format=html`, '_blank', 'noopener');
      }
    };
  }
}

