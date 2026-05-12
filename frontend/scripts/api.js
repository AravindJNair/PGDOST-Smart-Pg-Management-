/**
 * PGDOST — API Interceptor (api.js)
 * Centralized Fetch wrapper that:
 *  - Automatically attaches Bearer JWT from localStorage
 *  - Parses JSON responses
 *  - Handles 401 Unauthorized (redirects to login)
 *  - Exposes token / user helpers
 */

const API_BASE = 'http://127.0.0.1:8000/api';

const Theme = {
  storageKey: 'pgdost-theme',
  initialized: false,
  getStoredTheme() {
    try {
      const val = localStorage.getItem(this.storageKey);
      return val === 'dark' ? 'dark' : 'light';
    } catch {
      return 'light';
    }
  },
  saveTheme(theme) {
    try {
      localStorage.setItem(this.storageKey, theme === 'dark' ? 'dark' : 'light');
    } catch {}
  },
  apply(theme) {
    const mode = theme === 'dark' ? 'dark' : 'light';
    const isDark = mode === 'dark';
    document.documentElement.classList.toggle('dark-mode', isDark);
    document.documentElement.classList.toggle('light-mode', !isDark);
    if (document.body) {
      document.body.classList.toggle('dark-mode', isDark);
      document.body.classList.toggle('light-mode', !isDark);
      document.body.dataset.theme = mode;
    }
    this.syncToggleState(mode);
  },
  set(theme) {
    const mode = theme === 'dark' ? 'dark' : 'light';
    this.saveTheme(mode);
    this.apply(mode);
  },
  toggle() {
    const current = this.getCurrent();
    this.set(current === 'dark' ? 'light' : 'dark');
  },
  getCurrent() {
    if (document.documentElement.classList.contains('dark-mode')) return 'dark';
    if (document.body && document.body.classList.contains('dark-mode')) return 'dark';
    return this.getStoredTheme();
  },
  syncToggleState(mode) {
    const isDark = mode === 'dark';
    const controls = document.querySelectorAll('#theme-toggle, #global-theme-toggle');
    controls.forEach((control) => {
      control.setAttribute('aria-pressed', String(isDark));
      control.setAttribute('aria-label', isDark ? 'Switch to light mode' : 'Switch to dark mode');
      control.classList.toggle('is-dark', isDark);
    });
  },
  ensureGlobalToggle() {
    if (document.getElementById('theme-toggle') || document.getElementById('global-theme-toggle')) return;
    const btn = document.createElement('button');
    btn.id = 'global-theme-toggle';
    btn.type = 'button';
    btn.className = 'global-theme-toggle';
    btn.setAttribute('aria-label', 'Switch to dark mode');
    btn.setAttribute('aria-pressed', 'false');
    btn.innerHTML = '<span class="theme-toggle-sun">&#9728;</span><span class="theme-toggle-moon">&#9790;</span>';
    btn.addEventListener('click', () => this.toggle());
    document.body.appendChild(btn);
  },
  attachToggleHandlers() {
    const controls = document.querySelectorAll('#theme-toggle, #global-theme-toggle');
    controls.forEach((control) => {
      if (control.dataset.themeBound === '1') return;
      control.dataset.themeBound = '1';
      control.addEventListener('click', () => this.toggle());
    });
  },
  initAtmosphereLayer() {
    if (!document.body || document.querySelector('.theme-atmosphere')) return;
    const layer = document.createElement('div');
    layer.className = 'theme-atmosphere';
    layer.setAttribute('aria-hidden', 'true');
    layer.innerHTML = [
      '<span class="ambient-glow ambient-glow-1"></span>',
      '<span class="ambient-glow ambient-glow-2"></span>',
      '<span class="ambient-glow ambient-glow-3"></span>',
      '<span class="floating-leaf leaf-1"></span>',
      '<span class="floating-leaf leaf-2"></span>',
      '<span class="floating-leaf leaf-3"></span>',
      '<span class="floating-leaf leaf-4"></span>',
      '<span class="ambient-particle particle-1"></span>',
      '<span class="ambient-particle particle-2"></span>',
      '<span class="ambient-particle particle-3"></span>',
    ].join('');
    document.body.prepend(layer);
  },
  init() {
    if (this.initialized) return;
    this.initialized = true;
    this.apply(this.getStoredTheme());
    this.initAtmosphereLayer();
    this.ensureGlobalToggle();
    this.attachToggleHandlers();
    this.syncToggleState(this.getCurrent());
  },
};

// ── Smart Page Navigation ─────────────────────────────────────
// Works whether the app is opened via http:// OR file://, and works 
// regardless of the live server root.
function _goTo(pageName) {
  if (window.location.pathname.includes('/pages/')) {
    // Already inside pages/ — sibling file
    window.location.href = pageName;
  } else {
    // At root (e.g. index.html) — go into pages/
    window.location.href = 'pages/' + pageName;
  }
}

// ── Token Helpers ────────────────────────────────────────────
const Auth = {
  setTokens(access, refresh) {
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
  },
  getAccess()  { return localStorage.getItem('access_token'); },
  getRefresh() { return localStorage.getItem('refresh_token'); },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  setUser(user) { localStorage.setItem('user', JSON.stringify(user)); },
  getUser() {
    try { return JSON.parse(localStorage.getItem('user')); }
    catch { return null; }
  },
  isLoggedIn() { return !!Auth.getAccess(); },
  getRole() { return Auth.getUser()?.role || null; },
  logout() {
    Auth.clear();
    _goTo('login.html');
  },
};

