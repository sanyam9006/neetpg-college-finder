import re

def update_frontend_with_auth():
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Insert CSS for Auth Widget & Modal
    auth_css = """
    /* AUTH MODAL & HEADER WIDGET */
    .auth-btn-hdr{font-family:'Inter',sans-serif;font-size:.78rem;font-weight:700;padding:6px 14px;border-radius:20px;border:1px solid rgba(99,102,241,.4);background:rgba(99,102,241,.12);color:#a5b4fc;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:all .18s}
    .auth-btn-hdr:hover{background:rgba(99,102,241,.25);color:#fff;border-color:var(--accent)}
    .user-pill{display:inline-flex;align-items:center;gap:8px;padding:4px 10px 4px 6px;border-radius:20px;background:rgba(16,185,129,.1);border:1px solid rgba(16,185,129,.25)}
    .user-avatar{width:24px;height:24px;border-radius:50%;background:rgba(16,185,129,.2);display:inline-flex;align-items:center;justify-content:center;font-size:.75rem}
    .user-info{font-size:.75rem;line-height:1.2;text-align:left}
    .user-name{font-weight:700;color:#fff;display:block}
    .user-batch{font-size:.65rem;color:var(--t2)}
    .logout-btn{background:none;border:none;color:#ef4444;font-size:.72rem;font-weight:700;cursor:pointer;padding:2px 6px;border-radius:4px;transition:background .15s}
    .logout-btn:hover{background:rgba(239,68,68,.15)}
    .auth-input-group{margin-bottom:12px;text-align:left}
    .auth-input-group label{display:block;font-size:.75rem;font-weight:700;color:var(--t2);margin-bottom:5px}
    .auth-input-group input, .auth-input-group select{width:100%;box-sizing:border-box;background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.12);border-radius:10px;padding:10px 12px;color:var(--text);font-size:.85rem;font-family:'Inter',sans-serif;outline:none;transition:border-color .18s}
    .auth-input-group input:focus, .auth-input-group select:focus{border-color:var(--accent);background:rgba(99,102,241,.05)}
    .auth-alert{padding:10px 14px;border-radius:8px;font-size:.8rem;margin-bottom:14px;display:none}
    .auth-alert.err{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.3);color:#fca5a5}
    .auth-alert.succ{background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.3);color:#86efac}
    .auth-banner-info{background:rgba(99,102,241,.12);border:1px solid rgba(99,102,241,.25);padding:10px 14px;border-radius:10px;font-size:.8rem;color:#c7d2fe;margin-bottom:16px;display:flex;align-items:center;gap:8px}
"""
    if ".auth-btn-hdr" not in html:
        css_pos = html.find("/* MODAL */")
        html = html[:css_pos] + auth_css + "\n    " + html[css_pos:]

    # 2. Insert authHeaderWidget into Header
    header_old = """    <div style="display:flex;align-items:center;gap:10px">
      <span id="apiStatusBadge" class="api-badge offline">⚪ MLOps Checking...</span>
      <span class="badge">2025–26 DATA</span>
    </div>"""

    header_new = """    <div style="display:flex;align-items:center;gap:10px">
      <div id="authHeaderWidget"></div>
      <span id="apiStatusBadge" class="api-badge offline">⚪ MLOps Checking...</span>
      <span class="badge">2025–26 DATA</span>
    </div>"""

    if "authHeaderWidget" not in html:
        html = html.replace(header_old, header_new, 1)

    # 3. Insert Auth Modal HTML right before the other modals
    auth_modal_html = """
<!-- CANDIDATE REGISTRATION & LOGIN MODAL -->
<div class="modal-overlay" id="authModal">
  <div class="modal-box" style="max-width:480px">
    <div class="modal-hdr">
      <div>
        <div class="modal-title">🔐 Candidate Verification</div>
        <div style="font-size:.75rem;color:var(--t2);margin-top:2px">Register or login to predict your AIR &amp; explore eligible colleges</div>
      </div>
      <button class="modal-close" onclick="closeAuthModal()">✕</button>
    </div>

    <div class="auth-banner-info" id="authModalNotice">
      <span>💡</span>
      <span id="authNoticeText">Create your free candidate account to unlock All India Rank prediction and eligible college recommendations.</span>
    </div>

    <div class="modal-tabs">
      <button class="mtab active" id="authTabRegister" onclick="switchAuthTab('register')">Register Candidate</button>
      <button class="mtab" id="authTabLogin" onclick="switchAuthTab('login')">Candidate Sign In</button>
    </div>

    <div id="authAlert" class="auth-alert"></div>

    <!-- REGISTER FORM -->
    <form id="registerForm" onsubmit="handleRegister(event)" style="display:block">
      <div class="auth-input-group">
        <label for="regName">Full Name (Doctor / Candidate) *</label>
        <input id="regName" type="text" placeholder="e.g. Dr. Aryan Sharma" required />
      </div>
      <div class="auth-input-group">
        <label for="regEmail">Email Address *</label>
        <input id="regEmail" type="email" placeholder="e.g. aryan.sharma@example.com" required />
      </div>
      <div class="auth-input-group">
        <label for="regPhone">Mobile / WhatsApp Number *</label>
        <input id="regPhone" type="tel" placeholder="10-digit mobile number" maxlength="15" required />
      </div>
      <div class="auth-input-group">
        <label for="regBatch">MBBS Batch Year *</label>
        <select id="regBatch" required>
          <option value="">Select your MBBS batch...</option>
          <option value="2022 (Current Intern)">2022 Batch (Current Intern)</option>
          <option value="2021 (Intern / Post-Intern)">2021 Batch (Intern / Post-Intern)</option>
          <option value="2020 (Post-Intern)">2020 Batch (Post-Intern)</option>
          <option value="2019 (Post-Intern)">2019 Batch (Post-Intern)</option>
          <option value="2018 (Post-Intern)">2018 Batch (Post-Intern)</option>
          <option value="2017 or earlier">2017 or earlier</option>
          <option value="2023 or later (Final Year MBBS)">2023 or later (Final Year MBBS)</option>
        </select>
      </div>
      <div class="auth-input-group">
        <label for="regPass">Password *</label>
        <input id="regPass" type="password" placeholder="Create password (min 6 chars)" minlength="6" required />
      </div>
      <button type="submit" class="btn" style="width:100%;margin-top:10px" id="regSubmitBtn">
        ✨ Register &amp; Unlock Predictions
      </button>
      <div style="text-align:center;margin-top:12px;font-size:.75rem;color:var(--t3)">
        Already registered? <a href="#" onclick="switchAuthTab('login');return false;" style="color:var(--accent);font-weight:700">Sign in here</a>
      </div>
    </form>

    <!-- LOGIN FORM -->
    <form id="loginForm" onsubmit="handleLogin(event)" style="display:none">
      <div class="auth-input-group">
        <label for="loginIdent">Registered Email or Mobile Number *</label>
        <input id="loginIdent" type="text" placeholder="Enter your email or 10-digit mobile" required />
      </div>
      <div class="auth-input-group">
        <label for="loginPass">Password *</label>
        <input id="loginPass" type="password" placeholder="Enter your password" required />
      </div>
      <button type="submit" class="btn" style="width:100%;margin-top:10px" id="loginSubmitBtn">
        🔓 Sign In &amp; Unlock Predictions
      </button>
      <div style="text-align:center;margin-top:12px;font-size:.75rem;color:var(--t3)">
        New candidate? <a href="#" onclick="switchAuthTab('register');return false;" style="color:var(--accent);font-weight:700">Create your account</a>
      </div>
    </form>
  </div>
</div>
"""
    if 'id="authModal"' not in html:
        modal_pos = html.find("<!-- MARKS VS RANK REFERENCE MODAL -->")
        html = html[:modal_pos] + auth_modal_html + "\n" + html[modal_pos:]

    # 4. Insert Auth JavaScript Functions and Logic
    auth_js = """
/* ══════ AUTHENTICATION STATE & HANDLERS ══════ */
let currentUser = null;
let pendingSearchTrigger = false;

function initAuth() {
  const stored = localStorage.getItem('neetpg_user');
  if (stored) {
    try {
      currentUser = JSON.parse(stored);
    } catch(e) {
      currentUser = null;
    }
  }
  updateAuthUI();
}

function updateAuthUI() {
  const widget = document.getElementById('authHeaderWidget');
  if (!widget) return;
  if (currentUser) {
    const displayName = currentUser.name.startsWith('Dr.') ? currentUser.name : `Dr. ${currentUser.name}`;
    widget.innerHTML = `
      <div class="user-pill">
        <span class="user-avatar">👨‍⚕️</span>
        <div class="user-info">
          <span class="user-name">${displayName}</span>
          <span class="user-batch">${currentUser.batch_year}</span>
        </div>
        <button class="logout-btn" onclick="logoutUser()" title="Logout">Logout</button>
      </div>`;
  } else {
    widget.innerHTML = `
      <button class="auth-btn-hdr" onclick="openAuthModal('login')">
        🔑 Sign In / Register
      </button>`;
  }
}

function openAuthModal(tab = 'register', message = null) {
  const modal = document.getElementById('authModal');
  if (!modal) return;
  modal.style.display = 'flex';
  switchAuthTab(tab);
  const alertEl = document.getElementById('authAlert');
  alertEl.style.display = 'none';
  alertEl.className = 'auth-alert';
  const noticeEl = document.getElementById('authNoticeText');
  if (noticeEl) {
    if (message) {
      noticeEl.textContent = message;
    } else {
      noticeEl.textContent = 'Create your free candidate account to unlock All India Rank prediction and eligible college recommendations.';
    }
  }
}

function closeAuthModal() {
  const modal = document.getElementById('authModal');
  if (modal) modal.style.display = 'none';
}

function switchAuthTab(tab) {
  const isReg = tab === 'register';
  document.getElementById('authTabRegister').classList.toggle('active', isReg);
  document.getElementById('authTabLogin').classList.toggle('active', !isReg);
  document.getElementById('registerForm').style.display = isReg ? 'block' : 'none';
  document.getElementById('loginForm').style.display = !isReg ? 'block' : 'none';
  const alertEl = document.getElementById('authAlert');
  alertEl.style.display = 'none';
}

function showAuthAlert(msg, type = 'err') {
  const el = document.getElementById('authAlert');
  if (!el) return;
  el.className = `auth-alert ${type}`;
  el.textContent = msg;
  el.style.display = 'block';
}

async function handleRegister(e) {
  e.preventDefault();
  const name = document.getElementById('regName').value.trim();
  const email = document.getElementById('regEmail').value.trim();
  const phone = document.getElementById('regPhone').value.trim();
  const batch_year = document.getElementById('regBatch').value;
  const password = document.getElementById('regPass').value;

  if (!name || !email || !phone || !batch_year || !password) {
    showAuthAlert('Please fill in all required fields.', 'err');
    return;
  }

  const btn = document.getElementById('regSubmitBtn');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '⏳ Creating Account...';

  try {
    const res = await fetch('http://localhost:8000/api/v1/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone, batch_year, password })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed. Please check your details.');
    }

    currentUser = data.user;
    localStorage.setItem('neetpg_user', JSON.stringify(currentUser));
    updateAuthUI();
    showAuthAlert('Registration successful! Unlocking predictions...', 'succ');
    
    setTimeout(() => {
      closeAuthModal();
      btn.disabled = false;
      btn.innerHTML = originalText;
      if (pendingSearchTrigger) {
        pendingSearchTrigger = false;
        runSearch();
      }
    }, 500);
  } catch(err) {
    console.warn('Backend registration error or offline, fallback to local storage:', err);
    // Offline fallback ensuring candidate is never blocked
    currentUser = {
      id: Date.now(),
      name: name,
      email: email,
      phone: phone,
      batch_year: batch_year,
      token: 'offline_' + Math.random().toString(36).substr(2)
    };
    localStorage.setItem('neetpg_user', JSON.stringify(currentUser));
    updateAuthUI();
    showAuthAlert('Account created successfully! Unlocking predictions...', 'succ');

    setTimeout(() => {
      closeAuthModal();
      btn.disabled = false;
      btn.innerHTML = originalText;
      if (pendingSearchTrigger) {
        pendingSearchTrigger = false;
        runSearch();
      }
    }, 500);
  }
}

async function handleLogin(e) {
  e.preventDefault();
  const email_or_phone = document.getElementById('loginIdent').value.trim();
  const password = document.getElementById('loginPass').value;

  if (!email_or_phone || !password) {
    showAuthAlert('Please enter your email/phone and password.', 'err');
    return;
  }

  const btn = document.getElementById('loginSubmitBtn');
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '⏳ Signing In...';

  try {
    const res = await fetch('http://localhost:8000/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email_or_phone, password })
    });

    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Invalid email/phone or password.');
    }

    currentUser = data.user;
    localStorage.setItem('neetpg_user', JSON.stringify(currentUser));
    updateAuthUI();
    showAuthAlert('Sign in successful! Loading predictions...', 'succ');

    setTimeout(() => {
      closeAuthModal();
      btn.disabled = false;
      btn.innerHTML = originalText;
      if (pendingSearchTrigger) {
        pendingSearchTrigger = false;
        runSearch();
      }
    }, 500);
  } catch(err) {
    showAuthAlert(err.message || 'Login failed. Please check your credentials.', 'err');
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
}

function logoutUser() {
  currentUser = null;
  localStorage.removeItem('neetpg_user');
  updateAuthUI();
}
"""

    if "/* ══════ AUTHENTICATION STATE & HANDLERS ══════ */" not in html:
        # Insert right after /* ══════ CONSTANTS ══════ */
        c_pos = html.find("/* ══════ CONSTANTS ══════ */")
        html = html[:c_pos] + auth_js + "\n" + html[c_pos:]

    # 5. Insert gatekeeper check in runSearch()
    gatekeeper_code = """  // AUTHENTICATION GATEKEEPER
  if (!currentUser) {
    pendingSearchTrigger = true;
    openAuthModal('register', 'Please enter your candidate information (Name, Email, Phone, Batch Year) to predict your All India Rank and view eligible colleges.');
    return;
  }
"""

    old_runsearch_start = """function runSearch() {
  const catVal = document.getElementById('cs').value;
  const st = document.getElementById('ss').value;
  const tp = document.getElementById('ts').value;
  const sp = document.getElementById('sp').value;
  const tf = document.getElementById('tierf').value;"""

    new_runsearch_start = """function runSearch() {
  const catVal = document.getElementById('cs').value;
  const st = document.getElementById('ss').value;
  const tp = document.getElementById('ts').value;
  const sp = document.getElementById('sp').value;
  const tf = document.getElementById('tierf').value;

  // Validate inputs before prompting auth
  if (activeMode === 'marks') {
    const mVal = document.getElementById('mi').value.trim();
    if (!mVal) {
      const el = document.getElementById('mi');
      el.focus(); el.style.borderColor = '#ef4444';
      setTimeout(() => el.style.borderColor = '', 1800);
      return;
    }
  } else {
    const rVal = document.getElementById('ri').value.trim();
    if (!rVal) {
      const el = document.getElementById('ri');
      el.focus(); el.style.borderColor = '#ef4444';
      setTimeout(() => el.style.borderColor = '', 1800);
      return;
    }
  }

  // Check Authentication Gatekeeper
  if (!currentUser) {
    pendingSearchTrigger = true;
    openAuthModal('register', 'Please register your candidate details (Name, Email, Phone, Batch Year) to view your All India Rank prediction and eligible colleges.');
    return;
  }"""

    if "Check Authentication Gatekeeper" not in html:
        html = html.replace(old_runsearch_start, new_runsearch_start, 1)

    # 6. Call initAuth() on window load
    if "initAuth();" not in html:
        check_health_call = "checkBackendHealth();"
        html = html.replace(check_health_call, "initAuth();\n  checkBackendHealth();", 1)

    # 7. Add outside click handler for authModal
    old_outside_click = "const rmEl = document.getElementById('rankModal');"
    new_outside_click = """const amEl = document.getElementById('authModal');
if (amEl) {
  amEl.addEventListener('click', e => {
    if (e.target.id === 'authModal') closeAuthModal();
  });
}

const rmEl = document.getElementById('rankModal');"""
    if "id === 'authModal'" not in html:
        html = html.replace(old_outside_click, new_outside_click, 1)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print("index.html updated with Authentication flow successfully!")

if __name__ == '__main__':
    update_frontend_with_auth()
