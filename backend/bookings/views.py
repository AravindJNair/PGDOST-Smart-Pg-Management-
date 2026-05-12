from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer
from properties.models import Room


class IsOwner(permissions.BasePermission):
    """Grants access only to users with role='owner'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsResident(permissions.BasePermission):
    """Grants access only to users with role='resident'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'resident'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


# --- RESIDENT VIEWS ---

class ResidentApplyView(generics.CreateAPIView):
    """Resident applies for a PG (creates a pending booking)."""
    permission_classes = [IsResident]
    serializer_class = BookingCreateSerializer

    def get_serializer_context(self):
        return {'request': self.request}


class ResidentBookingListView(generics.ListAPIView):
    """Resident views their own bookings."""
    permission_classes = [IsResident]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(resident=self.request.user)


class ResidentActiveBookingView(APIView):
    """Returns the single active (approved) booking for a resident, or 404."""
    permission_classes = [IsResident]

    def get(self, request):
        booking = Booking.objects.filter(
            resident=request.user, status='approved'
        ).order_by('-id').first()
        if not booking:
            return Response({'detail': 'No active booking found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)


# --- OWNER VIEWS ---

class OwnerBookingListView(generics.ListAPIView):
    """Owner sees all bookings for their properties."""
    permission_classes = [IsOwner]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(property__owner=self.request.user)


class OwnerBookingUpdateView(generics.UpdateAPIView):
    """Owner approves/rejects a booking."""
    permission_classes = [IsOwner]
    serializer_class = BookingStatusUpdateSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return Booking.objects.filter(property__owner=self.request.user)

    def perform_update(self, serializer):
        booking = serializer.save()
        # When approved: decrement available beds in the assigned room
        if booking.status == 'approved' and booking.room:
            room = booking.room
            if room.available_beds > 0:
                room.available_beds -= 1
                room.save()
        # When vacated: restore a bed
        elif booking.status == 'vacated' and booking.room:
            room = booking.room
            room.available_beds = min(room.available_beds + 1, room.total_beds)
            room.save()
            
        # Create notification for resident
        from accounts.models import Notification
        message = f"Your booking for {booking.property.name} is now {booking.get_status_display()}."
        if booking.owner_note:
            message += f" Note: {booking.owner_note}"
        Notification.objects.create(user=booking.resident, message=message)


# --- SUPERADMIN VIEWS ---

class AllBookingsListView(generics.ListAPIView):
    """Superadmin sees every booking in the system."""
    permission_classes = [IsSuperAdmin]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()
