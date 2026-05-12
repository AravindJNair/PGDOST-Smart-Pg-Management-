from django.urls import path
from .views import (
    ResidentInvoiceListView, ResidentPayInvoiceView,
    OwnerCreateInvoiceView, OwnerInvoiceListView, OwnerInvoiceDetailView,
    AllInvoicesListView
)

urlpatterns = [
    # Resident
    path('my/', ResidentInvoiceListView.as_view(), name='my-invoices'),
    path('my/<int:pk>/pay/', ResidentPayInvoiceView.as_view(), name='pay-invoice'),
    # Owner
    path('owner/create/', OwnerCreateInvoiceView.as_view(), name='create-invoice'),
    path('owner/', OwnerInvoiceListView.as_view(), name='owner-invoices'),
    path('owner/<int:pk>/', OwnerInvoiceDetailView.as_view(), name='owner-invoice-detail'),
    # Superadmin
    path('all/', AllInvoicesListView.as_view(), name='all-invoices'),
]
