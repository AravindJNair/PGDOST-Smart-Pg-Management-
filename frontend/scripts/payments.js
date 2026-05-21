/**
 * PGDOST — Shared payment UI helpers
 */

const PAYMENT_METHODS = [
  { value: 'upi', label: 'UPI' },
  { value: 'gpay', label: 'Google Pay' },
  { value: 'phonepe', label: 'PhonePe' },
  { value: 'paytm', label: 'Paytm' },
  { value: 'bhim', label: 'BHIM UPI' },
  { value: 'bank_transfer', label: 'Bank Transfer' },
  { value: 'other', label: 'Other' },
];

function paymentStatusBadge(status, labelOverride) {
  const map = {
    paid: ['pay-status-paid', 'Paid'],
    approved: ['pay-status-paid', 'Paid'],
    unpaid: ['pay-status-pending', 'Unpaid'],
    pending_verification: ['pay-status-review', 'Under Review'],
    pending: ['pay-status-pending', 'Pending'],
    failed: ['pay-status-failed', 'Failed'],
    rejected: ['pay-status-failed', 'Rejected'],
  };
  const [cls, defaultLabel] = map[status] || ['pay-status-pending', status || '—'];
  const label = labelOverride || defaultLabel;
  return `<span class="pay-status ${cls}">${label}</span>`;
}

function paymentMethodOptions(selected = 'upi') {
  return PAYMENT_METHODS.map(
    (m) => `<option value="${m.value}" ${m.value === selected ? 'selected' : ''}>${m.label}</option>`
  ).join('');
}

function renderPaymentMethodLabel(value) {
  const found = PAYMENT_METHODS.find((m) => m.value === value);
  return found ? found.label : value || 'UPI';
}

async function copyUpiId(upiId, btn) {
  if (!upiId) {
    Toast.warning('No UPI ID configured.');
    return;
  }
  try {
    await navigator.clipboard.writeText(upiId);
    if (btn) {
      const prev = btn.textContent;
      btn.textContent = 'Copied!';
      setTimeout(() => { btn.textContent = prev; }, 1600);
    }
    Toast.success('UPI ID copied to clipboard.');
  } catch {
    Toast.info(`UPI ID: ${upiId}`);
  }
}

function buildProofFormData({ transactionId, paymentMethod, screenshot, amount }) {
  const fd = new FormData();
  fd.append('transaction_id', transactionId);
  fd.append('payment_method', paymentMethod || 'upi');
  if (screenshot) fd.append('screenshot', screenshot);
  if (amount != null && amount !== '') fd.append('amount', String(amount));
  return fd;
}

window.PAYMENT_METHODS = PAYMENT_METHODS;
window.paymentStatusBadge = paymentStatusBadge;
window.paymentMethodOptions = paymentMethodOptions;
window.renderPaymentMethodLabel = renderPaymentMethodLabel;
window.copyUpiId = copyUpiId;
window.buildProofFormData = buildProofFormData;
