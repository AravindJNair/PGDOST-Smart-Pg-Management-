import pathlib, re

f = pathlib.Path(r'c:\Users\aravi\OneDrive\Documents\newfinalyearproject\frontend\pages\resident-dashboard.html')
html = f.read_text(encoding='utf-8')

NEW_SHELL = r'''</head>
<body>
<button class="hamburger" id="hamburger" onclick="toggleSidebar()" aria-label="Menu">
  <span></span><span></span><span></span>
</button>
<div class="ds-overlay" id="ds-overlay" onclick="closeSidebar()"></div>

<div class="ds-shell">
  <!-- SIDEBAR -->
  <aside class="ds-sidebar" id="ds-sidebar">
    <div class="sb-brand">
      <div class="sb-logo-box">
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none"><path d="M6 22V10l8-5 8 5v12H6z" fill="white"/><rect x="11" y="15" width="6" height="7" rx="1" fill="#3A5C2A"/></svg>
      </div>
      <span class="sb-title">PG<strong>DOST</strong></span>
    </div>
    <div class="sb-role">Resident Portal</div>
    <div class="sb-section">My Stay</div>
    <nav class="sb-nav">
      <button class="sb-item active" data-tab="overview" onclick="switchTab('overview')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 16V7l7-4 7 4v9H2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><rect x="7" y="11" width="4" height="5" rx=".8" stroke="currentColor" stroke-width="1.3"/></svg>
        Overview
      </button>
      <button class="sb-item" data-tab="payments" onclick="switchTab('payments')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="1" y="4" width="16" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M1 8h16" stroke="currentColor" stroke-width="1.5"/><rect x="3" y="11" width="4" height="1.5" rx=".5" fill="currentColor"/></svg>
        Payments
        <span class="sb-badge" id="sb-due-badge" style="display:none">!</span>
      </button>
      <button class="sb-item" data-tab="complaints" onclick="switchTab('complaints')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M9 5.5v4M9 11.5v1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        Complaints
        <span class="sb-badge" id="sb-ticket-badge" style="display:none">0</span>
      </button>
      <button class="sb-item" data-tab="visitors" onclick="switchTab('visitors')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="6" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M3 15c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        Visitors
      </button>
    </nav>
    <div class="sb-section">Links</div>
    <nav class="sb-nav">
      <a class="sb-item" href="index.html#explore-section">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="8" cy="8" r="5" stroke="currentColor" stroke-width="1.5"/><path d="M12 12l4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        Explore PGs
      </a>
      <a class="sb-item" href="index.html">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 9l7-7 7 7M3 8v7h4v-4h4v4h4V8" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
        Back to Home
      </a>
    </nav>
    <div class="sb-footer">
      <div class="sb-user">
        <div class="sb-avatar" id="avatar-text">R</div>
        <div>
          <div class="sb-user-name" id="sidebar-username">Resident</div>
          <div class="sb-user-role">PG Resident</div>
        </div>
        <button class="sb-logout" onclick="residentLogout()" title="Logout">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M11 5l3 3-3 3M14 8H6M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>
  </aside>

  <!-- MAIN -->
  <main class="ds-main">
    <header class="ds-topbar">
      <div class="topbar-left">
        <div class="topbar-title" id="page-title">Overview</div>
        <div class="topbar-subtitle" id="topbar-date"></div>
      </div>
      <div class="topbar-search">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none"><circle cx="7" cy="7" r="5" stroke="#6B7B5A" stroke-width="1.5"/><path d="M11 11l3 3" stroke="#6B7B5A" stroke-width="1.5" stroke-linecap="round"/></svg>
        <input type="text" placeholder="Search…"/>
      </div>
      <div class="topbar-actions">
        <div style="position:relative;">
          <button class="topbar-icon-btn" onclick="toggleNotifications()" title="Notifications">
            <svg width="17" height="17" viewBox="0 0 17 17" fill="none"><path d="M8.5 1.5a5.5 5.5 0 0 0-5.5 5.5v3l-1 2h13l-1-2V7A5.5 5.5 0 0 0 8.5 1.5z" stroke="currentColor" stroke-width="1.4"/><path d="M7 13.5a1.5 1.5 0 0 0 3 0" stroke="currentColor" stroke-width="1.3"/></svg>
            <span class="notif-dot-badge" id="notif-badge"></span>
          </button>
          <div class="notif-panel" id="notif-dropdown">
            <h4>Notifications</h4>
            <div id="notif-list"><p style="font-size:.85rem;color:#6B7B5A;text-align:center;padding:10px 0">Loading...</p></div>
          </div>
        </div>
        <button class="btn btn-primary btn-sm" onclick="switchTab('complaints');setTimeout(()=>openModal('modal-new-ticket'),100)">+ Complaint</button>
      </div>
    </header>

    <div class="ds-body">

      <!-- Overview Tab -->
      <div id="tab-overview" class="tab-content active">
        <div id="status-section" class="mb-xl">
          <div style="display:flex;align-items:center;justify-content:center;min-height:100px;"><div class="spinner"></div></div>
        </div>
        <div id="stats-row" style="display:none;">
          <div class="ds-stats" style="margin-bottom:26px;">
            <div class="ds-stat">
              <div class="stat-icon-box" style="background:rgba(229,155,34,0.1)">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="5" width="18" height="13" rx="2" stroke="#E59B22" stroke-width="1.6"/><path d="M2 9h18" stroke="#E59B22" stroke-width="1.5"/><path d="M6 14h4" stroke="#E59B22" stroke-width="1.5" stroke-linecap="round"/></svg>
              </div>
              <div class="stat-info"><div class="stat-val" id="stat-due" style="color:#E59B22;">₹0</div><div class="stat-lbl">Amount Due</div></div>
              <div class="stat-trend trend-down">pending</div>
            </div>
            <div class="ds-stat">
              <div class="stat-icon-box" style="background:rgba(224,86,86,0.1)">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="8" stroke="#e05656" stroke-width="1.6"/><path d="M11 7v4.5M11 14v.5" stroke="#e05656" stroke-width="1.8" stroke-linecap="round"/></svg>
              </div>
              <div class="stat-info"><div class="stat-val" id="stat-open-tickets" style="color:#e05656;">0</div><div class="stat-lbl">Open Complaints</div></div>
              <div class="stat-trend trend-down">open</div>
            </div>
            <div class="ds-stat">
              <div class="stat-icon-box" style="background:rgba(67,160,106,0.1)">
                <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 11l5 5 9-9" stroke="#43A06A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </div>
              <div class="stat-info"><div class="stat-val" id="stat-paid" style="color:#43A06A;">0</div><div class="stat-lbl">Payments Made</div></div>
              <div class="stat-trend trend-up">paid</div>
            </div>
          </div>
          <!-- Quick actions for resident -->
          <div class="dash-grid" style="grid-template-columns:1fr 300px;">
            <div class="ds-card">
              <div class="ds-card-header"><div class="ds-card-title">Your Stay</div></div>
              <div class="ds-card-body" id="stay-detail"><p style="color:#6B7B5A;">Loading stay details...</p></div>
            </div>
            <div class="ds-card">
              <div class="ds-card-header"><div class="ds-card-title">Quick Actions</div></div>
              <div class="qa-grid">
                <button class="qa-btn" onclick="switchTab('payments')">
                  <div class="qa-icon" style="background:rgba(67,160,106,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1" y="5" width="18" height="12" rx="2" stroke="#43A06A" stroke-width="1.5"/><path d="M1 9h18M5 13h5" stroke="#43A06A" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Pay Rent
                </button>
                <button class="qa-btn" onclick="switchTab('complaints');setTimeout(()=>openModal('modal-new-ticket'),100)">
                  <div class="qa-icon" style="background:rgba(224,86,86,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="7" stroke="#e05656" stroke-width="1.5"/><path d="M10 6v4.5M10 13v.5" stroke="#e05656" stroke-width="1.6" stroke-linecap="round"/></svg></div>
                  Complaint
                </button>
                <button class="qa-btn" onclick="switchTab('visitors')">
                  <div class="qa-icon" style="background:rgba(168,85,247,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="#A855F7" stroke-width="1.5"/><path d="M4 17c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#A855F7" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Visitors
                </button>
                <a class="qa-btn" href="index.html#explore-section">
                  <div class="qa-icon" style="background:rgba(108,99,255,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="9" cy="9" r="5.5" stroke="#6C63FF" stroke-width="1.5"/><path d="M14 14l4 4" stroke="#6C63FF" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Explore PGs
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Payments Tab -->
      <div id="tab-payments" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">My Invoices</h2><p class="section-subtitle">Rent invoices from your PG owner</p></div>
        </div>
        <div id="invoices-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- Complaints Tab -->
      <div id="tab-complaints" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">My Complaints</h2><p class="section-subtitle">Track your maintenance requests</p></div>
          <button class="btn btn-primary btn-sm" onclick="openModal('modal-new-ticket')">+ New Complaint</button>
        </div>
        <div id="tickets-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- Visitors Tab -->
      <div id="tab-visitors" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">Visitor Log</h2><p class="section-subtitle">Track who has visited you</p></div>
        </div>
        <div id="visitors-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

    </div>
  </main>
</div>

<div id="toast-container">'''

