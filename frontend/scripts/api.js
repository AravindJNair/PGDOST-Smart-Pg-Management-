/**
 * PGDOST API utilities
 */

function resolveApiBase() {
  const configured = (window.PGDOST_API_BASE || '').trim();
  if (configured) return configured.replace(/\/+$/, '');
  if (window.location.protocol === 'file:') return 'http://127.0.0.1:8000/api';
  const host = window.location.hostname;
  const port = window.location.port;
  const isLocalHost = host === 'localhost' || host === '127.0.0.1';
  // When frontend is served from a local static server (e.g. :5500),
  // route API calls to Django running on :8000.
  if (isLocalHost && port && port !== '8000') return 'http://127.0.0.1:8000/api';
  return `${window.location.origin}/api`;
}

const API_BASE = resolveApiBase();
const OWNER_ONBOARDING_STORAGE_KEY = 'pgdost-owner-onboarding';

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
  _isLocalSession() {
    return !!(localStorage.getItem('access_token') || localStorage.getItem('refresh_token') || localStorage.getItem('user'));
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
  setUser(user, persist) {
    const resolvedPersist = typeof persist === 'boolean' ? persist : this._isLocalSession();
    const normalizedUser = user || null;
    const storage = this._storage(resolvedPersist ? 'local' : 'session');
    const other = this._storage(resolvedPersist ? 'session' : 'local');
    storage.setItem('user', JSON.stringify(normalizedUser));
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
  setOwnerOnboardingState(onboarding, persist) {
    const resolvedPersist = typeof persist === 'boolean' ? persist : this._isLocalSession();
    const storage = this._storage(resolvedPersist ? 'local' : 'session');
    const other = this._storage(resolvedPersist ? 'session' : 'local');
    if (onboarding) {
      storage.setItem(OWNER_ONBOARDING_STORAGE_KEY, JSON.stringify(onboarding));
    } else {
      storage.removeItem(OWNER_ONBOARDING_STORAGE_KEY);
    }
    other.removeItem(OWNER_ONBOARDING_STORAGE_KEY);
  },
  getOwnerOnboardingState() {
    try {
      const raw = localStorage.getItem(OWNER_ONBOARDING_STORAGE_KEY) || sessionStorage.getItem(OWNER_ONBOARDING_STORAGE_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },
  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem(OWNER_ONBOARDING_STORAGE_KEY);
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem(OWNER_ONBOARDING_STORAGE_KEY);
  },
  isLoggedIn() {
    return !!this.getAccess();
  },
  getRole() {
    return this.getUser()?.role || null;
  },
  getLoginPageForRole(role) {
    const pageByRole = {
      owner: 'owner-login.html',
      superadmin: 'admin-portal/login.html',
    };
    return pageByRole[role] || 'login.html';
  },
  logout(redirectPage = null) {
    const role = this.getRole();
    const target = redirectPage || this.getLoginPageForRole(role);
    this.clear();
    _goTo(target);
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
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const headers = { ...(options.headers || {}) };
  if (!isFormData) headers['Content-Type'] = 'application/json';
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
  post: (endpoint, body) => apiFetch(endpoint, {
    method: 'POST',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  patch: (endpoint, body) => apiFetch(endpoint, {
    method: 'PATCH',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  put: (endpoint, body) => apiFetch(endpoint, {
    method: 'PUT',
    body: body instanceof FormData ? body : JSON.stringify(body),
  }),
  delete: (endpoint) => apiFetch(endpoint, { method: 'DELETE' }),
};

const Toast = {
  _container: null,
  _lastSignature: '',
  _lastShownAt: 0,
  _getContainer() {
    if (!this._container) {
      this._container = document.getElementById('toast-container') || document.createElement('div');
      if (!this._container.id) this._container.id = 'toast-container';
      if (!this._container.parentNode) document.body.appendChild(this._container);
    }
    return this._container;
  },
  show(message, type = 'info', duration = 4000) {
    const signature = `${type}:${String(message || '').trim()}`;
    const now = Date.now();
    if (signature === this._lastSignature && now - this._lastShownAt < 1400) {
      return;
    }
    this._lastSignature = signature;
    this._lastShownAt = now;
    const icons = { success: 'OK', error: 'X', warning: '!', info: 'i' };
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${icons[type] || 'i'}</span><span>${message}</span>`;
    const container = this._getContainer();
    container.innerHTML = '';
    container.appendChild(toast);
    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => {
        if (toast.parentNode) toast.remove();
      }, 220);
    }, duration);
  },
  success(message) { this.show(message, 'success'); },
  error(message) { this.show(message, 'error'); },
  warning(message) { this.show(message, 'warning'); },
  info(message) { this.show(message, 'info'); },
};

function requireAuth(role = null) {
  if (!Auth.isLoggedIn()) {
    Auth.logout();
    return false;
  }
  if (role && Auth.getRole() !== role) {
    Toast.error('Access denied. Insufficient permissions.');
    Auth.logout(Auth.getLoginPageForRole(role));
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

let openModalCount = 0;

function syncBodyModalLock() {
  if (!document.body) return;
  const shouldLock = openModalCount > 0;
  document.body.classList.toggle('overflow-hidden', shouldLock);
}

function openModal(id) {
  const el = document.getElementById(id);
  if (!el || el.classList.contains('open')) return;
  el.classList.add('open');
  openModalCount += 1;
  syncBodyModalLock();
}

function closeModal(id) {
  const el = document.getElementById(id);
  if (!el || !el.classList.contains('open')) return;
  el.classList.remove('open');
  openModalCount = Math.max(0, openModalCount - 1);
  syncBodyModalLock();
}

document.addEventListener('click', (event) => {
  if (event.target.classList.contains('modal-overlay')) {
    closeModal(event.target.id);
  }
});

document.addEventListener('keydown', (event) => {
  if (event.key !== 'Escape') return;
  const openOverlays = [...document.querySelectorAll('.modal-overlay.open')];
  const topOverlay = openOverlays[openOverlays.length - 1];
  if (topOverlay?.id) closeModal(topOverlay.id);
});

function formatDate(dateStr) {
  if (!dateStr) return '\u2014';
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

function formatCurrency(amount) {
  if (amount == null || amount === '') return '\u2014';
  return `\u20B9${parseFloat(amount).toLocaleString('en-IN')}`;
}

function statusBadge(status, labelOverride) {
  if (typeof paymentStatusBadge === 'function' && ['paid', 'unpaid', 'pending_verification', 'failed', 'rejected', 'approved'].includes(status)) {
    return paymentStatusBadge(status, labelOverride);
  }
  const map = {
    pending: ['badge-yellow', 'Pending Review'],
    approved: ['badge-green', 'Approved'],
    rejected: ['badge-red', 'Rejected'],
    vacated: ['badge-blue', 'Vacated'],
    paid: ['badge-green', 'Paid'],
    unpaid: ['badge-yellow', 'Unpaid'],
    pending_verification: ['badge-blue', 'Under Review'],
    failed: ['badge-red', 'Failed'],
    overdue: ['badge-red', 'Overdue'],
    open: ['badge-yellow', 'Open'],
    in_progress: ['badge-blue', 'In Progress'],
    resolved: ['badge-green', 'Resolved'],
    closed: ['badge-blue', 'Closed'],
  };
  const [cls, defaultLabel] = map[status] || ['badge-blue', status];
  const label = labelOverride || defaultLabel;
  return `<span class="badge ${cls}">${label}</span>`;
}

function bookingStatusBadge(booking) {
  if (!booking) return statusBadge('pending');
  const role = Auth.getRole();
  const label = role === 'resident'
    ? (booking.resident_status_display || booking.status_display)
    : (booking.status_display || booking.resident_status_display);
  return statusBadge(booking.status, label);
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
window.bookingStatusBadge = bookingStatusBadge;
window.ApiError = ApiError;
window.Theme = Theme;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => Theme.init(), { once: true });
} else {
  Theme.init();
}
