/** Owner dashboard — payments module */
var ownerInvoicesMap = window.ownerInvoicesMap || {};
window.ownerInvoicesMap = ownerInvoicesMap;
let ownerPayOverview = null;
let ownerPropertiesForPay = [];
let ownerSubmissionsMap = {};
let currentPayPanel = 'overview';
let paymentSettingsPropertyId = null;

function switchPayPanel(panel) {
  currentPayPanel = panel;
  document.querySelectorAll('.pay-subtab').forEach((btn) => {
    btn.classList.toggle('active', btn.dataset.payPanel === panel);
  });
  ['overview', 'settings', 'invoices', 'verifications'].forEach((p) => {
    const el = document.getElementById(`pay-panel-${p}`);
    if (el) el.classList.toggle('hidden', p !== panel);
  });
  if (panel === 'overview') renderPayOverview();
  if (panel === 'settings') renderPaymentSettingsForm();
  if (panel === 'invoices') loadPaymentsTable();
  if (panel === 'verifications') renderVerificationsPanel();
}

async function loadPayments() {
  try {
    const [overview, properties] = await Promise.all([
      api.get('/payments/owner/overview/'),
      api.get('/properties/owner/'),
    ]);
    ownerPayOverview = overview;
    ownerPropertiesForPay = properties.results || properties || [];
    (overview.pending_submissions || []).forEach((s) => { ownerSubmissionsMap[s.id] = s; });
    const badge = document.getElementById('pay-pending-badge');
    if (badge) {
      const n = overview.pending_verifications || 0;
      badge.textContent = n;
      badge.classList.toggle('hidden', n === 0);
    }
    const ap = document.getElementById('attn-payments');
    if (ap) ap.textContent = String(overview.overdue_invoices || 0);
    switchPayPanel(currentPayPanel);
  } catch (e) {
    Toast.error(e.message || 'Failed to load payments.');
  }
}

function renderPayOverview() {
  const el = document.getElementById('pay-panel-overview');
  if (!el || !ownerPayOverview) return;
  const o = ownerPayOverview;
  el.innerHTML = `
    <motion class="pay-stat-grid">
      <div class="pay-stat-card"><div class="pay-stat-label">Pending review</div><div class="pay-stat-value">${o.pending_verifications || 0}</div></div>
      <div class="pay-stat-card"><div class="pay-stat-label">Unpaid invoices</div><div class="pay-stat-value">${o.unpaid_invoices || 0}</div></div>
      <div class="pay-stat-card"><div class="pay-stat-label">Overdue</div><motion class="pay-stat-value">${o.overdue_invoices || 0}</div></div>
      <div class="pay-stat-card"><div class="pay-stat-label">Revenue this month</div><div class="pay-stat-value">${formatCurrency(o.paid_this_month || 0)}</div></div>
    </div>
    <div class="pay-glass-card">
      <h3 class="font-bold mb-md">Unpaid residents</h3>
      ${!(o.unpaid_residents || []).length ? '<p class="text-muted">All residents are up to date.</p>' : `
        <div class="table-wrapper"><table class="table"><thead><tr><th>Resident</th><th>Property</th><th>Amount</th><th>Due</th><th>Status</th></tr></thead>
        <tbody>${o.unpaid_residents.map((r) => `<tr>
          <td>${r.resident_username}</td><td>${r.property_name}</td>
          <td>${formatCurrency(r.amount)}</td><td>${formatDate(r.due_date)}</td>
          <td>${paymentStatusBadge(r.status)}</td>
        </tr>`).join('')}</tbody></table></motion>`}
    </div>
    <div class="pay-glass-card">
      <h3 class="font-bold mb-md">Recent verified payments</h3>
      ${renderSubmissionsMiniList(o.recent_payments || [])}
    </div>`;
  el.innerHTML = el.innerHTML.replace(/<\/?motion[^>]*>/g, '').replace(/<motion /g, '<div ').replace(/<\/motion>/g, '');
  if (window.Cinematic?.rescanReveals) Cinematic.rescanReveals(el);
}

function renderSubmissionsMiniList(items) {
  if (!items.length) return '<p class="text-muted">No verified payments yet.</p>';
  return `<div class="pay-timeline">${items.map((s) => `
    <div class="pay-timeline-item">
      <span class="pay-timeline-dot"></span>
      <div>
        <strong>${s.resident_username}</strong> · ${formatCurrency(s.amount)}
        <div class="text-sm text-muted">${s.submission_type_display} · ${renderPaymentMethodLabel(s.payment_method)} · ${formatDate(s.submitted_at)}</div>
      </div>
      ${paymentStatusBadge(s.status, s.status_display)}
    </div>`).join('')}</div>`;
}

