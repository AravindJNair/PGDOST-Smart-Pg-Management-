from rest_framework import generics, permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingStatusUpdateSerializer


class IsOwner(permissions.BasePermission):
    """Grants access only to users with role='owner'."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsResident(permissions.BasePermission):
    """Grants access only to users with role='resident'."""
    message = 'Only residents can submit booking requests. Please sign in with a resident account.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None) == 'resident'
        )


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


# --- RESIDENT VIEWS ---

class ResidentApplyView(generics.CreateAPIView):
    """Resident applies for a PG (creates a pending booking)."""
    permission_classes = [IsResident]
    serializer_class = BookingCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        output = BookingSerializer(booking, context={'request': request})
        return Response(output.data, status=status.HTTP_201_CREATED)


class ResidentBookingListView(generics.ListAPIView):
    """Resident views their own bookings."""
    permission_classes = [IsResident]
    serializer_class = BookingSerializer

    def get_queryset(self):
        return Booking.objects.filter(resident=self.request.user).select_related(
            'property', 'room', 'resident'
        ).prefetch_related('documents')


class ResidentActiveBookingView(APIView):
    """Returns the single active (approved) booking for a resident, or 404."""
    permission_classes = [IsResident]

    def get(self, request):
        booking = Booking.objects.filter(
            resident=request.user, status='approved'
        ).prefetch_related('documents').order_by('-id').first()
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
        return Booking.objects.filter(property__owner=self.request.user).select_related(
            'property', 'room', 'resident'
        ).prefetch_related('documents')


class OwnerBookingUpdateView(generics.UpdateAPIView):
    """Owner approves/rejects a booking."""
    permission_classes = [IsOwner]
    serializer_class = BookingStatusUpdateSerializer
    http_method_names = ['patch']

    def get_queryset(self):
        return Booking.objects.filter(property__owner=self.request.user).select_related('property', 'room', 'resident')

    def perform_update(self, serializer):
        previous_status = serializer.instance.status
        previous_room = serializer.instance.room
        next_status = serializer.validated_data.get('status', previous_status)
        next_room = serializer.validated_data.get('room', previous_room)

        if next_status == 'approved' and previous_status != 'approved' and next_room and next_room.available_beds <= 0:
            raise ValidationError({'room': 'Selected room has no available beds.'})

        booking = serializer.save()
        # Guard status transitions so repeated PATCH calls do not drift bed counts.
        if booking.status == 'approved' and previous_status != 'approved' and booking.room:
            room = booking.room
            room.available_beds -= 1
            room.save(update_fields=['available_beds'])
        elif booking.status == 'vacated' and previous_status == 'approved':
            room = previous_room or booking.room
            if room:
                room.available_beds += 1
                room.save(update_fields=['available_beds'])
            
        # Create notification for resident
        from accounts.models import Notification
        message = f"Your booking for {booking.property.name} is now {booking.get_resident_status_display()}."
        if booking.owner_note:
            message += f" Note: {booking.owner_note}"
        Notification.objects.create(user=booking.resident, message=message)


# --- SUPERADMIN VIEWS ---

class AllBookingsListView(generics.ListAPIView):
    """Superadmin sees every booking in the system."""
    permission_classes = [IsSuperAdmin]
    serializer_class = BookingSerializer
    queryset = Booking.objects.all().select_related('property', 'room', 'resident').prefetch_related('documents')
