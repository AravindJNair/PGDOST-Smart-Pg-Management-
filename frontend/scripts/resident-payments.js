/** Resident dashboard — payments module */
var residentInvoicesMap = window.residentInvoicesMap || {};
window.residentInvoicesMap = residentInvoicesMap;
let residentPaySummary = null;
let residentPaymentHistory = [];

function initResidentPaymentModals() {
  const payMethod = document.getElementById('pay-method');
  const depMethod = document.getElementById('deposit-method');
  if (payMethod) payMethod.innerHTML = paymentMethodOptions();
  if (depMethod) depMethod.innerHTML = paymentMethodOptions();
  document.getElementById('pay-screenshot')?.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) document.getElementById('pay-screenshot-label').textContent = f.name;
  });
  document.getElementById('deposit-screenshot')?.addEventListener('change', (e) => {
    const f = e.target.files?.[0];
    if (f) document.getElementById('deposit-screenshot-label').textContent = f.name;
  });
}

async function loadResidentPayments() {
  const root = document.getElementById('resident-payments-root');
  if (!root) return;
  root.innerHTML = '<div style="display:flex;justify-content:center;padding:48px;"><div class="spinner"></div></div>';
  try {
    const [summary, invoices, history] = await Promise.all([
      api.get('/payments/my/summary/'),
      api.get('/payments/my/'),
      api.get('/payments/my/history/'),
    ]);
    residentPaySummary = summary;
    residentPaymentHistory = history;
    invoices.forEach((inv) => { residentInvoicesMap[inv.id] = inv; });
    renderResidentPaymentsUI();
    await loadStats();
  } catch (e) {
    root.innerHTML = `<p class="text-muted text-center py-xl">${e.message || 'Failed to load payments.'}</p>`;
  }
}

