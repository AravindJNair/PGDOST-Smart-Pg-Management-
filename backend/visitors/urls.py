from django.urls import path
from .views import (
    ResidentVisitorLogListView,
    OwnerVisitorLogListCreateView, OwnerVisitorLogDetailView,
    AllVisitorLogsListView
)

urlpatterns = [
    # Resident
    path('my/', ResidentVisitorLogListView.as_view(), name='my-visitor-logs'),
    # Owner
    path('owner/', OwnerVisitorLogListCreateView.as_view(), name='owner-visitor-logs'),
    path('owner/<int:pk>/', OwnerVisitorLogDetailView.as_view(), name='owner-visitor-log-detail'),
    # Superadmin
    path('all/', AllVisitorLogsListView.as_view(), name='all-visitor-logs'),
]