# Marker replacement
start = html.find('</head>')
end   = html.find('<div id="toast-container">') + len('<div id="toast-container">')
if start == -1 or end < len('<div id="toast-container">'):
    print('ERROR: markers not found')
else:
    html = html[:start] + NEW_SHELL + html[end:]
    f.write_text(html, encoding='utf-8')
    print('Resident shell replaced')

# Patch switchTab
html = f.read_text(encoding='utf-8')
old = """  function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sidebar-item[data-tab]').forEach(i => i.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.querySelector(`.sidebar-item[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById('page-title').textContent = { overview: 'Overview', payments: 'My Payments', complaints: 'Complaints', visitors: 'Visitor Log' }[tab] || tab;
    activeTab = tab;
    if (tab === 'payments') loadInvoices();
    if (tab === 'complaints') loadTickets();
    if (tab === 'visitors') loadVisitors();
  }"""
new = """  function switchTab(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sb-item[data-tab]').forEach(i => i.classList.remove('active'));
    document.getElementById('tab-' + tab).classList.add('active');
    document.querySelector(`.sb-item[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById('page-title').textContent = { overview:'Overview', payments:'My Payments', complaints:'Complaints', visitors:'Visitor Log' }[tab] || tab;
    activeTab = tab;
    closeSidebar();
    if (tab === 'payments') loadInvoices();
    if (tab === 'complaints') loadTickets();
    if (tab === 'visitors') loadVisitors();
  }

  function toggleSidebar() {
    document.getElementById('ds-sidebar').classList.toggle('open');
    document.getElementById('ds-overlay').classList.toggle('active');
  }
  function closeSidebar() {
    document.getElementById('ds-sidebar').classList.remove('open');
    document.getElementById('ds-overlay').classList.remove('active');
  }"""
