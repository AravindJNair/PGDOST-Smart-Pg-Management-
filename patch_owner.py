import pathlib

f = pathlib.Path(r'c:\Users\aravi\OneDrive\Documents\newfinalyearproject\frontend\pages\owner-dashboard.html')
html = f.read_text(encoding='utf-8')

# The new shell (everything from </head> up to and including <div id="toast-container">)
NEW_SHELL = r'''</head>
<body>

<!-- Hamburger for mobile -->
<button class="hamburger" id="hamburger" onclick="toggleSidebar()" aria-label="Menu">
  <span></span><span></span><span></span>
</button>
<div class="ds-overlay" id="ds-overlay" onclick="closeSidebar()"></div>

<div class="ds-shell">

  <!-- ═══ SIDEBAR ═══ -->
  <aside class="ds-sidebar" id="ds-sidebar">
    <div class="sb-brand">
      <div class="sb-logo-box">
        <svg width="22" height="22" viewBox="0 0 28 28" fill="none">
          <path d="M6 22V10l8-5 8 5v12H6z" fill="white"/>
          <rect x="11" y="15" width="6" height="7" rx="1" fill="#3A5C2A"/>
        </svg>
      </div>
      <span class="sb-title">PG<strong>DOST</strong></span>
    </div>
    <div class="sb-role">PG Owner Panel</div>

    <div class="sb-section">Overview</div>
    <nav class="sb-nav">
      <button class="sb-item active" data-tab="overview" onclick="switchTab('overview')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="1" y="1" width="7" height="7" rx="2" stroke="currentColor" stroke-width="1.5"/><rect x="10" y="1" width="7" height="7" rx="2" stroke="currentColor" stroke-width="1.5"/><rect x="1" y="10" width="7" height="7" rx="2" stroke="currentColor" stroke-width="1.5"/><rect x="10" y="10" width="7" height="7" rx="2" stroke="currentColor" stroke-width="1.5"/></svg>
        Dashboard
      </button>
    </nav>

    <div class="sb-section">Management</div>
    <nav class="sb-nav">
      <button class="sb-item" data-tab="properties" onclick="switchTab('properties')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 16V7l7-4 7 4v9H2z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><rect x="7" y="11" width="4" height="5" rx="0.8" stroke="currentColor" stroke-width="1.3"/></svg>
        Properties
      </button>
      <button class="sb-item" data-tab="inquiries" onclick="switchTab('inquiries')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 2h14a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H5l-4 3V3a1 1 0 0 1 1-1z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
        Inquiries
      </button>
      <button class="sb-item" data-tab="bookings" onclick="switchTab('bookings')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="2" y="3" width="14" height="13" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M2 7h14M6 3V1M12 3V1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        Bookings
        <span class="sb-badge" id="sb-badge-bookings" style="display:none">0</span>
      </button>
      <button class="sb-item" data-tab="payments" onclick="switchTab('payments')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="1" y="4" width="16" height="11" rx="2" stroke="currentColor" stroke-width="1.5"/><path d="M1 8h16" stroke="currentColor" stroke-width="1.5"/><rect x="3" y="11" width="4" height="1.5" rx=".5" fill="currentColor"/></svg>
        Payments
      </button>
      <button class="sb-item" data-tab="complaints" onclick="switchTab('complaints')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="1.5"/><path d="M9 5.5v4M9 11.5v1" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
        Complaints
        <span class="sb-badge" id="sb-badge-complaints" style="display:none">0</span>
      </button>
      <button class="sb-item" data-tab="visitors" onclick="switchTab('visitors')">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="6" r="3" stroke="currentColor" stroke-width="1.5"/><path d="M3 15c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
        Visitors
      </button>
    </nav>

    <div class="sb-section">Links</div>
    <nav class="sb-nav">
      <a class="sb-item" href="index.html">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 9l7-7 7 7M3 8v7h4v-4h4v4h4V8" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>
        Back to Home
      </a>
    </nav>

    <div class="sb-footer">
      <div class="sb-user">
        <div class="sb-avatar" id="avatar-text">O</div>
        <div>
          <div class="sb-user-name" id="sidebar-username">Owner</div>
          <div class="sb-user-role">PG Owner</div>
        </div>
        <button class="sb-logout" onclick="ownerLogout()" title="Logout">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M11 5l3 3-3 3M14 8H6M6 2H3a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </button>
      </div>
    </div>
  </aside>

  <!-- ═══ MAIN ═══ -->
  <main class="ds-main">

    <!-- Topbar -->
    <header class="ds-topbar">
      <div class="topbar-left">
        <div class="topbar-title" id="page-title">Dashboard</div>
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
        <button id="btn-open-create-invoice-top" class="btn btn-primary btn-sm" style="display:none" onclick="document.getElementById('btn-open-create-invoice').click()">+ Invoice</button>
      </div>
    </header>

    <!-- Page Body -->
    <div class="ds-body">

      <!-- ── Overview Tab ── -->
      <div id="tab-overview" class="tab-content active">
        <!-- Stat cards -->
        <div class="ds-stats" id="stats-grid">
          <div class="ds-stat">
            <div class="stat-icon-box" style="background:rgba(92,122,74,0.12)">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 20V9l8-6 8 6v11H3z" stroke="#5C7A4A" stroke-width="1.6" stroke-linejoin="round"/><rect x="8" y="13" width="6" height="7" rx="1" stroke="#5C7A4A" stroke-width="1.4"/></svg>
            </div>
            <div class="stat-info"><div class="stat-val" id="stat-props">—</div><div class="stat-lbl">My Properties</div></div>
            <div class="stat-trend trend-neu">total</div>
          </div>
          <div class="ds-stat">
            <div class="stat-icon-box" style="background:rgba(108,99,255,0.1)">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="3" width="18" height="17" rx="2" stroke="#6C63FF" stroke-width="1.6"/><path d="M2 8h18M7 3V1M15 3V1" stroke="#6C63FF" stroke-width="1.6" stroke-linecap="round"/></svg>
            </div>
            <div class="stat-info"><div class="stat-val" id="stat-pending">—</div><div class="stat-lbl">Pending Bookings</div></div>
            <div class="stat-trend trend-down" id="trend-pending">awaiting</div>
          </div>
          <div class="ds-stat">
            <div class="stat-icon-box" style="background:rgba(67,160,106,0.1)">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="9" cy="7" r="4" stroke="#43A06A" stroke-width="1.6"/><path d="M2 20c0-4 3.134-7.2 7-7.2" stroke="#43A06A" stroke-width="1.6" stroke-linecap="round"/><circle cx="16" cy="15" r="4" stroke="#43A06A" stroke-width="1.5"/><path d="M14 15h4M16 13v4" stroke="#43A06A" stroke-width="1.4" stroke-linecap="round"/></svg>
            </div>
            <div class="stat-info"><div class="stat-val" id="stat-active">—</div><div class="stat-lbl">Active Residents</div></div>
            <div class="stat-trend trend-up">live</div>
          </div>
          <div class="ds-stat">
            <div class="stat-icon-box" style="background:rgba(229,155,34,0.1)">
              <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="8" stroke="#E59B22" stroke-width="1.6"/><path d="M11 7v4.5M11 14v.5" stroke="#E59B22" stroke-width="1.8" stroke-linecap="round"/></svg>
            </div>
            <div class="stat-info"><div class="stat-val" id="stat-open">—</div><div class="stat-lbl">Open Tickets</div></div>
            <div class="stat-trend trend-down" id="trend-tickets">open</div>
          </div>
        </div>

        <!-- Two-column dashboard grid -->
        <div class="dash-grid">
          <!-- LEFT -->
          <div style="display:flex;flex-direction:column;gap:20px;">
            <!-- Property Occupancy bars -->
            <div class="ds-card">
              <div class="ds-card-header">
                <div><div class="ds-card-title">Property Occupancy</div><div class="ds-card-sub">Room fill rate across your properties</div></div>
              </div>
              <div style="padding:20px;" id="occ-bars"><p style="color:#6B7B5A;font-size:.85rem;">Loading...</p></div>
            </div>
            <!-- Pending Approvals -->
            <div class="ds-card">
              <div class="ds-card-header">
                <div><div class="ds-card-title">Pending Approvals</div><div class="ds-card-sub">Booking requests awaiting your action</div></div>
                <button class="btn btn-secondary btn-sm" onclick="switchTab('bookings')">View All</button>
              </div>
              <div id="pending-bookings-list" style="padding:4px 0;"><div style="display:flex;justify-content:center;padding:24px;"><div class="spinner"></div></div></div>
            </div>
          </div>

          <!-- RIGHT -->
          <div style="display:flex;flex-direction:column;gap:20px;">
            <!-- Occupancy Ring -->
            <div class="ds-card">
              <div class="ds-card-header"><div class="ds-card-title">Overall Occupancy</div></div>
              <div class="occ-ring-wrap">
                <svg class="ring-svg" width="130" height="130" viewBox="0 0 90 90">
                  <defs><linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#8FAD72"/><stop offset="100%" stop-color="#5C7A4A"/></linearGradient></defs>
                  <circle class="ring-track" cx="45" cy="45" r="40"/>
                  <circle class="ring-fill" cx="45" cy="45" r="40" id="ringFill"/>
                  <text x="45" y="40" text-anchor="middle" dominant-baseline="middle" font-family="Outfit" font-size="12" font-weight="800" fill="#3A5C2A" id="ringPct">—%</text>
                  <text x="45" y="54" text-anchor="middle" dominant-baseline="middle" font-family="Outfit" font-size="6" fill="#6B7B5A">Occupied</text>
                </svg>
                <div style="display:flex;gap:24px;text-align:center;">
                  <div><p style="font-size:1.1rem;font-weight:800;color:#3A5C2A;" id="ring-occupied">—</p><p style="font-size:.72rem;color:#6B7B5A;">Occupied</p></div>
                  <div><p style="font-size:1.1rem;font-weight:800;color:#43A06A;" id="ring-available">—</p><p style="font-size:.72rem;color:#6B7B5A;">Available</p></div>
                </div>
              </div>
            </div>

            <!-- Needs Attention -->
            <div class="ds-card">
              <div class="ds-card-header"><div class="ds-card-title">Needs Attention</div></div>
              <div>
                <button class="needs-item w-full" style="border:none;background:none;font-family:Outfit,sans-serif;text-align:left;width:100%;" onclick="switchTab('bookings')">
                  <div class="act-dot" style="background:rgba(229,155,34,0.12)"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="2" width="12" height="12" rx="2" stroke="#E59B22" stroke-width="1.4"/><path d="M5 8h6M5 5.5h3" stroke="#E59B22" stroke-width="1.4" stroke-linecap="round"/></svg></div>
                  <div class="act-body"><div class="act-msg">Pending booking requests</div><div class="act-time">Awaiting approval</div></div>
                  <span class="act-tag" style="background:rgba(229,155,34,0.12);color:#E59B22;" id="attn-bookings">—</span>
                </button>
                <button class="needs-item w-full" style="border:none;background:none;font-family:Outfit,sans-serif;text-align:left;width:100%;" onclick="switchTab('complaints')">
                  <div class="act-dot" style="background:rgba(224,86,86,0.1)"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="6" stroke="#e05656" stroke-width="1.4"/><path d="M8 5v3.5M8 10v.5" stroke="#e05656" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  <div class="act-body"><div class="act-msg">Open complaints</div><div class="act-time">Unresolved tickets</div></div>
                  <span class="act-tag" style="background:rgba(224,86,86,0.1);color:#e05656;" id="attn-complaints">—</span>
                </button>
                <button class="needs-item w-full" style="border:none;background:none;font-family:Outfit,sans-serif;text-align:left;width:100%;" onclick="switchTab('payments')">
                  <div class="act-dot" style="background:rgba(92,122,74,0.1)"><svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="4" width="14" height="9" rx="1.5" stroke="#5C7A4A" stroke-width="1.4"/><path d="M1 7h14" stroke="#5C7A4A" stroke-width="1.4"/></svg></div>
                  <div class="act-body"><div class="act-msg">Overdue payments</div><div class="act-time">This month</div></div>
                  <span class="act-tag" style="background:rgba(92,122,74,0.1);color:#5C7A4A;" id="attn-payments">—</span>
                </button>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="ds-card">
              <div class="ds-card-header"><div class="ds-card-title">Quick Actions</div></div>
              <div class="qa-grid">
                <button class="qa-btn" onclick="openModal('modal-add-property')">
                  <div class="qa-icon" style="background:rgba(92,122,74,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M3 18V8l7-5 7 5v10H3z" stroke="#5C7A4A" stroke-width="1.5" stroke-linejoin="round"/><rect x="7.5" y="12" width="5" height="6" rx=".8" stroke="#5C7A4A" stroke-width="1.3"/></svg></div>
                  Add Property
                </button>
                <button class="qa-btn" onclick="switchTab('bookings')">
                  <div class="qa-icon" style="background:rgba(108,99,255,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="2" y="3" width="16" height="15" rx="2" stroke="#6C63FF" stroke-width="1.5"/><path d="M2 8h16M7 3V1M13 3V1" stroke="#6C63FF" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Bookings
                </button>
                <button class="qa-btn" onclick="switchTab('payments'); document.getElementById('btn-open-create-invoice').click()">
                  <div class="qa-icon" style="background:rgba(67,160,106,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1" y="5" width="18" height="12" rx="2" stroke="#43A06A" stroke-width="1.5"/><path d="M1 9h18M5 13h5" stroke="#43A06A" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Create Invoice
                </button>
                <button class="qa-btn" onclick="switchTab('visitors')">
                  <div class="qa-icon" style="background:rgba(168,85,247,0.1)"><svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="7" r="3.5" stroke="#A855F7" stroke-width="1.5"/><path d="M4 17c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#A855F7" stroke-width="1.5" stroke-linecap="round"/></svg></div>
                  Visitors
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Properties Tab ── -->
      <div id="tab-properties" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">My Properties</h2><p class="section-subtitle">Manage your PG listings</p></div>
          <button class="btn btn-primary btn-sm" onclick="openModal('modal-add-property')">+ Add Property</button>
        </div>
        <div id="properties-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- ── Inquiries Tab ── -->
      <div id="tab-inquiries" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">Property Inquiries</h2><p class="section-subtitle">Messages from interested residents</p></div>
        </div>
        <div id="inquiries-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- ── Bookings Tab ── -->
      <div id="tab-bookings" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">All Bookings</h2><p class="section-subtitle">Manage resident applications</p></div>
        </div>
        <div id="bookings-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- ── Payments Tab ── -->
      <div id="tab-payments" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">Invoices</h2><p class="section-subtitle">Rent invoices for your residents</p></div>
          <button id="btn-open-create-invoice" class="btn btn-primary btn-sm">+ Create Invoice</button>
        </div>
        <div id="payments-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- ── Complaints Tab ── -->
      <div id="tab-complaints" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">Complaints</h2><p class="section-subtitle">Resident maintenance &amp; support tickets</p></div>
        </div>
        <div id="complaints-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

      <!-- ── Visitors Tab ── -->
      <div id="tab-visitors" class="tab-content">
        <div class="section-header">
          <div><h2 class="section-title">Visitor Log</h2><p class="section-subtitle">Log and track visitor entries</p></div>
          <button id="btn-open-log-visitor" class="btn btn-primary btn-sm">+ Log Visitor</button>
        </div>
        <div id="visitors-list"><div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div></div>
      </div>

    </div><!-- /ds-body -->
  </main>
</div><!-- /ds-shell -->

<div id="toast-container">'''

f2 = pathlib.Path(r'c:\Users\aravi\OneDrive\Documents\newfinalyearproject\frontend\pages\owner-dashboard.html')
html = f2.read_text(encoding='utf-8')

# Find markers
start_marker = '</head>'
end_marker = '<div id="toast-container">'

start_idx = html.find(start_marker)
end_idx = html.find(end_marker) + len(end_marker)

if start_idx == -1 or end_idx == -1:
    print('ERROR: markers not found')
else:
    new_html = html[:start_idx] + NEW_SHELL + html[end_idx:]
    f2.write_text(new_html, encoding='utf-8')
    print('Owner dashboard shell replaced successfully')
