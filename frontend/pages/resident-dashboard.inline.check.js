
  // Strict guard — only 'resident' role allowed
  if (!Auth.isLoggedIn() || Auth.getRole() !== 'resident') {
    Auth.logout('login.html');
  }

  function residentLogout() {
    Auth.logout('login.html');
  }

  function toggleSidebar() {
    document.getElementById('ds-sidebar').classList.toggle('open');
    document.getElementById('ds-overlay').classList.toggle('active');
  }
  function closeSidebar() {
    document.getElementById('ds-sidebar').classList.remove('open');
    document.getElementById('ds-overlay').classList.remove('active');
  }

  const user = Auth.getUser();
  document.getElementById('sidebar-username').textContent = user?.username || 'Resident';
  document.getElementById('avatar-text').textContent = (user?.username || 'R')[0].toUpperCase();
  document.getElementById('welcome-avatar').textContent = (user?.username || 'R')[0].toUpperCase();
  document.getElementById('topbar-avatar').textContent = (user?.username || 'R')[0].toUpperCase();
  document.getElementById('topbar-username').textContent = user?.username || 'Resident';

  let activeBooking = null;
  let activeTab = 'overview';
  let latestInvoices = [];
  let latestTickets = [];
  let residentBookings = [];
  let visitorRealtimeTimer = null;

  function stopVisitorRealtime() {
    if (!visitorRealtimeTimer) return;
    clearInterval(visitorRealtimeTimer);
    visitorRealtimeTimer = null;
  }

  function startVisitorRealtime() {
    stopVisitorRealtime();
    visitorRealtimeTimer = setInterval(() => {
      if (activeTab !== 'visitors' || document.hidden) return;
      loadVisitors(true);
    }, 8000);
  }

  function switchTab(tab) {
    const nextTab = document.getElementById('tab-' + tab);
    if (!nextTab) return;
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.sb-item[data-tab]').forEach(i => i.classList.remove('active'));
    nextTab.classList.add('active');
    document.querySelector(`.sb-item[data-tab="${tab}"]`)?.classList.add('active');
    document.getElementById('page-title').textContent = {
      overview: 'Resident Dashboard',
      payments: 'My Payments',
      complaints: 'Complaints',
      visitors: 'Visitor Log',
      bookings: 'Booking Flow',
      wishlist: 'Wishlist',
      reviews: 'My Reviews',
      profile: 'My Profile',
    }[tab] || tab;
    activeTab = tab;
    if (tab !== 'visitors') {
      stopVisitorRealtime();
    }
    if (tab === 'overview') {
      if (window.location.hash) history.replaceState(null, '', window.location.pathname + window.location.search);
    } else {
      history.replaceState(null, '', `${window.location.pathname}${window.location.search}#${tab}`);
    }
    closeSidebar();
    if (tab === 'payments') loadInvoices();
    if (tab === 'complaints') loadTickets();
    if (tab === 'visitors') {
      loadVisitors();
      startVisitorRealtime();
    }
    if (tab === 'bookings') loadBookingFlow();
    if (tab === 'wishlist') loadWishlist();
    if (tab === 'reviews') loadMyReviews();
    if (tab === 'profile') loadResidentProfile();
  }

  const residentPropertyImages = [
    'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1502672260266-1c1ef937d166?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1512918728675-ed5a9ecdeb87?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1560185127-6ed189bf04f5?auto=format&fit=crop&w=900&q=85',
    'https://images.unsplash.com/photo-1480074568708-e7b720bb3f09?auto=format&fit=crop&w=900&q=85',
  ];
  function getResidentPropertyImage(prop, index = 0) {
    if (prop?.primary_image_url) return prop.primary_image_url;
    const id = Number(prop?.id) || 0;
    const nameSeed = String(prop?.name || '').split('').reduce((sum, ch) => sum + ch.charCodeAt(0), 0);
    return residentPropertyImages[(id + nameSeed + index) % residentPropertyImages.length];
  }

  function showPremiumOverview() {
    document.getElementById('resident-overview-loading')?.classList.add('hidden');
    document.getElementById('resident-overview-content')?.classList.remove('hidden');
  }

  function renderStaySummary() {
    const card = document.getElementById('stay-summary-card');
    if (!card) return;
    if (!activeBooking) {
      card.innerHTML = `<div class="resident-card-icon">⌂</div><span class="resident-pill">Explore</span><div class="resident-info-title">Room Details</div><div class="resident-info-strong">No active stay yet</div><p class="text-muted">Apply to a verified PG to start managing your stay.</p>`;
      return;
    }
    card.innerHTML = `<div class="resident-card-icon">⌂</div><span class="resident-pill">Active Stay</span><div class="resident-info-title">Room Details</div><div class="resident-info-strong">${activeBooking.room_number ? `Room ${activeBooking.room_number}, ` : ''}${activeBooking.property_name}</div><p>${activeBooking.move_in_date ? `Moved in ${formatDate(activeBooking.move_in_date)}` : 'Current resident booking'}</p>`;
  }

  function renderRenewalSummary() {
    const card = document.getElementById('renewal-summary-card');
    if (!card) return;
    const nextDue = latestInvoices.find(i => i.status !== 'paid') || latestInvoices[0];
    card.innerHTML = `<div class="resident-card-icon dark">▣</div><span class="resident-pill">Upcoming</span><div class="resident-info-title">${nextDue ? 'Next Rent Due' : 'Lease Renewal'}</div><div class="resident-info-strong">${nextDue ? formatDate(nextDue.due_date) : 'Not scheduled'}</div><p>${nextDue ? `${formatCurrency(nextDue.amount)} for ${nextDue.month_display} ${nextDue.year}` : 'Notice period and renewal details will appear here.'}</p>`;
  }

  function renderAlertSummary() {
    const card = document.getElementById('alert-summary-card');
    if (!card) return;
    const urgent = latestTickets.find(t => t.priority === 'urgent' && t.status !== 'resolved');
    const unpaid = latestInvoices.find(i => i.status !== 'paid');
    if (urgent) card.innerHTML = `<div class="resident-card-icon alert">!</div><span class="resident-pill alert">Urgent Alert</span><div class="resident-info-strong">${urgent.title}</div><p>${urgent.description || 'Your owner has an urgent maintenance ticket to resolve.'}</p>`;
    else if (unpaid) card.innerHTML = `<div class="resident-card-icon alert">₹</div><span class="resident-pill alert">Payment Due</span><div class="resident-info-strong">${formatCurrency(unpaid.amount)} pending</div><p>Due on ${formatDate(unpaid.due_date)} for ${unpaid.month_display} ${unpaid.year}.</p>`;
    else card.innerHTML = `<div class="resident-card-icon alert">✓</div><span class="resident-pill alert">All Clear</span><div class="resident-info-strong">No urgent alerts</div><p>Your payments and maintenance requests look calm right now.</p>`;
  }

  function renderOverviewPayments() {
    const el = document.getElementById('overview-payments-list');
    if (!el) return;
    const recent = latestInvoices.slice(0, 3);
    if (!recent.length) { el.innerHTML = '<div class="resident-empty-dashed">No recent invoices yet</div>'; return; }
    el.innerHTML = recent.map(inv => `<div class="resident-pay-row"><div>${inv.month_display}<br>${inv.year}</div><strong>${formatCurrency(inv.amount)}</strong><span class="resident-status ${inv.status === 'paid' ? 'paid' : 'unpaid'}">${inv.status === 'paid' ? 'Paid' : 'Unpaid'}</span>${inv.status === 'paid' ? `<button class="resident-mini-link" onclick="showReceipt(${inv.id})">Receipt</button>` : `<button class="resident-round-pay" onclick="openPayModal(${inv.id})">Pay<br>Now</button>`}</div>`).join('');
  }

  function renderOverviewComplaints() {
    const el = document.getElementById('overview-complaints-list');
    if (!el) return;
    const active = latestTickets.filter(t => t.status !== 'resolved');
    document.getElementById('overview-active-count').textContent = `${active.length} ACTIVE`;
    if (!active.length) { el.innerHTML = '<div class="resident-empty-dashed">No other active maintenance tickets</div>'; return; }
    el.innerHTML = active.slice(0, 2).map(t => `<div class="resident-ticket-card"><div class="resident-ticket-title">${t.title}</div><p>${t.description || 'No description provided.'}</p><div class="resident-ticket-meta"><span>Ref: #TKT-${String(t.id).padStart(4, '0')}</span><button class="resident-mini-link" onclick="switchTab('complaints')">Track Update</button></div></div>`).join('');
  }

  async function loadDiscoverProperties() {
    const grid = document.getElementById('resident-discover-grid');
    if (!grid) return;
    try {
      const res = await api.get('/properties/?page_size=3&city=Bangalore');
      const props = (res.results || res).slice(0, 3);
      grid.innerHTML = props.map((p, index) => `
        <article class="resident-property-card">
          <a href="index.html#explore-section">
            <div class="resident-property-img" style="background-image:url('${getResidentPropertyImage(p, index)}');background-size:cover;background-position:center;">
              <span class="resident-rating">★ ${p.avg_rating || (4.8 - index * 0.1).toFixed(1)}</span>
            </div>
          </a>
          <div class="resident-property-body">
            <div class="resident-property-title">${p.name}</div>
            <div class="resident-property-loc">⌖ ${p.address || p.city}</div>
            <div class="resident-property-rent">${p.min_rent ? formatCurrency(p.min_rent) : 'On request'}<span style="font-weight:400;font-size:.78rem;">/mo</span></div>
            <div class="flex gap-sm mt-sm">
              <a class="btn btn-secondary btn-sm" href="index.html?viewProperty=${p.id}#explore-section">View</a>
              <a class="btn btn-primary btn-sm" href="index.html?bookProperty=${p.id}#explore-section">Request Booking</a>
            </div>
          </div>
        </article>
      `).join('') + `<a class="resident-search-card" href="index.html#explore-section"><div class="resident-search-icon">⌕</div><strong>Want more options?</strong><p>Browse 50+ managed properties in your city.</p><span class="btn btn-secondary">Start Searching</span></a>`;
    } catch {
      grid.innerHTML = '<div class="resident-empty-dashed">Could not load suggested PGs right now.</div>';
    }
  }

  async function refreshPremiumOverview() {
    try {
      const [invoices, tickets] = await Promise.all([api.get('/payments/my/'), api.get('/complaints/my/')]);
      latestInvoices = invoices;
      latestTickets = tickets;
      latestInvoices.forEach(inv => residentInvoicesMap[inv.id] = inv);
    } catch {
      latestInvoices = [];
      latestTickets = [];
    }
    renderStaySummary();
    renderRenewalSummary();
    renderAlertSummary();
    renderOverviewPayments();
    renderOverviewComplaints();
    loadDiscoverProperties();
    showPremiumOverview();
  }

  // ── Overview: Load booking status ──────────────────────────
  async function loadOverview() {
    const section = document.getElementById('status-section');
    try {
      activeBooking = await api.get('/bookings/active/');
      section.innerHTML = `
        <div class="booking-status-card">
          <div class="flex items-center justify-between flex-wrap gap-md">
            <div>
              <div class="text-xs text-muted font-semibold uppercase mb-sm" style="letter-spacing:.1em">Current Stay</div>
              <h3 class="text-2xl font-bold mb-xs">${activeBooking.property_name}</h3>
              <div class="flex items-center gap-sm flex-wrap">
                ${bookingStatusBadge(activeBooking)}
                ${activeBooking.room_number ? `<span class="tag">Room ${activeBooking.room_number}</span>` : ''}
                ${activeBooking.move_in_date ? `<span class="tag">Since ${formatDate(activeBooking.move_in_date)}</span>` : ''}
              </div>
            </div>
            <div class="text-center">
              <div class="text-5xl">🏠</div>
              <p class="text-xs text-muted mt-sm">Your PG</p>
            </div>
          </div>
        </div>`;
      document.getElementById('stats-row').style.display = '';
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
        </div>`;
      loadStats();
      refreshPremiumOverview();
    } catch (err) {
      // No active booking — show pending or explore state
      try {
        const bookings = await api.get('/bookings/my/');
        const pending = bookings.find(b => b.status === 'pending');
        if (pending) {
          section.innerHTML = `
            <div class="pending-banner">
              <div class="text-4xl mb-md">⏳</div>
              <h3 class="text-xl font-bold mb-sm">Pending Owner Approval</h3>
              <p class="text-muted mb-md">Your application to <strong>${pending.property_name}</strong> is awaiting owner review.</p>
              ${bookingStatusBadge(pending)}
            </div>`;
        } else {
          section.innerHTML = `
            <div class="card text-center">
              <div class="text-4xl mb-md">🔍</div>
              <h3 class="text-xl font-bold mb-sm">No Active Booking</h3>
              <p class="text-muted mb-lg">You haven't moved into any PG yet. Browse the marketplace to apply.</p>
              <a href="index.html#explore-section" class="btn btn-primary">Explore PGs</a>
            </div>`;
        }
      } catch { section.innerHTML = '<p class="text-muted text-center">Could not load booking status.</p>'; }
      refreshPremiumOverview();
    }
  }

  async function loadStats() {
    try {
      const [invoices, tickets] = await Promise.all([
        api.get('/payments/my/'),
        api.get('/complaints/my/'),
      ]);
      const due = invoices.filter(i => !['paid', 'pending_verification'].includes(i.status)).reduce((s, i) => s + parseFloat(i.total_amount != null ? i.total_amount : i.amount), 0);
      const openTickets = tickets.filter(t => t.status === 'open' || t.status === 'in_progress').length;
      const paid = invoices.filter(i => i.status === 'paid').length;
      document.getElementById('stat-due').textContent = formatCurrency(due);
      document.getElementById('stat-open-tickets').textContent = openTickets;
      document.getElementById('stat-paid').textContent = paid;
      const dueBadge = document.getElementById('sb-due-badge');
      if (dueBadge) {
        dueBadge.style.display = due > 0 ? '' : 'none';
      }
    } catch {}
  }

  // ── Payments (see resident-payments.js) ────────────────
  function showReceipt(idOrObj) {
    const inv = (typeof idOrObj === 'object') ? idOrObj : residentInvoicesMap[idOrObj];
    if (!inv) { Toast.error('Receipt data not found.'); return; }
    document.getElementById('rcpt-id').textContent       = '#' + inv.id;
    document.getElementById('rcpt-resident').textContent  = inv.resident_username || inv.resident;
    document.getElementById('rcpt-property').textContent  = inv.property_name;
    document.getElementById('rcpt-period').textContent    = inv.month_display + ' ' + inv.year;
    document.getElementById('rcpt-amount').textContent    = formatCurrency(inv.total_amount != null ? inv.total_amount : inv.amount);
    document.getElementById('rcpt-due').textContent       = formatDate(inv.due_date);
    document.getElementById('rcpt-paid-on').textContent   = formatDate(inv.payment_date || inv.paid_at);
    document.getElementById('rcpt-txn').textContent       = inv.transaction_id || 'N/A';
    document.getElementById('rcpt-notes').textContent     = inv.notes || '—';
    openModal('modal-receipt');
  }

  // ── Tickets ───────────────────────────────────────────────
  async function loadTickets() {
    const el = document.getElementById('tickets-list');
    if (activeBooking) document.getElementById('ticket-property-id').value = activeBooking.property;
    try {
      const tickets = await api.get('/complaints/my/');
      const openT = tickets.filter(t => t.status !== 'resolved').length;
      const tb = document.getElementById('sb-ticket-badge');
      if (tb) { if(openT>0){tb.textContent=openT;tb.style.display='';}else{tb.style.display='none';} }
      if (!tickets.length) { el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">📋</div><h3>No Complaints</h3><p>Raise a complaint if you have a maintenance or service issue.</p></div>'; return; }
      el.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>#</th><th>Subject</th><th>Category</th><th>Priority</th><th>Status</th><th>Date</th></tr></thead>
        <tbody>${tickets.map(t => `
          <tr><td>#${t.id}</td><td class="font-semibold">${t.title}<br><span class="text-xs text-muted">${t.owner_response ? `<b>Owner Reply:</b> ${t.owner_response}` : 'No reply yet'}</span></td><td>${t.category_display}</td>
          <td class="${t.priority === 'urgent' ? 'priority-urgent' : t.priority === 'high' ? 'priority-high' : ''} font-semibold">${t.priority_display}</td>
          <td>${statusBadge(t.status)}</td><td>${formatDate(t.created_at)}</td></tr>`).join('')}
        </tbody></table></div>`;
    } catch { el.innerHTML = '<p class="text-muted text-center py-xl">Failed to load complaints.</p>'; }
  }

  document.getElementById('new-ticket-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!activeBooking) { Toast.warning('You need an active booking to raise a complaint.'); return; }
    const btn = e.target.querySelector('button[type=submit]');
    btn.disabled = true; btn.textContent = 'Submitting…';
    try {
      await api.post('/complaints/my/', {
        property: activeBooking.property,
        title: document.getElementById('ticket-title').value,
        category: document.getElementById('ticket-category').value,
        priority: document.getElementById('ticket-priority').value,
        description: document.getElementById('ticket-desc').value,
      });
      closeModal('modal-new-ticket');
      Toast.success('Complaint submitted successfully!');
      e.target.reset();
      await loadTickets();
      refreshPremiumOverview();
    } catch (err) { Toast.error(err.message); }
    finally { btn.disabled = false; btn.textContent = 'Submit Complaint'; }
  });

  document.getElementById('resident-profile-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    const btn = document.getElementById('profile-save-btn');
    const err = document.getElementById('profile-save-error');
    err.classList.add('hidden');
    btn.disabled = true;
    btn.textContent = 'Saving...';
    try {
      const payload = {
        first_name: document.getElementById('profile-first-name').value.trim(),
        last_name: document.getElementById('profile-last-name').value.trim(),
        email: document.getElementById('profile-email').value.trim(),
        phone_number: document.getElementById('profile-phone').value.trim(),
      };
      await api.patch('/auth/profile/', payload);
      Auth.setUser({ ...(Auth.getUser() || {}), role: 'resident', username: Auth.getUser()?.username });
      Toast.success('Profile updated successfully.');
    } catch (error) {
      err.textContent = error.message || 'Unable to update profile.';
      err.classList.remove('hidden');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Save Profile';
    }
  });

  // ── Visitors ──────────────────────────────────────────────
  function formatDateTime(dateStr) {
  if (!dateStr) return '-';
  return new Date(dateStr).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function visitorStatusBadge(status) {
  if (status === 'approved') return '<span class="badge badge-green">Approved</span>';
  if (status === 'rejected') return '<span class="badge badge-red">Rejected</span>';
  return '<span class="badge badge-yellow">Pending</span>';
}

function getVisitLifecycleStatus(checkIn, checkOut, apiStatus = '') {
  const normalized = (apiStatus || '').toLowerCase();
  if (['upcoming', 'active', 'completed'].includes(normalized)) return normalized;
  const nowMs = Date.now();
  const checkInMs = checkIn ? new Date(checkIn).getTime() : Number.NaN;
  const checkOutMs = checkOut ? new Date(checkOut).getTime() : Number.NaN;
  if (Number.isFinite(checkOutMs) && nowMs >= checkOutMs) return 'completed';
  if (Number.isFinite(checkInMs) && nowMs >= checkInMs) return 'active';
  return 'upcoming';
}

function visitLifecycleBadge(status) {
  if (status === 'completed') return '<span class="badge badge-green">Completed</span>';
  if (status === 'active') return '<span class="badge badge-yellow">Active / Inside</span>';
  return '<span class="badge badge-blue">Upcoming</span>';
}

function toLocalDateTimeInputValue(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hour = String(date.getHours()).padStart(2, '0');
  const minute = String(date.getMinutes()).padStart(2, '0');
  return `${year}-${month}-${day}T${hour}:${minute}`;
}

function calculateVisitDurationLabel(checkIn, checkOut) {
  if (!checkIn || !checkOut) return '-';
  const start = new Date(checkIn).getTime();
  const end = new Date(checkOut).getTime();
  if (!Number.isFinite(start) || !Number.isFinite(end) || end <= start) return '-';
  const mins = Math.floor((end - start) / 60000);
  const hours = Math.floor(mins / 60);
  const remMins = mins % 60;
  if (hours && remMins) return `${hours}h ${remMins}m`;
  if (hours) return `${hours}h`;
  return `${remMins}m`;
}

async function populateVisitorRequestProperties() {
  const selector = document.getElementById('visitor-request-property');
  if (!selector) return 0;
  try {
    let options = [];
    if (activeBooking?.property) {
      options = [{ id: activeBooking.property, name: activeBooking.property_name || 'Current Property' }];
    } else {
      const bookings = await api.get('/bookings/my/');
      options = bookings.filter((b) => b.status === 'approved').map((b) => ({ id: b.property, name: b.property_name }));
    }
    selector.innerHTML = '<option value="">Select property...</option>';
    options.forEach((item) => {
      selector.innerHTML += `<option value="${item.id}">${item.name}</option>`;
    });
    if (options.length === 1) selector.value = String(options[0].id);
    return options.length;
  } catch {
    selector.innerHTML = '<option value="">Unable to load properties</option>';
    return 0;
  }
}

async function loadVisitors(silent = false) {
  const requestsEl = document.getElementById('visitor-requests-list');
  const approvedEl = document.getElementById('visitors-approved-list');
  try {
    const [requests, logs] = await Promise.all([
      api.get('/visitors/requests/my/'),
      api.get('/visitors/my/'),
    ]);

    if (!requests.length) {
      requestsEl.innerHTML = '<div class="empty-state"><div class="empty-state-icon">REQ</div><h3>No Visitor Requests</h3><p>Create a request and wait for owner approval.</p></div>';
    } else {
      requestsEl.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>Visitor</th><th>Purpose</th><th>Request Time</th><th>Expected Check-In</th><th>Expected Check-Out</th><th>Duration</th><th>Approval Time</th><th>Status</th></tr></thead>
        <tbody>${requests.map((req) => `
          <tr>
            <td class="font-semibold">${req.visitor_name}<br><span class="text-xs text-muted">${req.visitor_phone || 'No phone'}</span></td>
            <td>${req.purpose_display}</td>
            <td>${formatDateTime(req.created_at)}</td>
            <td>${formatDateTime(req.requested_check_in)}</td>
            <td>${formatDateTime(req.requested_check_out)}</td>
            <td>${calculateVisitDurationLabel(req.requested_check_in, req.requested_check_out)}</td>
            <td>${formatDateTime(req.reviewed_at)}</td>
            <td>${visitorStatusBadge(req.status)}${req.owner_note ? `<div class="text-xs text-muted mt-xs">${req.owner_note}</div>` : ''}</td>
          </tr>`).join('')}
        </tbody></table></div>`;
    }

    if (!logs.length) {
      approvedEl.innerHTML = '<div class="empty-state"><div class="empty-state-icon">OK</div><h3>No Approved Visitors Yet</h3><p>Approved requests will appear here with visit timeline status.</p></div>';
    } else {
      approvedEl.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>Visitor</th><th>Phone</th><th>Purpose</th><th>Check In</th><th>Check Out</th><th>Status</th></tr></thead>
        <tbody>${logs.map((v) => {
          const lifecycle = getVisitLifecycleStatus(v.check_in, v.check_out, v.visit_status);
          return `<tr><td class="font-semibold">${v.visitor_name}</td><td class="text-muted">${v.visitor_phone || '-'}</td>
          <td>${v.purpose_display}</td><td>${formatDateTime(v.check_in)}</td><td>${formatDateTime(v.check_out)}</td><td>${visitLifecycleBadge(lifecycle)}</td></tr>`;
        }).join('')}
        </tbody></table></div>`;
    }

    if (!silent) await populateVisitorRequestProperties();
  } catch {
    requestsEl.innerHTML = '<p class="text-muted text-center py-xl">Failed to load visitor requests.</p>';
    approvedEl.innerHTML = '<p class="text-muted text-center py-xl">Failed to load approved visitor log.</p>';
  }
}

document.getElementById('btn-open-visitor-request')?.addEventListener('click', async () => {
  const propertyCount = await populateVisitorRequestProperties();
  if (!propertyCount) {
    Toast.warning('No active approved booking found. Visitor requests require an approved stay.');
    return;
  }
  const checkInInput = document.getElementById('visitor-request-checkin');
  const checkOutInput = document.getElementById('visitor-request-checkout');
  const nowPlusHour = new Date(Date.now() + 60 * 60 * 1000);
  if (checkInInput && !checkInInput.value) {
    checkInInput.value = toLocalDateTimeInputValue(nowPlusHour);
  }
  if (checkOutInput && !checkOutInput.value) {
    const checkOutDefault = new Date(nowPlusHour.getTime() + 2 * 60 * 60 * 1000);
    checkOutInput.value = toLocalDateTimeInputValue(checkOutDefault);
  }
  openModal('modal-request-visitor');
});

document.getElementById('visitor-request-checkin')?.addEventListener('change', () => {
  const checkInRaw = document.getElementById('visitor-request-checkin').value;
  const checkoutEl = document.getElementById('visitor-request-checkout');
  if (!checkoutEl || !checkInRaw) return;
  const currentCheckout = checkoutEl.value ? new Date(checkoutEl.value) : null;
  const checkInDate = new Date(checkInRaw);
  if (!currentCheckout || currentCheckout <= checkInDate) {
    const suggestedCheckout = new Date(checkInDate.getTime() + 2 * 60 * 60 * 1000);
    checkoutEl.value = toLocalDateTimeInputValue(suggestedCheckout);
  }
});

document.getElementById('visitor-request-form')?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const btn = event.target.querySelector('button[type=submit]');
  const propertyId = Number(document.getElementById('visitor-request-property').value);
  const checkInRaw = document.getElementById('visitor-request-checkin').value;
  const checkOutRaw = document.getElementById('visitor-request-checkout').value;
  if (!propertyId) {
    Toast.warning('Please select a property before submitting.');
    return;
  }
  if (!checkInRaw) {
    Toast.warning('Please choose expected check-in date and time.');
    return;
  }
  if (!checkOutRaw) {
    Toast.warning('Please choose expected check-out date and time.');
    return;
  }
  const checkInDate = new Date(checkInRaw);
  const checkOutDate = new Date(checkOutRaw);
  if (checkOutDate <= checkInDate) {
    Toast.warning('Expected check-out must be later than expected check-in.');
    return;
  }
  btn.disabled = true;
  btn.textContent = 'Submitting...';
  try {
    const checkInIso = checkInDate.toISOString();
    const checkOutIso = checkOutDate.toISOString();
    await api.post('/visitors/requests/my/', {
      property: propertyId,
      visitor_name: document.getElementById('visitor-request-name').value.trim(),
      visitor_phone: document.getElementById('visitor-request-phone').value.trim(),
      purpose: document.getElementById('visitor-request-purpose').value,
      requested_check_in: checkInIso,
      requested_check_out: checkOutIso,
      notes: document.getElementById('visitor-request-note').value.trim(),
    });
    closeModal('modal-request-visitor');
    event.target.reset();
    Toast.success('Visitor request submitted. Waiting for owner approval.');
    await loadVisitors();
  } catch (err) {
    Toast.error(err.message || 'Failed to submit visitor request.');
  } finally {
    btn.disabled = false;
    btn.textContent = 'Submit Request';
  }
});
async function loadBookingFlow() {
    const el = document.getElementById('booking-flow-list');
    if (!el) return;
    try {
      residentBookings = await api.get('/bookings/my/');
      if (!residentBookings.length) {
        el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">🔍</div><h3>No Booking History</h3><p>You have not applied to any PG yet.</p><a href="index.html#explore-section" class="btn btn-primary btn-sm">Explore PGs</a></div>';
        return;
      }
      el.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>#</th><th>Property</th><th>Room</th><th>Applied</th><th>Move In</th><th>Status</th></tr></thead>
        <tbody>${residentBookings.map((booking) => `
          <tr>
            <td>#${booking.id}</td>
            <td class="font-semibold">${booking.property_name}</td>
            <td>${booking.room_number || '—'}</td>
            <td>${formatDate(booking.applied_at)}</td>
            <td>${formatDate(booking.move_in_date)}</td>
            <td>${bookingStatusBadge(booking)}</td>
          </tr>`).join('')}
        </tbody></table></div>`;
    } catch {
      el.innerHTML = '<p class="text-muted text-center py-xl">Could not load booking flow right now.</p>';
    }
  }

  async function loadWishlist() {
    const el = document.getElementById('wishlist-list');
    if (!el) return;
    let savedIds = [];
    try {
      savedIds = JSON.parse(localStorage.getItem('pgdost-wishlist') || '[]')
        .map((id) => Number(id))
        .filter((id) => Number.isFinite(id));
    } catch {
      savedIds = [];
    }
    if (!savedIds.length) {
      el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">♡</div><h3>Wishlist is empty</h3><p>Save properties from the explore page to see them here.</p><a href="index.html#explore-section" class="btn btn-primary btn-sm">Browse Properties</a></div>';
      return;
    }
    try {
      const props = await Promise.all(savedIds.map((id) => api.get(`/properties/${id}/`).catch(() => null)));
      const valid = props.filter(Boolean);
      if (!valid.length) {
        el.innerHTML = '<p class="text-muted text-center py-xl">Saved properties are unavailable right now.</p>';
        return;
      }
      el.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>Property</th><th>Location</th><th>Rating</th><th>Action</th></tr></thead>
        <tbody>${valid.map((property) => `
          <tr>
            <td class="font-semibold">${property.name}</td>
            <td>${property.city}, ${property.state}</td>
            <td>${property.avg_rating ? `★ ${property.avg_rating}` : '—'}</td>
            <td><a href="index.html#explore-section" class="btn btn-secondary btn-sm">Open</a></td>
          </tr>`).join('')}
        </tbody></table></div>`;
    } catch {
      el.innerHTML = '<p class="text-muted text-center py-xl">Failed to load wishlist data.</p>';
    }
  }

  async function loadMyReviews() {
    const el = document.getElementById('my-reviews-list');
    if (!el) return;
    try {
      if (!residentBookings.length) residentBookings = await api.get('/bookings/my/');
      const approvedBookings = residentBookings.filter((booking) => ['approved', 'vacated'].includes(booking.status));
      const propertyIds = [...new Set(approvedBookings.map((booking) => booking.property))];
      if (!propertyIds.length) {
        el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">★</div><h3>No Reviews Yet</h3><p>Your submitted reviews will show here once you review a property.</p></div>';
        return;
      }
      const username = Auth.getUser()?.username;
      const results = await Promise.all(propertyIds.map((propertyId) => api.get(`/properties/${propertyId}/reviews/`).catch(() => [])));
      const myReviews = [];
      results.forEach((reviews, index) => {
        (reviews || []).forEach((review) => {
          if (review.username === username) {
            myReviews.push({ ...review, property_name: approvedBookings.find((b) => b.property === propertyIds[index])?.property_name || 'Property' });
          }
        });
      });
      if (!myReviews.length) {
        el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">★</div><h3>No Reviews Submitted</h3><p>Use the marketplace to submit your first review.</p></div>';
        return;
      }
      el.innerHTML = `<div class="table-wrapper"><table class="table">
        <thead><tr><th>Property</th><th>Rating</th><th>Review</th><th>Date</th></tr></thead>
        <tbody>${myReviews.map((review) => `
          <tr>
            <td class="font-semibold">${review.property_name}</td>
            <td>${'★'.repeat(Number(review.rating || 0)) || '—'}</td>
            <td>${review.review_text || 'No text provided.'}</td>
            <td>${formatDate(review.review_date || review.created_at)}</td>
          </tr>`).join('')}
        </tbody></table></div>`;
    } catch {
      el.innerHTML = '<p class="text-muted text-center py-xl">Failed to load your review history.</p>';
    }
  }

  async function loadResidentProfile() {
    try {
      const profile = await api.get('/auth/profile/');
      document.getElementById('profile-first-name').value = profile.first_name || '';
      document.getElementById('profile-last-name').value = profile.last_name || '';
      document.getElementById('profile-email').value = profile.email || '';
      document.getElementById('profile-phone').value = profile.phone_number || '';
    } catch {
      const errorEl = document.getElementById('profile-save-error');
      if (errorEl) {
        errorEl.textContent = 'Failed to load profile data.';
        errorEl.classList.remove('hidden');
      }
    }
  }

  // ── Notifications ───────────────────────────────────────
  async function loadNotifications() {
      try {
          const notifs = await api.get('/auth/notifications/');
          const unreadCount = notifs.filter(n => !n.is_read).length;
          const badge = document.getElementById('notif-badge');
          if (unreadCount > 0) {
              badge.style.display = 'block';
          } else {
              badge.style.display = 'none';
          }
          
          const list = document.getElementById('notif-list');
          if (notifs.length === 0) {
              list.innerHTML = '<p class="text-sm text-muted text-center py-sm">No notifications.</p>';
          } else {
              list.innerHTML = notifs.map(n => `
                  <div style="padding:10px; border-bottom:1px solid var(--border); ${n.is_read ? 'opacity:0.6;' : 'background:rgba(92,122,74,0.06);'} border-radius:4px; margin-bottom:5px; cursor:pointer;" onclick="markNotifRead(${n.id})">
                      <p style="font-size:0.85rem; margin:0;">${n.message}</p>
                      <span style="font-size:0.7rem; color:var(--text-muted);">${formatDate(n.created_at)}</span>
                  </div>
              `).join('');
          }
      } catch (e) {}
  }

  function toggleNotifications() {
      const el = document.getElementById('notif-dropdown');
      el.style.display = el.style.display === 'block' ? 'none' : 'block';
      if (el.style.display === 'block') loadNotifications();
  }

  document.addEventListener('click', (event) => {
    const panel = document.getElementById('notif-dropdown');
    const trigger = event.target.closest('.topbar-icon-btn');
    const insidePanel = event.target.closest('#notif-dropdown');
    if (!panel) return;
    if (!insidePanel && !trigger) panel.style.display = 'none';
  });

  async function markNotifRead(id) {
      try {
          await api.patch(`/auth/notifications/${id}/`, { is_read: true });
          loadNotifications();
      } catch (e) {}
  }

  // Init
  loadOverview();
  loadNotifications();
  const initialTab = (window.location.hash || '').replace('#', '').trim();
  const validTabs = ['overview', 'payments', 'complaints', 'visitors', 'bookings', 'wishlist', 'reviews', 'profile'];
  if (initialTab && validTabs.includes(initialTab)) switchTab(initialTab);
  window.addEventListener('resize', () => {
    if (window.innerWidth > 900) closeSidebar();
  });
  window.addEventListener('beforeunload', stopVisitorRealtime);
  // Topbar date
  const tdate = document.getElementById('topbar-date');
  if (tdate) tdate.textContent = new Date().toLocaleDateString('en-IN', {weekday:'long', year:'numeric', month:'long', day:'numeric'});