if old in html:
    html = html.replace(old, new)
    print('switchTab patched')
else:
    print('WARNING: switchTab not matched')

# Add topbar date + stay detail card
old_init = "  loadOverview();\n  loadNotifications();"
new_init = """  loadOverview();
  loadNotifications();
  document.getElementById('topbar-date').textContent =
    new Date().toLocaleDateString('en-IN',{weekday:'long',year:'numeric',month:'long',day:'numeric'});"""
if old_init in html:
    html = html.replace(old_init, new_init)
    print('init patched')

# Patch loadOverview to populate stay-detail card + show stats-row
old_stats_show = "      document.getElementById('stats-row').classList.remove('hidden');"
new_stats_show = """      document.getElementById('stats-row').style.display = '';
      // Populate stay detail card
      const sd = document.getElementById('stay-detail');
      if (sd) sd.innerHTML = `
        <div style="display:flex;align-items:center;gap:18px;flex-wrap:wrap;">
          <div style="font-size:3rem;">🏠</div>
          <div>
            <div style="font-size:1.15rem;font-weight:800;color:#3A5C2A;margin-bottom:4px;">${activeBooking.property_name}</div>
            <div style="font-size:.82rem;color:#6B7B5A;margin-bottom:6px;">
              ${activeBooking.room_number ? '<span style="background:rgba(92,122,74,0.1);padding:2px 10px;border-radius:20px;font-weight:600;">Room '+activeBooking.room_number+'</span>' : ''}
              ${activeBooking.move_in_date ? ' &nbsp; Since '+formatDate(activeBooking.move_in_date) : ''}
            </div>
            <span style="background:rgba(67,160,106,0.12);color:#43A06A;font-size:.72rem;font-weight:700;padding:3px 10px;border-radius:20px;">✓ Active</span>
          </div>
        </div>`;"""
if old_stats_show in html:
    html = html.replace(old_stats_show, new_stats_show)
    print('stats-row show patched')

# Update notif badge display (was inline style with display:none then display:flex)
old_badge = "id=\"notif-badge\" style=\"position:absolute; top:-5px; right:-5px; background:var(--clr-danger); color:white; border-radius:50%; width:18px; height:18px; font-size:10px; display:flex; align-items:center; justify-content:center; display:none;\""
if old_badge in html:
    html = html.replace(old_badge, 'id="notif-badge" class="notif-dot-badge"')
    print('notif badge patched')

# Update notif badge JS
old_notif_show = "              badge.style.display = 'flex';"
new_notif_show = "              badge.style.display = 'flex'; badge.style.width='auto'; badge.style.height='auto';"
html = html.replace(old_notif_show, new_notif_show)

# Patch btn for complaint badge
old_ticket_load = "      if (!tickets.length) { el.innerHTML = "
# Find loadTickets and add badge update
old_load_tickets_api = "      const tickets = await api.get('/complaints/my/');"
new_load_tickets_api = """      const tickets = await api.get('/complaints/my/');
      const openT = tickets.filter(t => t.status !== 'resolved').length;
      const tb = document.getElementById('sb-ticket-badge');
      if (tb) { if(openT>0){tb.textContent=openT;tb.style.display='';}else{tb.style.display='none';} }"""
if old_load_tickets_api in html:
    html = html.replace(old_load_tickets_api, new_load_tickets_api)
    print('ticket badge patched')

# Add toast and form styles
old_head_end = '</head>'
if old_head_end in html and '.btn-primary' not in html:
    pass  # already added

f.write_text(html, encoding='utf-8')
print('Resident dashboard fully patched')
