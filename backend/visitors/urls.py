from django.urls import path
from .views import (
    ResidentVisitorRequestListCreateView,
    OwnerVisitorRequestListView,
    OwnerVisitorRequestReviewView,
    ResidentVisitorLogListView,
    OwnerVisitorLogListView, OwnerVisitorLogDetailView,
    AllVisitorLogsListView
)

urlpatterns = [
    # Resident logs + request workflow
    path('my/', ResidentVisitorLogListView.as_view(), name='my-visitor-logs'),
    path('requests/my/', ResidentVisitorRequestListCreateView.as_view(), name='resident-visitor-requests'),
    # Owner logs + request approval workflow
    path('owner/', OwnerVisitorLogListView.as_view(), name='owner-visitor-logs'),
    path('owner/<int:pk>/', OwnerVisitorLogDetailView.as_view(), name='owner-visitor-log-detail'),
    path('requests/owner/', OwnerVisitorRequestListView.as_view(), name='owner-visitor-requests'),
    path('requests/owner/<int:pk>/review/', OwnerVisitorRequestReviewView.as_view(), name='owner-visitor-request-review'),
    # Superadmin
    path('all/', AllVisitorLogsListView.as_view(), name='all-visitor-logs'),
]
