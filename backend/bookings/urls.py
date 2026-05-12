from django.urls import path
from .views import (
    ResidentApplyView, ResidentBookingListView, ResidentActiveBookingView,
    OwnerBookingListView, OwnerBookingUpdateView,
    AllBookingsListView
)

urlpatterns = [
    # Resident
    path('apply/', ResidentApplyView.as_view(), name='booking-apply'),
    path('my/', ResidentBookingListView.as_view(), name='my-bookings'),
    path('active/', ResidentActiveBookingView.as_view(), name='active-booking'),
    # Owner
    path('owner/', OwnerBookingListView.as_view(), name='owner-bookings'),
    path('owner/<int:pk>/update/', OwnerBookingUpdateView.as_view(), name='owner-booking-update'),
    # Superadmin
    path('all/', AllBookingsListView.as_view(), name='all-bookings'),
]