function renderResidentPaymentsUI() {
  const root = document.getElementById('resident-payments-root');
  if (!root) return;
  const s = residentPaySummary;
  if (!s?.has_active_stay) {
    root.innerHTML = '<div class="empty-state"><div class="empty-state-icon">💳</div><h3>No active stay</h3><p>Book and get approved at a PG to view payment options.</p></div>';
    return;
  }
  const settings = s.payment_settings;
  const rent = s.rent_summary || {};
  const dep = s.deposit || {};
  const depRequired = parseFloat(dep.total_required || 0);
  const depPaid = parseFloat(dep.amount_paid || 0);
  const depPct = depRequired > 0 ? Math.min(100, Math.round((depPaid / depRequired) * 100)) : 0;

  root.innerHTML = `
    <div class="pay-glass-card payment-card">
      <h3 class="font-bold mb-md">Rent summary — ${s.property?.name || ''}</h3>
      <div class="pay-summary-grid">
        <div class="pay-summary-item"><span>Current month rent</span><strong>${formatCurrency(rent.current_month_rent || 0)}</strong></div>
        <div class="pay-summary-item"><span>Due amount</span><strong>${formatCurrency(rent.due_amount || 0)}</strong></div>
        <div class="pay-summary-item"><span>Due date</span><strong>${rent.due_date ? formatDate(rent.due_date) : '—'}</strong></div>
        <div class="pay-summary-item"><span>Maintenance</span><strong>${formatCurrency(rent.maintenance_charges || 0)}</strong></div>
        <div class="pay-summary-item"><span>Food charges</span><strong>${formatCurrency(rent.food_charges || 0)}</strong></div>
        <div class="pay-summary-item"><span>Total paid</span><strong>${formatCurrency(rent.total_paid_amount || 0)}</strong></div>
      </div>
      ${rent.current_invoice_id && rent.current_invoice_status !== 'paid' && rent.current_invoice_status !== 'pending_verification'
        ? `<button class="btn btn-success mt-md" onclick="openPayModal(${rent.current_invoice_id})">Pay rent & submit proof</button>`
        : rent.current_invoice_status === 'pending_verification'
          ? '<p class="text-muted mt-md">Your payment is under owner review.</p>'
          : ''}
    </div>

    <div class="pay-glass-card payment-card">
      <h3 class="font-bold mb-sm">Scan &amp; pay</h3>
      <p class="text-muted text-sm mb-md">Pay via UPI using the owner details below, then submit proof.</p>
      ${settings?.qr_code_url ? `<div class="pay-qr-wrap"><img src="${settings.qr_code_url}" alt="Payment QR" /></div>` : '<p class="text-muted text-sm">Owner has not uploaded a QR code yet.</p>'}
      <div class="pay-upi-row mt-md">
        <span class="pay-upi-id">${settings?.upi_id || 'UPI not configured'}</span>
        ${settings?.upi_id ? `<button type="button" class="btn btn-secondary btn-sm" data-upi-copy="${settings.upi_id.replace(/"/g, '&quot;')}">Copy UPI</button>` : ''}
      </div>
      ${settings?.account_holder_name ? `<p class="text-sm text-muted mt-sm">${settings.account_holder_name}${settings.bank_name ? ' · ' + settings.bank_name : ''}</p>` : ''}
      <div class="pay-apps mt-sm">
        <span class="pay-app-chip">Google Pay</span><span class="pay-app-chip">PhonePe</span>
        <span class="pay-app-chip">Paytm</span><span class="pay-app-chip">BHIM UPI</span>
      </div>
      ${settings?.payment_instructions ? `<p class="text-sm mt-md" style="white-space:pre-wrap;">${settings.payment_instructions}</p>` : ''}
    </div>

    <div class="pay-glass-card payment-card">
      <h3 class="font-bold mb-md">Security deposit</h3>
      <div class="pay-summary-grid">
        <div class="pay-summary-item"><span>Required</span><strong>${formatCurrency(depRequired)}</strong></div>
        <div class="pay-summary-item"><span>Paid</span><strong>${formatCurrency(depPaid)}</strong></div>
        <div class="pay-summary-item"><span>Pending</span><strong>${formatCurrency(dep.pending_amount || 0)}</strong></div>
        <div class="pay-summary-item"><span>Refundable</span><strong>${formatCurrency(dep.refundable_amount || 0)}</strong></div>
      </div>
      <div class="pay-deposit-bar"><div class="pay-deposit-bar-fill" style="width:${depPct}%"></div></div>
      <p class="text-xs text-muted">${depPct}% of deposit paid</p>
      <button type="button" class="btn btn-secondary btn-sm mt-md" onclick="openDepositPayModal()">Submit deposit payment</button>
    </div>

    <div class="pay-glass-card payment-card">
      <h3 class="font-bold mb-md">Payment history</h3>
      ${renderResidentHistory()}
    </div>

    <div class="pay-glass-card payment-card">
      <h3 class="font-bold mb-md">Invoices</h3>
      <div id="resident-invoices-embed"></div>
    </div>`;

  root.querySelector('[data-upi-copy]')?.addEventListener('click', function () {
    copyUpiId(this.getAttribute('data-upi-copy'), this);
  });
  renderResidentInvoicesTable();
  if (window.Cinematic?.rescanReveals) Cinematic.rescanReveals(root);
}

function renderResidentHistory() {
  const items = residentPaymentHistory;
  if (!items.length) return '<p class="text-muted">No payment submissions yet.</p>';
  return `<div class="pay-timeline">${items.map((h) => `
    <div class="pay-timeline-item">
      <span class="pay-timeline-dot"></span>
      <div>
        <strong>${h.submission_type_display}</strong> · ${formatCurrency(h.amount)}
        <div class="text-sm text-muted">${formatDate(h.submitted_at)} · ${renderPaymentMethodLabel(h.payment_method)} · ${h.transaction_id}</div>
        ${h.invoice_period ? `<div class="text-xs">Period: ${h.invoice_period}</div>` : ''}
      </div>
      ${paymentStatusBadge(h.status === 'approved' ? 'paid' : h.status, h.status_display)}
    </div>`).join('')}</div>`;
}

function renderResidentInvoicesTable() {
  const el = document.getElementById('resident-invoices-embed');
  if (!el) return;
  const invoices = Object.values(residentInvoicesMap);
  if (!invoices.length) {
    el.innerHTML = '<p class="text-muted">No invoices yet.</p>';
    return;
  }
  el.innerHTML = `<div class="table-wrapper"><table class="table">
    <thead><tr><th>Period</th><th>Amount</th><th>Due</th><th>Status</th><th></th></tr></thead>
    <tbody>${invoices.map((inv) => {
      const total = inv.total_amount != null ? inv.total_amount : inv.amount;
      const canPay = ['unpaid', 'rejected'].includes(inv.status);
      return `<tr>
        <td>${inv.month_display} ${inv.year}</td>
        <td class="font-bold">${formatCurrency(total)}</td>
        <td>${formatDate(inv.due_date)}</td>
        <td>${paymentStatusBadge(inv.status, inv.status_display)}</td>
        <td>${canPay
          ? `<button onclick="openPayModal(${inv.id})" class="btn btn-success btn-sm">Pay</button>`
          : inv.status === 'paid'
            ? `<button onclick="showReceipt(${inv.id})" class="btn btn-secondary btn-sm">Receipt</button>`
            : inv.status === 'pending_verification' ? '<span class="text-xs text-muted">Review</span>' : '—'
        }</td></tr>`;
    }).join('')}</tbody></table></div>`;
}

function openPayModal(invoiceId) {
  const inv = residentInvoicesMap[invoiceId];
  document.getElementById('pay-invoice-id').value = invoiceId;
  document.getElementById('pay-txn').value = '';
  document.getElementById('pay-screenshot').value = '';
  document.getElementById('pay-screenshot-label').textContent = 'Tap to upload screenshot (JPG/PNG)';
  const amt = document.getElementById('pay-amount');
  if (amt && inv) amt.value = inv.total_amount != null ? inv.total_amount : inv.amount;
  openModal('modal-pay');
}

function openDepositPayModal() {
  const dep = residentPaySummary?.deposit;
  const pending = parseFloat(dep?.pending_amount || dep?.total_required || 0);
  document.getElementById('deposit-amount').value = pending > 0 ? pending : '';
  document.getElementById('deposit-txn').value = '';
  document.getElementById('deposit-screenshot').value = '';
  document.getElementById('deposit-screenshot-label').textContent = 'Tap to upload screenshot';
  openModal('modal-pay-deposit');
}

async function submitRentProof(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  btn.disabled = true;
  btn.textContent = 'Submitting…';
  const id = document.getElementById('pay-invoice-id').value;
  const fd = buildProofFormData({
    transactionId: document.getElementById('pay-txn').value.trim(),
    paymentMethod: document.getElementById('pay-method').value,
    screenshot: document.getElementById('pay-screenshot').files[0],
    amount: document.getElementById('pay-amount').value,
  });
  try {
    const res = await api.post(`/payments/my/${id}/submit-proof/`, fd);
    closeModal('modal-pay');
    Toast.success('Payment proof submitted. Awaiting owner verification.');
    if (res.invoice) residentInvoicesMap[res.invoice.id] = res.invoice;
    await loadResidentPayments();
    refreshPremiumOverview?.();
  } catch (err) { Toast.error(err.message); }
  finally { btn.disabled = false; btn.textContent = 'Submit for Verification'; }
}

async function submitDepositProof(e) {
  e.preventDefault();
  const btn = e.target.querySelector('button[type=submit]');
  btn.disabled = true;
  const fd = buildProofFormData({
    transactionId: document.getElementById('deposit-txn').value.trim(),
    paymentMethod: document.getElementById('deposit-method').value,
    screenshot: document.getElementById('deposit-screenshot').files[0],
    amount: document.getElementById('deposit-amount').value,
  });
  try {
    await api.post('/payments/my/deposit/submit-proof/', fd);
    closeModal('modal-pay-deposit');
    Toast.success('Deposit proof submitted for verification.');
    await loadResidentPayments();
  } catch (err) { Toast.error(err.message); }
  finally { btn.disabled = false; }
}

window.loadInvoices = loadResidentPayments;
window.openPayModal = openPayModal;
window.openDepositPayModal = openDepositPayModal;

function bootResidentPayments() {
  initResidentPaymentModals();
  const payForm = document.getElementById('pay-form');
  const depForm = document.getElementById('deposit-pay-form');
  if (payForm && !payForm.dataset.bound) {
    payForm.dataset.bound = '1';
    payForm.addEventListener('submit', submitRentProof);
  }
  if (depForm && !depForm.dataset.bound) {
    depForm.dataset.bound = '1';
    depForm.addEventListener('submit', submitDepositProof);
  }
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', bootResidentPayments);
} else {
  bootResidentPayments();
}
