/**
 * PGDOST — Cinematic scroll & motion (enhancement layer only)
 */
const Cinematic = {
  enabled: false,
  reduced: false,
  mobile: false,
  parallax: false,
  revealObserver: null,
  scanTimer: null,
  rafId: 0,
  scrollY: 0,

  REVEAL_SELECTORS: [
    '.card:not(.modal)',
    '.property-card',
    '.feature-card',
    '.role-card',
    '.ds-stat',
    '.stat-item',
    '.manage-card',
    '.resident-property-card',
    '.resident-info-card',
    '.resident-panel',
    '.resident-ticket-card',
    '.resident-search-card',
    '.onboard-card',
    '.apply-form-section',
    '.booking-status-card',
    '.pending-banner',
    '.empty-state',
    '.table-wrapper',
    '.auth-card .card',
    '.invoice-card',
    '.payment-card',
    '.complaint-card',
    '.wishlist-card',
    '.qa-btn',
    '.section-header',
    '.features-grid > *',
    '.roles-grid > *',
    '.stats-inner > *',
    '.ds-stats > *',
    '.dash-grid > *',
    '.properties-grid > .property-card',
  ].join(','),

  STAGGER_PARENTS: [
    '.ds-stats',
    '.stats-inner',
    '.properties-grid',
    '.features-grid',
    '.roles-grid',
    '.dash-grid',
    '#properties-grid',
    '.apply-form-main',
    '.resident-discover-grid',
  ],

  init() {
    this.reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.mobile = window.matchMedia('(max-width: 768px)').matches;
    this.parallax = !this.reduced && !this.mobile;

    if (this.reduced) {
      document.documentElement.classList.add('cine-reduced');
      return;
    }

    this.enabled = true;
    document.documentElement.classList.add('cinematic-ready');
    if (this.mobile) document.documentElement.classList.add('cine-mobile');
    if (this.parallax) document.documentElement.classList.add('cinematic-parallax');

    this.ensureScrollProgress();
    this.initReveals();
    this.initParallax();
    this.initPropertyDepth();
    this.initScrollProgress();
    this.initTabPanels();
    this.watchDynamicContent();
    this.bindModalHooks();
  },

  ensureScrollProgress() {
    if (document.querySelector('.cine-scroll-progress')) return;
    const bar = document.createElement('div');
    bar.className = 'cine-scroll-progress';
    bar.setAttribute('aria-hidden', 'true');
    document.body.appendChild(bar);
  },

  initScrollProgress() {
    const bar = document.querySelector('.cine-scroll-progress');
    if (!bar) return;

    const update = () => {
      const doc = document.documentElement;
      const scrollTop = window.scrollY || doc.scrollTop;
      const max = Math.max(1, doc.scrollHeight - window.innerHeight);
      const pct = Math.min(100, (scrollTop / max) * 100);
      bar.style.width = `${pct}%`;
      bar.classList.toggle('is-active', scrollTop > 24);
      this.scrollY = scrollTop;
    };

    window.addEventListener('scroll', () => {
      if (this.rafId) return;
      this.rafId = requestAnimationFrame(() => {
        this.rafId = 0;
        update();
        if (this.parallax) this.applyParallax();
      });
    }, { passive: true });
    update();
  },

  shouldSkipReveal(el) {
    if (!el || el.closest('.modal-overlay')) return true;
    if (el.classList.contains('cine-reveal')) return true;
    if (el.closest('[hidden], .hidden')) return true;
    if (el.classList.contains('animate-fade-up') || el.classList.contains('animate-fade-in')) return true;
    if (el.classList.contains('reveal')) return true;
    const rect = el.getBoundingClientRect();
    if (rect.width < 8 && rect.height < 8) return true;
    return false;
  },

  markReveal(el, index) {
    if (this.shouldSkipReveal(el)) return;
    el.classList.add('cine-reveal');
    el.style.setProperty('--cine-i', String(index % 12));
  },

  initReveals() {
    const nodes = document.querySelectorAll(this.REVEAL_SELECTORS);
    nodes.forEach((el, i) => this.markReveal(el, i));

    this.STAGGER_PARENTS.forEach((sel) => {
      document.querySelectorAll(sel).forEach((parent) => {
        parent.classList.add('cine-stagger');
        Array.from(parent.children).forEach((child, i) => this.markReveal(child, i));
      });
    });

    this.revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('cine-visible');
          this.revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -6% 0px' }
    );

    document.querySelectorAll('.cine-reveal').forEach((el) => {
      this.revealObserver.observe(el);
    });
  },

  rescanReveals(root = document) {
    clearTimeout(this.scanTimer);
    this.scanTimer = setTimeout(() => {
      const scope = root && root.querySelectorAll ? root : document;
      const nodes = scope.querySelectorAll(this.REVEAL_SELECTORS);
      nodes.forEach((el, i) => {
        if (el.classList.contains('cine-visible')) return;
        this.markReveal(el, i);
        if (this.revealObserver) this.revealObserver.observe(el);
      });
      root.querySelectorAll?.('.property-card')?.forEach((card) => {
        card.classList.add('cine-depth');
      });
    }, 80);
  },

  initParallax() {
    if (!this.parallax) return;
    const layer = document.querySelector('.theme-atmosphere');
    if (!layer) return;

    const items = [
      ['.ambient-glow-1', 0.04],
      ['.ambient-glow-2', 0.06],
      ['.ambient-glow-3', 0.03],
      ['.leaf-1', 0.08],
      ['.leaf-2', 0.1],
      ['.leaf-3', 0.07],
      ['.leaf-4', 0.09],
      ['.particle-1', 0.12],
      ['.particle-2', 0.14],
      ['.particle-3', 0.11],
    ];

    items.forEach(([sel, factor]) => {
      const el = layer.querySelector(sel);
      if (!el) return;
      el.dataset.cineParallax = String(factor);
    });

    this.applyParallax();
  },

  applyParallax() {
    const layer = document.querySelector('.theme-atmosphere');
    if (!layer) return;
    const y = this.scrollY;
    layer.querySelectorAll('[data-cine-parallax]').forEach((el) => {
      const factor = parseFloat(el.dataset.cineParallax) || 0.05;
      const offset = Math.round(y * factor);
      el.style.transform = `translate3d(0, ${offset}px, 0)`;
    });
  },

  initPropertyDepth() {
    if (this.mobile) return;
    document.querySelectorAll('.property-card:not([data-cine-depth])').forEach((card) => {
      card.dataset.cineDepth = '1';
      card.classList.add('cine-depth');
      card.addEventListener('mousemove', (e) => this.onCardPointer(e, card), { passive: true });
      card.addEventListener('mouseleave', () => this.resetCardPointer(card), { passive: true });
    });
  },

  onCardPointer(e, card) {
    const rect = card.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    const tiltY = (x - 0.5) * -6;
    const tiltX = (y - 0.5) * 5;
    card.style.setProperty('--cine-tilt-x', `${tiltX}deg`);
    card.style.setProperty('--cine-tilt-y', `${tiltY}deg`);
    card.style.setProperty('--cine-glow-x', `${x * 100}%`);
    card.style.setProperty('--cine-glow-y', `${y * 100}%`);
  },

  resetCardPointer(card) {
    card.style.setProperty('--cine-tilt-x', '0deg');
    card.style.setProperty('--cine-tilt-y', '0deg');
    card.style.setProperty('--cine-glow-x', '50%');
    card.style.setProperty('--cine-glow-y', '40%');
  },

  initTabPanels() {
    const animateActiveTab = () => {
      const panel = document.querySelector('.tab-content.active');
      if (!panel) return;
      panel.classList.remove('cine-tab-active');
      void panel.offsetWidth;
      panel.classList.add('cine-tab-active');
    };

    document.querySelectorAll('.sb-item[data-tab]').forEach((item) => {
      item.addEventListener('click', () => {
        requestAnimationFrame(animateActiveTab);
      });
    });

    animateActiveTab();
  },

  onModalOpen(overlay) {
    if (!this.enabled || !overlay) return;
    overlay.classList.add('cine-modal-open');
    const modal = overlay.querySelector('.modal');
    if (!modal) return;
    const fields = modal.querySelectorAll(
      '.form-group, .apply-form-section, .ds-form-group, .card, .modal-header'
    );
    fields.forEach((el, i) => el.style.setProperty('--cine-i', String(i)));
    this.rescanReveals(modal);
  },

  onModalClose(overlay) {
    if (!overlay) return;
    overlay.classList.remove('cine-modal-open');
  },

  bindModalHooks() {
    if (window.__cineModalHooked) return;
    window.__cineModalHooked = true;

    const wrap = (name) => {
      const fn = window[name];
      if (typeof fn !== 'function') return;
      window[name] = (id) => {
        const el = document.getElementById(id);
        const result = fn(id);
        if (name === 'openModal') this.onModalOpen(el);
        else this.onModalClose(el);
        return result;
      };
    };

    wrap('openModal');
    wrap('closeModal');
  },

  watchDynamicContent() {
    const observer = new MutationObserver((mutations) => {
      let touched = false;
      mutations.forEach((m) => {
        m.addedNodes.forEach((node) => {
          if (node.nodeType !== 1) return;
          touched = true;
          this.rescanReveals(node);
        });
      });
      if (touched && !this.mobile) this.initPropertyDepth();
    });
    observer.observe(document.body, { childList: true, subtree: true });
  },
};

function initCinematic() {
  if (typeof Theme !== 'undefined' && Theme.initAtmosphereLayer) {
    Theme.initAtmosphereLayer();
  }
  Cinematic.init();
}

window.Cinematic = Cinematic;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initCinematic, { once: true });
} else {
  initCinematic();
}