// ── Core Fetch Wrapper ───────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

  const token = Auth.getAccess();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let response = await fetch(url, { ...options, headers });

  // Attempt token refresh on 401
  if (response.status === 401 && Auth.getRefresh()) {
    const refreshed = await refreshToken();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${Auth.getAccess()}`;
      response = await fetch(url, { ...options, headers });
    } else {
      Auth.logout();
      return;
    }
  }

  // Handle non-2xx without body (204 No Content)
  if (response.status === 204) return null;

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const errorMsg = extractError(data) || `HTTP ${response.status}`;
    throw new ApiError(errorMsg, response.status, data);
  }

  return data;
}

// ── Token Refresh ─────────────────────────────────────────────
async function refreshToken() {
  try {
    const refresh = Auth.getRefresh();
    if (!refresh) return false;
    const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access_token', data.access);
    return true;
  } catch { return false; }
}

// ── ApiError Class ─────────────────────────────────────────────
class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// ── Error Extractor ─────────────────────────────────────────────
function extractError(data) {
  if (!data) return null;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.non_field_errors) return data.non_field_errors.join(', ');
  // First field error
  const firstKey = Object.keys(data)[0];
  if (firstKey) {
    const val = data[firstKey];
    return `${firstKey}: ${Array.isArray(val) ? val.join(', ') : val}`;
  }
  return JSON.stringify(data);
}

// ── Convenience Methods ─────────────────────────────────────────
const api = {
  get:    (endpoint)         => apiFetch(endpoint, { method: 'GET' }),
  post:   (endpoint, body)   => apiFetch(endpoint, { method: 'POST',   body: JSON.stringify(body) }),
  patch:  (endpoint, body)   => apiFetch(endpoint, { method: 'PATCH',  body: JSON.stringify(body) }),
  put:    (endpoint, body)   => apiFetch(endpoint, { method: 'PUT',    body: JSON.stringify(body) }),
  delete: (endpoint)         => apiFetch(endpoint, { method: 'DELETE' }),
};

// ── Toast Notification System ───────────────────────────────────
const Toast = {
  _container: null,
  _getContainer() {
    if (!this._container) {
      this._container = document.createElement('div');
      this._container.id = 'toast-container';
      document.body.appendChild(this._container);
    }
    return this._container;
  },
  show(message, type = 'info', duration = 4000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const container = this._getContainer();
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 200);
    }, duration);
  },
  success: (msg) => Toast.show(msg, 'success'),
  error:   (msg) => Toast.show(msg, 'error'),
  warning: (msg) => Toast.show(msg, 'warning'),
  info:    (msg) => Toast.show(msg, 'info'),
};

// ── Auth Guard ──────────────────────────────────────────────────
function requireAuth(role = null) {
  if (!Auth.isLoggedIn()) {
    _goTo('login.html');
    return false;
  }
  if (role && Auth.getRole() !== role) {
    Toast.error('Access denied. Insufficient permissions.');
    _goTo('login.html');
    return false;
  }
  return true;
}

function redirectIfLoggedIn() {
  if (!Auth.isLoggedIn()) return;
  const role = Auth.getRole();
  const pages = {
    resident:   'resident-dashboard.html',
    owner:      'owner-dashboard.html',
    superadmin: 'admin-dashboard.html',
  };
  _goTo(pages[role] || 'index.html');
}

// ── Modal Helpers ───────────────────────────────────────────────
function openModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.add('open'); }
}
function closeModal(id) {
  const el = document.getElementById(id);
  if (el) { el.classList.remove('open'); }
}
// Close modal on overlay click
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// ── Utility: Format Date ─────────────────────────────────────────
function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit', month: 'short', year: 'numeric'
  });
}

function formatCurrency(amount) {
  if (amount == null) return '—';
  return '₹' + parseFloat(amount).toLocaleString('en-IN');
}

// ── Render Status Badge ──────────────────────────────────────────
function statusBadge(status) {
  const map = {
    pending:     ['badge-yellow', 'Pending'],
    approved:    ['badge-green',  'Approved'],
    rejected:    ['badge-red',    'Rejected'],
    vacated:     ['badge-blue',   'Vacated'],
    paid:        ['badge-green',  'Paid'],
    overdue:     ['badge-red',    'Overdue'],
    open:        ['badge-yellow', 'Open'],
    in_progress: ['badge-blue',   'In Progress'],
    resolved:    ['badge-green',  'Resolved'],
    closed:      ['badge-blue',   'Closed'],
  };
  const [cls, label] = map[status] || ['badge-blue', status];
  return `<span class="badge ${cls}">${label}</span>`;
}

// Expose globally
window.api   = api;
window.Auth  = Auth;
window.Toast = Toast;
window.requireAuth = requireAuth;
window.redirectIfLoggedIn = redirectIfLoggedIn;
window.openModal  = openModal;
window.closeModal = closeModal;
window.formatDate = formatDate;
window.formatCurrency = formatCurrency;
window.statusBadge = statusBadge;
window.ApiError = ApiError;
window.Theme = Theme;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Theme.init(), { once: true });
} else {
  Theme.init();
}
