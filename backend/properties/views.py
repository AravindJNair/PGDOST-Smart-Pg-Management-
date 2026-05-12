from rest_framework import generics, permissions, filters, status, pagination
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Min
from .models import Property, Room, PropertyImage, Review, Inquiry
from .serializers import PropertySerializer, PropertyListSerializer, RoomSerializer, PropertyImageSerializer, ReviewSerializer, InquirySerializer
from bookings.models import Booking


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


# --- PUBLIC MARKETPLACE ---

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class PublicPropertyListView(generics.ListAPIView):
    """Public-facing marketplace: returns only approved properties with optional search."""
    permission_classes = [permissions.AllowAny]
    serializer_class = PropertyListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['name', 'city', 'state', 'address']
    ordering_fields = ['created_at'] # We will add custom ordering for price below
    filterset_fields = ['city', 'has_wifi', 'has_ac', 'has_food', 'has_parking', 'property_type']

    def get_queryset(self):
        qs = Property.objects.filter(is_approved=True).annotate(min_rent_value=Min('rooms__rent_per_month'))
        
        # Price range filter
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            qs = qs.filter(min_rent_value__gte=min_price)
        if max_price:
            qs = qs.filter(min_rent_value__lte=max_price)
            
        # Custom ordering by price
        ordering = self.request.query_params.get('ordering')
        if ordering == 'price_low_high':
            qs = qs.order_by('min_rent_value')
        elif ordering == 'price_high_low':
            qs = qs.order_by('-min_rent_value')

        return qs

    def get_serializer_context(self):
        return {'request': self.request}


class PublicPropertyDetailView(generics.RetrieveAPIView):
    """Public detail view of an approved property (with rooms)."""
    permission_classes = [permissions.AllowAny]
    serializer_class = PropertySerializer
    queryset = Property.objects.filter(is_approved=True)

    def get_serializer_context(self):
        return {'request': self.request}


class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(property_id=self.kwargs['property_pk'])

    def perform_create(self, serializer):
        prop_id = self.kwargs['property_pk']
        # Check if user has an approved booking for this property
        has_booking = Booking.objects.filter(
            property_id=prop_id,
            resident=self.request.user,
            status='approved'
        ).exists()
        
        if not has_booking:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You can only review a property you have booked.")
            
        serializer.save(user=self.request.user, property_id=prop_id)


class InquiryCreateView(generics.CreateAPIView):
    serializer_class = InquirySerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        prop_id = self.kwargs['property_pk']
        inquiry = serializer.save(property_id=prop_id)
        
        # Optional: Send email
        from django.core.mail import send_mail
        from django.conf import settings
        
        try:
            prop = Property.objects.get(pk=prop_id)
            if prop.email:
                send_mail(
                    subject=f"New Inquiry for {prop.name}",
                    message=f"Name: {inquiry.sender_name}\nEmail: {inquiry.sender_email}\nPhone: {inquiry.sender_phone}\n\nMessage:\n{inquiry.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@pgdost.com',
                    recipient_list=[prop.email],
                    fail_silently=True,
                )
        except Exception:
            pass


# --- OWNER VIEWS ---

class OwnerPropertyListCreateView(generics.ListCreateAPIView):
    """Owner lists and creates their properties."""
    permission_classes = [IsOwner]
    serializer_class = PropertySerializer

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class OwnerPropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner retrieves, updates, or deletes a specific property."""
    permission_classes = [IsOwner]
    serializer_class = PropertySerializer

    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class OwnerInquiryListView(generics.ListAPIView):
    """Owner views inquiries for their properties."""
    permission_classes = [IsOwner]
    serializer_class = InquirySerializer

    def get_queryset(self):
        return Inquiry.objects.filter(property__owner=self.request.user)


class OwnerRoomListCreateView(generics.ListCreateAPIView):
    """Owner manages rooms for a specific property."""
    permission_classes = [IsOwner]
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(
            property__owner=self.request.user,
            property=self.kwargs['property_pk']
        )

    def perform_create(self, serializer):
        prop = Property.objects.get(pk=self.kwargs['property_pk'], owner=self.request.user)
        serializer.save(property=prop)


class OwnerRoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner manages a single room."""
    permission_classes = [IsOwner]
    serializer_class = RoomSerializer

    def get_queryset(self):
        return Room.objects.filter(property__owner=self.request.user)


# --- IMAGE UPLOAD VIEWS ---

class OwnerPropertyImageUploadView(APIView):
    """Owner uploads photos for a specific property."""
    permission_classes = [IsOwner]

    def get(self, request, property_pk):
        """List all images for a property."""
        try:
            prop = Property.objects.get(pk=property_pk, owner=request.user)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)
        images = prop.images.all()
        serializer = PropertyImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, property_pk):
        """Upload a new image for a property."""
        try:
            prop = Property.objects.get(pk=property_pk, owner=request.user)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Limit to 10 images per property
        if prop.images.count() >= 10:
            return Response(
                {'detail': 'Maximum 10 images allowed per property.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PropertyImageSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # If no images exist yet, make this primary automatically
            is_primary = not prop.images.exists()
            serializer.save(property=prop, is_primary=is_primary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerPropertyImageDetailView(APIView):
    """Owner manages a single property image."""
    permission_classes = [IsOwner]

    def patch(self, request, property_pk, image_pk):
        """Update image (e.g. set as primary or update caption)."""
        try:
            image = PropertyImage.objects.get(
                pk=image_pk, property__pk=property_pk, property__owner=request.user
            )
        except PropertyImage.DoesNotExist:
            return Response({'detail': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PropertyImageSerializer(image, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, property_pk, image_pk):
        """Delete an image."""
        try:
            image = PropertyImage.objects.get(
                pk=image_pk, property__pk=property_pk, property__owner=request.user
            )
        except PropertyImage.DoesNotExist:
            return Response({'detail': 'Image not found.'}, status=status.HTTP_404_NOT_FOUND)
        image.image.delete(save=False)  # Delete the actual file
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# --- SUPERADMIN VIEWS ---

class AdminPropertyListView(generics.ListAPIView):
    """Superadmin sees all properties regardless of approval status."""
    permission_classes = [IsSuperAdmin]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}


class AdminPropertyApproveView(generics.UpdateAPIView):
    """Superadmin approves/rejects a property listing."""
    permission_classes = [IsSuperAdmin]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()
    http_method_names = ['patch']

    def perform_update(self, serializer):
        is_approved = self.request.data.get('is_approved')
        if is_approved is True or is_approved == 'true':
            serializer.save(is_approved=True, approved_at=timezone.now())
        else:
            serializer.save(is_approved=False, approved_at=None)

class AdminPropertyDetailView(generics.RetrieveDestroyAPIView):
    """Superadmin views or deletes a property."""
    permission_classes = [IsSuperAdmin]
    serializer_class = PropertySerializer
    queryset = Property.objects.all()

    def get_serializer_context(self):
        return {'request': self.request}
