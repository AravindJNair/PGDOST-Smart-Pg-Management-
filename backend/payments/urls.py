from django.urls import path
from .views import (
    ResidentInvoiceListView,
    ResidentPayInvoiceView,
    ResidentPaymentSummaryView,
    ResidentPaymentHistoryView,
    ResidentSubmitRentProofView,
    ResidentSubmitDepositProofView,
    OwnerCreateInvoiceView,
    OwnerInvoiceListView,
    OwnerInvoiceDetailView,
    OwnerPaymentOverviewView,
    OwnerPaymentSettingsView,
    OwnerSubmissionListView,
    OwnerApproveSubmissionView,
    OwnerRejectSubmissionView,
    AllInvoicesListView,
)

urlpatterns = [
    # Resident
    path('my/', ResidentInvoiceListView.as_view(), name='my-invoices'),
    path('my/summary/', ResidentPaymentSummaryView.as_view(), name='my-payment-summary'),
    path('my/history/', ResidentPaymentHistoryView.as_view(), name='my-payment-history'),
    path('my/deposit/submit-proof/', ResidentSubmitDepositProofView.as_view(), name='submit-deposit-proof'),
    path('my/<int:pk>/pay/', ResidentPayInvoiceView.as_view(), name='pay-invoice'),
    path('my/<int:pk>/submit-proof/', ResidentSubmitRentProofView.as_view(), name='submit-rent-proof'),
    # Owner
    path('owner/overview/', OwnerPaymentOverviewView.as_view(), name='owner-payment-overview'),
    path('owner/settings/<int:property_id>/', OwnerPaymentSettingsView.as_view(), name='owner-payment-settings'),
    path('owner/submissions/', OwnerSubmissionListView.as_view(), name='owner-submissions'),
    path('owner/submissions/<int:pk>/approve/', OwnerApproveSubmissionView.as_view(), name='approve-submission'),
    path('owner/submissions/<int:pk>/reject/', OwnerRejectSubmissionView.as_view(), name='reject-submission'),
    path('owner/create/', OwnerCreateInvoiceView.as_view(), name='create-invoice'),
    path('owner/', OwnerInvoiceListView.as_view(), name='owner-invoices'),
    path('owner/<int:pk>/', OwnerInvoiceDetailView.as_view(), name='owner-invoice-detail'),
    # Superadmin
    path('all/', AllInvoicesListView.as_view(), name='all-invoices'),
]
