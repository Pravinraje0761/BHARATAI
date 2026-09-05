/**
 * BHARATGURU Authentication Controller (login.js)
 * Manages client-side validation, 1-click instant demo access,
 * Firebase Authentication (Google Sign-In), user registration,
 * and secure local token storage.
 */

document.addEventListener('DOMContentLoaded', () => {
  const state = {
    mode: 'login', // 'login' | 'register'
    role: 'student', // 'student' | 'teacher'
    firebaseReady: false,
    firebaseConfig: null,
  };

  // DOM elements
  const tabLogin = document.getElementById('tab-btn-login');
  const tabRegister = document.getElementById('tab-btn-register');
  const form = document.getElementById('auth-form');
  const roleRadios = document.querySelectorAll('input[name="auth-role"]');

  const fieldFullname = document.getElementById('field-fullname');
  const fieldEmail = document.getElementById('field-email');
  const fieldGrade = document.getElementById('field-grade');
  const fieldLanguage = document.getElementById('field-language');

  const inputUsername = document.getElementById('input-username');
  const inputEmail = document.getElementById('input-email');
  const inputFullname = document.getElementById('input-fullname');
  const inputPassword = document.getElementById('input-password');
  const selectGrade = document.getElementById('select-grade');
  const selectLanguage = document.getElementById('select-language');

  const labelUsername = document.getElementById('label-username');
  const labelGrade = document.getElementById('label-grade');

  const btnSubmit = document.getElementById('btn-submit');
  const btnSubmitText = document.getElementById('btn-submit-text');
  const btnSubmitSpinner = document.getElementById('btn-submit-spinner');

  const btnDemoStudent = document.getElementById('btn-demo-student');
  const btnDemoTeacher = document.getElementById('btn-demo-teacher');
  const btnTogglePwd = document.getElementById('btn-toggle-pwd');

  const alertBox = document.getElementById('auth-alert');
  const alertIcon = document.getElementById('auth-alert-icon');
  const alertMsg = document.getElementById('auth-alert-msg');

  // Firebase elements
  const btnGoogleSignIn = document.getElementById('btn-google-signin');
  const btnGoogleText = document.getElementById('btn-google-text');
  const btnGoogleSpinner = document.getElementById('btn-google-spinner');
  const fbStatusDot = document.getElementById('fb-status-dot');
  const fbStatusText = document.getElementById('fb-status-text');
  const btnToggleFbConfig = document.getElementById('btn-toggle-fb-config');
  const panelFbConfig = document.getElementById('panel-fb-config');
  const inputFbApiKey = document.getElementById('input-fb-api-key');
  const inputFbProjectId = document.getElementById('input-fb-project-id');
  const btnSaveFbConfig = document.getElementById('btn-save-fb-config');
  const btnDemoFbAuth = document.getElementById('btn-demo-fb-auth');

  // Initialize Firebase & check existing session
  initFirebase();
  checkExistingAuth();

  // ------------------------------------------------------------------------- //
  // Firebase Web SDK Initialization
  // ------------------------------------------------------------------------- //
  async function initFirebase() {
    try {
      const res = await fetch('/api/firebase/config');
      const config = await res.json();
      state.firebaseConfig = config;

      // Check if user saved custom config in localStorage
      const savedCustom = localStorage.getItem('bharat_fb_custom');
      if (savedCustom) {
        try {
          const custom = JSON.parse(savedCustom);
          state.firebaseConfig = { ...state.firebaseConfig, ...custom };
        } catch {}
      }

      if (state.firebaseConfig?.apiKey && window.firebase) {
        if (!firebase.apps.length) {
          firebase.initializeApp(state.firebaseConfig);
        }
        if (firebase.analytics && state.firebaseConfig?.measurementId) {
          try {
            firebase.analytics();
          } catch (analyticsErr) {
            console.warn('Firebase Analytics notice:', analyticsErr);
          }
        }
        state.firebaseReady = true;
        if (fbStatusText) fbStatusText.textContent = `Firebase Live (${state.firebaseConfig.projectId || 'Connected'})`;
        if (fbStatusDot) fbStatusDot.className = 'w-2 h-2 rounded-full bg-emerald-500 animate-pulse';
      } else {
        if (fbStatusText) fbStatusText.textContent = 'Firebase Cloud Ready (Local Bridge)';
        if (fbStatusDot) fbStatusDot.className = 'w-2 h-2 rounded-full bg-blue-500';
      }

      if (inputFbApiKey && state.firebaseConfig?.apiKey) {
        inputFbApiKey.value = state.firebaseConfig.apiKey;
      }
      if (inputFbProjectId && state.firebaseConfig?.projectId) {
        inputFbProjectId.value = state.firebaseConfig.projectId;
      }
    } catch (e) {
      console.warn('Firebase config fetch error:', e);
    }
  }

  // Toggle custom Firebase Config panel
  btnToggleFbConfig?.addEventListener('click', () => {
    panelFbConfig?.classList.toggle('hidden');
  });

  // Save manual Firebase keys
  btnSaveFbConfig?.addEventListener('click', () => {
    const custom = {
      apiKey: inputFbApiKey.value.trim(),
      projectId: inputFbProjectId.value.trim(),
      authDomain: `${inputFbProjectId.value.trim()}.firebaseapp.com`,
    };
    localStorage.setItem('bharat_fb_custom', JSON.stringify(custom));
    showAlert('success', 'Custom Firebase project credentials saved. Initializing...');
    initFirebase();
    setTimeout(clearAlert, 2000);
  });

  // ------------------------------------------------------------------------- //
  // Firebase Google Sign-In Flow
  // ------------------------------------------------------------------------- //
  btnGoogleSignIn?.addEventListener('click', handleGoogleSignIn);
  btnDemoFbAuth?.addEventListener('click', () => handleSimulatedGoogleLogin(state.role));

  async function handleGoogleSignIn() {
    clearAlert();

    // Check if live Firebase SDK is ready with an API key
    if (state.firebaseReady && window.firebase?.auth) {
      try {
        setGoogleLoading(true);
        const provider = new firebase.auth.GoogleAuthProvider();
        const result = await firebase.auth().signInWithPopup(provider);
        const idToken = await result.user.getIdToken();

        // Exchange with backend
        await exchangeFirebaseTokenWithBackend(idToken);
      } catch (err) {
        console.error('Firebase Auth Error:', err);
        const errCode = err?.code || '';
        const errMsg = err?.message || '';

        if (errCode === 'auth/configuration-not-found' || errMsg.includes('configuration-not-found')) {
          const projectId = state.firebaseConfig?.projectId || 'bharat-ai-47b02';
          const authConsoleUrl = `https://console.firebase.google.com/project/${projectId}/authentication`;
          showAlert(
            'error',
            `<div class="space-y-2">
              <div class="font-bold text-red-900 text-[13px] flex items-center gap-1.5">
                <span>Google Sign-In is not enabled in your Firebase Console yet</span>
              </div>
              <p class="text-[12px] text-red-800 leading-snug">
                Firebase threw <code>auth/configuration-not-found</code> because the Google provider must be enabled in the Firebase Console:
              </p>
              <ol class="list-decimal list-inside text-[11px] text-red-950 space-y-1 bg-white/70 p-2.5 rounded-lg border border-red-200">
                <li>Go to <a href="${authConsoleUrl}" target="_blank" rel="noopener noreferrer" class="underline font-bold text-primary hover:text-secondary">Firebase Console &rarr; Authentication</a></li>
                <li>Click <strong>Get started</strong> (if Authentication is not yet activated)</li>
                <li>Go to the <strong>Sign-in method</strong> tab &rarr; click <strong>Google</strong></li>
                <li>Toggle <strong>Enable</strong>, select your <strong>Support email</strong>, and click <strong>Save</strong></li>
              </ol>
              <div class="pt-1 flex flex-wrap items-center gap-2">
                <button id="btn-fallback-instant-login" type="button" class="px-3 py-1.5 bg-primary hover:bg-primary/90 text-white rounded-lg text-[12px] font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer">
                  <span>⚡ Continue with Instant Demo Login</span>
                </button>
                <a href="${authConsoleUrl}" target="_blank" rel="noopener noreferrer" class="px-2.5 py-1.5 bg-white hover:bg-surface-container border border-outline-variant/60 text-[11px] font-medium text-on-surface rounded-lg transition-colors inline-flex items-center gap-1">
                  <span>Open Firebase Console</span> &rarr;
                </a>
              </div>
            </div>`,
            true
          );
          document.getElementById('btn-fallback-instant-login')?.addEventListener('click', () => {
            handleSimulatedGoogleLogin(state.role);
          });
        } else if (errCode === 'auth/popup-closed-by-user') {
          showAlert('error', 'The Google Sign-In popup was closed before completing authentication.');
        } else if (errCode === 'auth/cancelled-popup-request') {
          showAlert('error', 'Sign-in popup request was cancelled.');
        } else if (errCode === 'auth/unauthorized-domain') {
          const currentHost = window.location.hostname || 'localhost';
          showAlert(
            'error',
            `Domain <strong>${currentHost}</strong> is not authorized in Firebase Console.<br>Add it under <em>Authentication &rarr; Settings &rarr; Authorized domains</em>.`,
            true
          );
        } else if (errCode === 'auth/operation-not-allowed') {
          const projectId = state.firebaseConfig?.projectId || 'bharat-ai-47b02';
          showAlert(
            'error',
            `Google provider is not enabled in Firebase Console.<br>Please enable it under <a href="https://console.firebase.google.com/project/${projectId}/authentication/providers" target="_blank" class="underline font-bold">Authentication &rarr; Sign-in method</a>.`,
            true
          );
        } else {
          showAlert('error', errMsg || 'Google sign-in failed via Firebase.');
        }
      } finally {
        setGoogleLoading(false);
      }
    } else {
      // Firebase API key not yet set in .env: use simulated Google Sign-In with backend token verification
      showAlert('success', 'Testing Google Sign-In via Firebase Cloud backend token pipeline...');
      handleSimulatedGoogleLogin(state.role);
    }
  }

  async function handleSimulatedGoogleLogin(role) {
    setGoogleLoading(true);
    try {
      const demoToken = `demo_firebase_token_for_${role}`;
      await exchangeFirebaseTokenWithBackend(demoToken);
    } catch (err) {
      showAlert('error', err.message);
    } finally {
      setGoogleLoading(false);
    }
  }

  async function exchangeFirebaseTokenWithBackend(idToken) {
    const res = await fetch('/api/auth/firebase-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id_token: idToken,
        role: state.role,
        grade_or_board: selectGrade?.value || 'CBSE Class 10',
        preferred_language: selectLanguage?.value || 'English',
      }),
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Firebase authentication failed on backend.');
    }

    onAuthSuccess(data);
  }

  function setGoogleLoading(isLoading) {
    if (isLoading) {
      btnGoogleSignIn.disabled = true;
      btnGoogleText.textContent = 'Connecting to Google...';
      btnGoogleSpinner?.classList.remove('hidden');
    } else {
      btnGoogleSignIn.disabled = false;
      btnGoogleText.textContent = 'Continue with Google';
      btnGoogleSpinner?.classList.add('hidden');
    }
  }

  // ------------------------------------------------------------------------- //
  // Tab Switching (Sign In <-> Register)
  // ------------------------------------------------------------------------- //
  tabLogin?.addEventListener('click', () => setMode('login'));
  tabRegister?.addEventListener('click', () => setMode('register'));

  function setMode(mode) {
    state.mode = mode;
    clearAlert();

    if (mode === 'login') {
      tabLogin.classList.add('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      tabLogin.classList.remove('text-on-surface-variant', 'font-medium');
      tabRegister.classList.remove('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      tabRegister.classList.add('text-on-surface-variant', 'font-medium');

      fieldFullname.classList.add('hidden');
      fieldEmail.classList.add('hidden');
      fieldGrade.classList.add('hidden');
      fieldLanguage.classList.add('hidden');

      labelUsername.textContent = 'Username or Email';
      inputUsername.placeholder = 'e.g. aarav or aarav@school.edu';
      btnSubmitText.textContent = 'Sign In to BHARATGURU';
    } else {
      tabRegister.classList.add('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      tabRegister.classList.remove('text-on-surface-variant', 'font-medium');
      tabLogin.classList.remove('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      tabLogin.classList.add('text-on-surface-variant', 'font-medium');

      fieldFullname.classList.remove('hidden');
      fieldEmail.classList.remove('hidden');
      fieldGrade.classList.remove('hidden');
      fieldLanguage.classList.remove('hidden');

      labelUsername.textContent = 'Choose Username';
      inputUsername.placeholder = 'e.g. priya_physics or rohan22';
      btnSubmitText.textContent = 'Create Free Account';
    }
  }

  // ------------------------------------------------------------------------- //
  // Dual Role Portal Switching (Student Portal <-> Teacher Portal)
  // ------------------------------------------------------------------------- //
  const portalBtnStudent = document.getElementById('portal-btn-student');
  const portalBtnTeacher = document.getElementById('portal-btn-teacher');
  const portalDescText = document.getElementById('portal-description-text');
  const hiddenRoleInput = document.getElementById('hidden-role-input');

  portalBtnStudent?.addEventListener('click', () => setPortal('student'));
  portalBtnTeacher?.addEventListener('click', () => setPortal('teacher'));

  function setPortal(role) {
    state.role = role;
    if (hiddenRoleInput) hiddenRoleInput.value = role;

    if (role === 'student') {
      portalBtnStudent?.classList.add('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      portalBtnStudent?.classList.remove('text-on-surface-variant', 'font-medium');
      portalBtnTeacher?.classList.remove('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      portalBtnTeacher?.classList.add('text-on-surface-variant', 'font-medium');

      if (portalDescText) {
        portalDescText.innerHTML = '<strong>Student View</strong>: Access your personalized lesson plan, live AI classroom, 3D STEM models, and memory flashcards. (Class-wide teaching reports and student rosters are hidden).';
      }

      if (btnGoogleText) btnGoogleText.textContent = 'Continue as Student with Google';
      if (btnSubmitText) {
        btnSubmitText.textContent = state.mode === 'login' ? 'Sign In as Student' : 'Create Student Account';
      }

      labelGrade.textContent = 'Syllabus / Exam Board';
      selectGrade.innerHTML = `
        <option value="CBSE Class 10">CBSE Class 10</option>
        <option value="CBSE Class 12">CBSE Class 12</option>
        <option value="ICSE / ISC">ICSE / ISC</option>
        <option value="JEE Main & Advanced">JEE Main & Advanced</option>
        <option value="NEET-UG">NEET-UG (Medical)</option>
        <option value="State Board">State Board</option>
        <option value="Custom Syllabus">Custom Syllabus</option>
      `;
    } else {
      portalBtnTeacher?.classList.add('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      portalBtnTeacher?.classList.remove('text-on-surface-variant', 'font-medium');
      portalBtnStudent?.classList.remove('bg-white', 'text-primary', 'shadow-sm', 'font-bold');
      portalBtnStudent?.classList.add('text-on-surface-variant', 'font-medium');

      if (portalDescText) {
        portalDescText.innerHTML = '<strong>Teacher / Educator View</strong>: Access cohort misconception radar, students at risk, curriculum planning, and individual "How to Teach Them" guidance.';
      }

      if (btnGoogleText) btnGoogleText.textContent = 'Continue as Teacher with Google';
      if (btnSubmitText) {
        btnSubmitText.textContent = state.mode === 'login' ? 'Sign In as Educator' : 'Create Teacher Account';
      }

      labelGrade.textContent = 'Department / Subject Specialization';
      selectGrade.innerHTML = `
        <option value="Physics Faculty">Physics Faculty</option>
        <option value="Chemistry Department">Chemistry Department</option>
        <option value="Mathematics Faculty">Mathematics Faculty</option>
        <option value="Biology & Life Sciences">Biology & Life Sciences</option>
        <option value="Computer Science & AI">Computer Science & AI</option>
        <option value="General Science">General Science</option>
      `;
    }
  }

  // ------------------------------------------------------------------------- //
  // Password Visibility Toggle
  // ------------------------------------------------------------------------- //
  btnTogglePwd?.addEventListener('click', () => {
    const isPassword = inputPassword.type === 'password';
    inputPassword.type = isPassword ? 'text' : 'password';
    btnTogglePwd.innerHTML = `<span class="material-symbols-outlined text-[20px]">${isPassword ? 'visibility_off' : 'visibility'}</span>`;
  });

  // ------------------------------------------------------------------------- //
  // 1-Click Instant Demo Logins
  // ------------------------------------------------------------------------- //
  btnDemoStudent?.addEventListener('click', () => handleDemoLogin('student'));
  btnDemoTeacher?.addEventListener('click', () => handleDemoLogin('teacher'));

  async function handleDemoLogin(role) {
    clearAlert();
    setLoading(true);
    try {
      const res = await fetch('/api/auth/demo-login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Demo login failed');
      }
      localStorage.setItem('bharat_demo_user', role === 'teacher' ? 'teacher_demo' : 'student_demo');
      onAuthSuccess(data);
    } catch (err) {
      showAlert('error', err.message || 'Demo login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  // ------------------------------------------------------------------------- //
  // Form Submission (Login or Register)
  // ------------------------------------------------------------------------- //
  form?.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAlert();
    localStorage.removeItem('bharat_demo_user');

    const username = inputUsername.value.trim();
    const password = inputPassword.value;

    if (!username) {
      showAlert('error', 'Please enter your username or email.');
      return;
    }
    if (!password || password.length < 6) {
      showAlert('error', 'Password must be at least 6 characters.');
      return;
    }

    setLoading(true);

    try {
      let endpoint = '';
      let payload = {};

      if (state.mode === 'login') {
        endpoint = '/api/auth/login';
        payload = {
          username_or_email: username,
          password: password,
        };
      } else {
        endpoint = '/api/auth/register';
        const email = inputEmail.value.trim();
        const fullname = inputFullname.value.trim() || username;
        const grade = selectGrade.value;
        const language = selectLanguage.value;

        if (!email || !email.includes('@')) {
          throw new Error('Please enter a valid email address.');
        }

        payload = {
          username: username,
          email: email,
          password: password,
          full_name: fullname,
          role: state.role,
          grade_or_board: grade,
          preferred_language: language,
        };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || (state.mode === 'login' ? 'Invalid credentials' : 'Registration failed'));
      }

      onAuthSuccess(data);
    } catch (err) {
      showAlert('error', err.message);
    } finally {
      setLoading(false);
    }
  });

  // ------------------------------------------------------------------------- //
  // Auth Success Handler & Redirection
  // ------------------------------------------------------------------------- //
  function onAuthSuccess(data) {
    if (data.token && data.user) {
      localStorage.setItem('bharat_token', data.token);
      localStorage.setItem('bharat_user', JSON.stringify(data.user));

      showAlert('success', `Welcome, ${data.user.full_name}! Redirecting to classroom...`);

      setTimeout(() => {
        if (data.user.role === 'teacher') {
          window.location.href = '/#view-teacher-dashboard';
        } else {
          window.location.href = '/';
        }
      }, 700);
    }
  }

  // ------------------------------------------------------------------------- //
  // UI Helpers (Alerts, Loading State)
  // ------------------------------------------------------------------------- //
  function showAlert(type, message, isHtml = false) {
    alertBox.classList.remove('hidden', 'bg-red-50', 'text-red-700', 'border-red-200', 'bg-emerald-50', 'text-emerald-700', 'border-emerald-200');

    if (type === 'error') {
      alertBox.classList.add('bg-red-50', 'text-red-700', 'border-red-200');
      alertIcon.textContent = 'error';
    } else {
      alertBox.classList.add('bg-emerald-50', 'text-emerald-700', 'border-emerald-200');
      alertIcon.textContent = 'check_circle';
    }

    if (isHtml) {
      alertMsg.innerHTML = message;
    } else {
      alertMsg.textContent = message;
    }
  }

  function clearAlert() {
    alertBox.classList.add('hidden');
    alertMsg.textContent = '';
  }

  function setLoading(isLoading) {
    if (isLoading) {
      btnSubmit.disabled = true;
      btnSubmit.classList.add('opacity-75', 'cursor-not-allowed');
      btnSubmitSpinner.classList.remove('hidden');
    } else {
      btnSubmit.disabled = false;
      btnSubmit.classList.remove('opacity-75', 'cursor-not-allowed');
      btnSubmitSpinner.classList.add('hidden');
    }
  }

  // ------------------------------------------------------------------------- //
  // Existing Session Check
  // ------------------------------------------------------------------------- //
  async function checkExistingAuth() {
    const token = localStorage.getItem('bharat_token');
    if (!token) return;

    try {
      const res = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        const data = await res.json();
        if (data.user) {
          const roleBadge = data.user.role === 'teacher' ? 'Faculty / Teacher' : 'Student';
          const targetUrl = data.user.role === 'teacher' ? '/#view-teacher-dashboard' : '/';
          showAlert(
            'success',
            `Currently signed in as <strong>${data.user.full_name}</strong> (${roleBadge}).
             <div class="mt-2 flex items-center gap-2">
               <a href="${targetUrl}" class="px-3 py-1 bg-primary text-white rounded-lg text-[11px] font-bold inline-flex items-center gap-1 hover:opacity-90 transition-opacity">
                 <span>Enter App</span> &rarr;
               </a>
               <button id="btn-login-clear-session" type="button" class="px-3 py-1 bg-white text-on-surface border border-outline-variant/50 rounded-lg text-[11px] font-bold hover:bg-surface-container transition-colors cursor-pointer">
                 Sign Out / Switch Account
               </button>
             </div>`,
            true
          );
          document.getElementById('btn-login-clear-session')?.addEventListener('click', async () => {
            try {
              await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
              });
            } catch (err) {
              console.error('Logout error:', err);
            }
            localStorage.removeItem('bharat_token');
            localStorage.removeItem('bharat_user');
            localStorage.removeItem('bharat_demo_user');
            clearAlert();
          });
        }
      } else {
        localStorage.removeItem('bharat_token');
        localStorage.removeItem('bharat_user');
      }
    } catch {
      // offline or error, let user interact
    }
  }
});