function renderPaymentSettingsForm() {
  const el = document.getElementById('pay-panel-settings');
  if (!el) return;
  if (!ownerPropertiesForPay.length) {
    el.innerHTML = '<div class="empty-state"><p>Add a property first to configure payment settings.</p></div>';
    return;
  }
  if (!paymentSettingsPropertyId) paymentSettingsPropertyId = ownerPropertiesForPay[0].id;
  el.innerHTML = `
    <div class="pay-glass-card">
      <div class="form-group mb-md">
        <label class="form-label">Select property</label>
        <select id="pay-settings-property" class="form-select" onchange="onPaymentSettingsPropertyChange(this.value)">
          ${ownerPropertiesForPay.map((p) => `<option value="${p.id}" ${String(p.id) === String(paymentSettingsPropertyId) ? 'selected' : ''}>${p.name}</option>`).join('')}
        </select>
      </div>
      <form id="payment-settings-form" class="flex flex-col gap-md">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">UPI ID *</label><input id="ps-upi" class="form-input" placeholder="name@upi" required /></div>
          <div class="form-group"><label class="form-label">Account holder name</label><input id="ps-holder" class="form-input" /></div>
        </div>
        <div class="form-group"><label class="form-label">Bank name (optional)</label><input id="ps-bank" class="form-input" /></div>
        <div class="form-group">
          <label class="form-label">QR code image</label>
          <label class="pay-upload-zone"><span id="ps-qr-label">Upload Google Pay / PhonePe QR</span>
            <input type="file" id="ps-qr" accept="image/jpeg,image/png,image/webp" />
          </label>
          <div id="ps-qr-preview" class="mt-sm"></div>
        </div>
        <div class="form-group">
          <label class="form-label">Payment instructions</label>
          <textarea id="ps-instructions" class="form-textarea" rows="3" placeholder="Pay before 5th of each month. Mention room number in UPI note."></textarea>
        </div>
        <div class="pay-apps">
          <span class="pay-app-chip">Google Pay</span><span class="pay-app-chip">PhonePe</span>
          <span class="pay-app-chip">Paytm</span><span class="pay-app-chip">BHIM UPI</span>
        </div>
        <button type="submit" class="btn btn-primary btn-lg w-full">Save payment settings</button>
      </form>
    </div>`;
  document.getElementById('payment-settings-form')?.addEventListener('submit', savePaymentSettings);
  document.getElementById('ps-qr')?.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) document.getElementById('ps-qr-label').textContent = f.name;
  });
  loadPaymentSettingsData(paymentSettingsPropertyId);
}

async function onPaymentSettingsPropertyChange(id) {
  paymentSettingsPropertyId = parseInt(id, 10);
  await loadPaymentSettingsData(paymentSettingsPropertyId);
}

async function loadPaymentSettingsData(propertyId) {
  try {
    const data = await api.get(`/payments/owner/settings/${propertyId}/`);
    document.getElementById('ps-upi').value = data.upi_id || '';
    document.getElementById('ps-holder').value = data.account_holder_name || '';
    document.getElementById('ps-bank').value = data.bank_name || '';
    document.getElementById('ps-instructions').value = data.payment_instructions || '';
    const prev = document.getElementById('ps-qr-preview');
    if (prev && data.qr_code_url) {
      prev.innerHTML = `<img src="${data.qr_code_url}" alt="QR" style="max-width:180px;border-radius:12px;" />`;
    } else if (prev) prev.innerHTML = '';
  } catch {
    ['ps-upi', 'ps-holder', 'ps-bank', 'ps-instructions'].forEach((id) => {
      const node = document.getElementById(id);
      if (node) node.value = '';
    });
  }
}

async function savePaymentSettings(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  btn.disabled = true;
  const fd = new FormData();
  fd.append('upi_id', document.getElementById('ps-upi').value.trim());
  fd.append('account_holder_name', document.getElementById('ps-holder').value.trim());
  fd.append('bank_name', document.getElementById('ps-bank').value.trim());
  fd.append('payment_instructions', document.getElementById('ps-instructions').value.trim());
  const qr = document.getElementById('ps-qr').files?.[0];
  if (qr) fd.append('qr_code', qr);
  try {
    await api.patch(`/payments/owner/settings/${paymentSettingsPropertyId}/`, fd);
    Toast.success('Payment settings saved.');
    await loadPaymentSettingsData(paymentSettingsPropertyId);
  } catch (err) { Toast.error(err.message); }
  finally { btn.disabled = false; }
}

