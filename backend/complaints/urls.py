from django.urls import path
from .views import (
    ResidentTicketListCreateView, ResidentTicketDetailView,
    OwnerTicketListView, OwnerTicketStatusUpdateView,
    TicketReplyCreateView,
    AllTicketsListView
)

urlpatterns = [
    # Resident
    path('my/', ResidentTicketListCreateView.as_view(), name='my-tickets'),
    path('my/<int:pk>/', ResidentTicketDetailView.as_view(), name='my-ticket-detail'),
    # Owner
    path('owner/', OwnerTicketListView.as_view(), name='owner-tickets'),
    path('owner/<int:pk>/status/', OwnerTicketStatusUpdateView.as_view(), name='owner-ticket-status'),
    # Replies (shared)
    path('<int:ticket_pk>/replies/', TicketReplyCreateView.as_view(), name='ticket-reply'),
    # Superadmin
    path('all/', AllTicketsListView.as_view(), name='all-tickets'),
]
