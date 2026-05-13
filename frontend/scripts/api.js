/**
 * PGDOST API utilities
 */

const API_BASE = 'http://127.0.0.1:8000/api';

const Theme = {
  storageKey: 'pgdost-theme',
  initialized: false,
  getStoredTheme() {
    try {
      const value = localStorage.getItem(this.storageKey);
      return value === 'dark' ? 'dark' : 'light';
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
    this.set(this.getCurrent() === 'dark' ? 'light' : 'dark');
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
    if (!document.body) return;
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

function _goTo(pageName) {
  if (window.location.pathname.includes('/pages/')) {
    window.location.href = pageName;
  } else {
    window.location.href = 'pages/' + pageName;
  }
}

const Auth = {
  _storage(mode) {
    return mode === 'session' ? sessionStorage : localStorage;
  },
  setTokens(access, refresh, persist = true) {
    const storage = this._storage(persist ? 'local' : 'session');
    const other = this._storage(persist ? 'session' : 'local');
    storage.setItem('access_token', access);
    storage.setItem('refresh_token', refresh);
    other.removeItem('access_token');
    other.removeItem('refresh_token');
  },
  getAccess() {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
  },
  getRefresh() {
    return localStorage.getItem('refresh_token') || sessionStorage.getItem('refresh_token');
  },
  setUser(user, persist = true) {
    const storage = this._storage(persist ? 'local' : 'session');
    const other = this._storage(persist ? 'session' : 'local');
    storage.setItem('user', JSON.stringify(user));
    other.removeItem('user');
  },
  getUser() {
    try {
      const raw = localStorage.getItem('user') || sessionStorage.getItem('user');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user');
  },
  isLoggedIn() {
    return !!this.getAccess();
  },
  getRole() {
    return this.getUser()?.role || null;
  },
  logout() {
    this.clear();
    _goTo('login.html');
  },
};

class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

function extractError(data) {
  if (!data) return null;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.non_field_errors) return data.non_field_errors.join(', ');
  const firstKey = Object.keys(data)[0];
  if (!firstKey) return JSON.stringify(data);
  const value = data[firstKey];
  return `${firstKey}: ${Array.isArray(value) ? value.join(', ') : value}`;
}

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
    const persistInLocal = !!localStorage.getItem('refresh_token');
    Auth.setTokens(data.access, refresh, persistInLocal);
    return true;
  } catch {
    return false;
  }
}

async function apiFetch(endpoint, options = {}) {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = Auth.getAccess();
  if (token) headers.Authorization = `Bearer ${token}`;

  let response = await fetch(url, { ...options, headers });
  if (response.status === 401 && Auth.getRefresh()) {
    const refreshed = await refreshToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${Auth.getAccess()}`;
      response = await fetch(url, { ...options, headers });
    } else {
      Auth.logout();
      return;
    }
  }

  if (response.status === 204) return null;
  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new ApiError(extractError(data) || `HTTP ${response.status}`, response.status, data);
  }
  return data;
}

const api = {
  get: (endpoint) => apiFetch(endpoint, { method: 'GET' }),
  post: (endpoint, body) => apiFetch(endpoint, { method: 'POST', body: JSON.stringify(body) }),
  patch: (endpoint, body) => apiFetch(endpoint, { method: 'PATCH', body: JSON.stringify(body) }),
  put: (endpoint, body) => apiFetch(endpoint, { method: 'PUT', body: JSON.stringify(body) }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' }),
};

const Toast = {
  _container: null,
  _getContainer() {
    if (!this._container) {
      this._container = document.getElementById('toast-container') || document.createElement('div');
      if (!this._container.id) this._container.id = 'toast-container';
      if (!this._container.parentNode) document.body.appendChild(this._container);
    }
    return this._container;
  },
  show(message, type = 'info', duration = 4000) {
    const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'ℹ️'}</span><span>${message}</span>`;
    this._getContainer().appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 220);
    }, duration);
  },
  success(message) { this.show(message, 'success'); },
  error(message) { this.show(message, 'error'); },
  warning(message) { this.show(message, 'warning'); },
  info(message) { this.show(message, 'info'); },
};

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
    resident: 'resident-dashboard.html',
    owner: 'owner-dashboard.html',
    superadmin: 'admin-dashboard.html',
  };
  _goTo(pages[role] || 'index.html');
}

function openModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('open');
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('open');
}

document.addEventListener('click', (event) => {
  if (event.target.classList.contains('modal-overlay')) {
    event.target.classList.remove('open');
  }
});

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function formatCurrency(amount) {
  if (amount == null || amount === '') return '—';
  return `₹${parseFloat(amount).toLocaleString('en-IN')}`;
}

function statusBadge(status) {
  const map = {
    pending: ['badge-yellow', 'Pending'],
    approved: ['badge-green', 'Approved'],
    rejected: ['badge-red', 'Rejected'],
    vacated: ['badge-blue', 'Vacated'],
    paid: ['badge-green', 'Paid'],
    overdue: ['badge-red', 'Overdue'],
    open: ['badge-yellow', 'Open'],
    in_progress: ['badge-blue', 'In Progress'],
    resolved: ['badge-green', 'Resolved'],
    closed: ['badge-blue', 'Closed'],
  };
  const [cls, label] = map[status] || ['badge-blue', status];
  return `<span class="badge ${cls}">${label}</span>`;
}

window.api = api;
window.Auth = Auth;
window.Toast = Toast;
window.requireAuth = requireAuth;
window.redirectIfLoggedIn = redirectIfLoggedIn;
window.openModal = openModal;
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