async function loadPaymentsTable() {
  const el = document.getElementById('payments-list');
  if (!el) return;
  el.innerHTML = '<div style="display:flex;justify-content:center;padding:32px;"><div class="spinner"></div></div>';
  try {
    const invoices = await api.get('/payments/owner/');
    invoices.forEach((inv) => { ownerInvoicesMap[inv.id] = inv; });
    if (!invoices.length) {
      el.innerHTML = '<div class="empty-state"><motion class="empty-state-icon">💰</motion><h3>No Invoices</h3><p>Create invoices for your residents.</p></motion>';
      el.innerHTML = el.innerHTML.replace(/<\/?motion[^>]*>/g, '');
      return;
    }
    el.innerHTML = `<div class="table-wrapper"><table class="table">
      <thead><tr><th>#</th><th>Resident</th><th>Period</th><th>Amount</th><th>Due</th><th>Txn</th><th>Status</th><th></th></tr></thead>
      <tbody>${invoices.map((inv) => {
        const total = inv.total_amount != null ? inv.total_amount : inv.amount;
        return `<tr>
          <td>#${inv.id}</td><td class="font-semibold">${inv.resident_username}</td>
          <td>${inv.month_display} ${inv.year}</td>
          <td class="font-bold">${formatCurrency(total)}</td>
          <td>${formatDate(inv.due_date)}</td>
          <td class="text-sm text-muted" style="font-family:monospace;">${inv.transaction_id || '—'}</td>
          <td>${paymentStatusBadge(inv.status, inv.status_display)}</td>
          <td>${inv.status === 'paid'
            ? `<button onclick="showReceipt(${inv.id})" class="btn btn-secondary btn-sm">Receipt</button>`
            : inv.status === 'pending_verification'
              ? '<span class="text-muted text-xs">Awaiting review</span>'
              : '<span class="text-muted text-xs">Unpaid</span>'
          }</td></tr>`;
      }).join('')}</tbody></table></motion>`;
    el.innerHTML = el.innerHTML.replace(/<\/?motion[^>]*>/g, '');
  } catch {
    el.innerHTML = '<p class="text-muted text-center py-xl">Failed to load invoices.</p>';
  }
}

function renderVerificationsPanel() {
  const el = document.getElementById('pay-panel-verifications');
  if (!el) return;
  const pending = ownerPayOverview?.pending_submissions || [];
  if (!pending.length) {
    el.innerHTML = '<div class="empty-state"><div class="empty-state-icon">✓</div><h3>All caught up</h3><p>No payments waiting for verification.</p></div>';
    return;
  }
  pending.forEach((s) => { ownerSubmissionsMap[s.id] = s; });
  el.innerHTML = `<div class="pay-timeline">${pending.map((s) => `
    <div class="pay-timeline-item payment-card">
      <span class="pay-timeline-dot"></span>
      <div>
        <strong>${s.resident_username}</strong> · ${s.property_name}
        <div class="text-sm text-muted">${s.submission_type_display} · ${formatCurrency(s.amount)} · ${s.transaction_id}</div>
        <div class="text-xs text-muted">${formatDate(s.submitted_at)} · ${renderPaymentMethodLabel(s.payment_method)}</motion>
        ${s.invoice_period ? `<div class="text-xs">Rent: ${s.invoice_period}</div>` : ''}
      </div>
      <button class="btn btn-primary btn-sm" onclick="openReviewPayment(${s.id})">Review</button>
    </div>`).join('')}</div>`;
  el.innerHTML = el.innerHTML.replace(/<\/?motion[^>]*>/g, '');
}

function openReviewPayment(id) {
  const s = ownerSubmissionsMap[id];
  if (!s) return;
  document.getElementById('review-submission-id').value = id;
  document.getElementById('review-owner-note').value = '';
  document.getElementById('review-payment-body').innerHTML = `
    <p><strong>${s.resident_username}</strong> submitted ${formatCurrency(s.amount)} for ${s.submission_type_display}</p>
    <p class="text-sm text-muted">Txn: <code>${s.transaction_id}</code></p>
    ${s.screenshot_url ? `<img class="pay-proof-preview" src="${s.screenshot_url}" alt="Proof" />` : ''}`;
  openModal('modal-review-payment');
}

async function approvePaymentSubmission() {
  const id = document.getElementById('review-submission-id').value;
  const note = document.getElementById('review-owner-note').value;
  try {
    await api.post(`/payments/owner/submissions/${id}/approve/`, { owner_note: note });
    closeModal('modal-review-payment');
    Toast.success('Payment approved.');
    await loadPayments();
  } catch (e) { Toast.error(e.message); }
}

async function rejectPaymentSubmission() {
  const id = document.getElementById('review-submission-id').value;
  const note = document.getElementById('review-owner-note').value;
  try {
    await api.post(`/payments/owner/submissions/${id}/reject/`, { owner_note: note });
    closeModal('modal-review-payment');
    Toast.success('Payment rejected.');
    await loadPayments();
  } catch (e) { Toast.error(e.message); }
}

window.switchPayPanel = switchPayPanel;
window.onPaymentSettingsPropertyChange = onPaymentSettingsPropertyChange;
window.openReviewPayment = openReviewPayment;
window.approvePaymentSubmission = approvePaymentSubmission;
window.rejectPaymentSubmission = rejectPaymentSubmission;
