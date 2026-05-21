from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Notification
from .models import VisitorLog, VisitorRequest
from .serializers import VisitorLogSerializer, VisitorRequestSerializer


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'resident'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


class IsOwnerOrResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['owner', 'resident']


# --- RESIDENT REQUEST FLOW ---

class ResidentVisitorRequestListCreateView(generics.ListCreateAPIView):
    """Resident submits request; sees own request history."""
    permission_classes = [IsResident]
    serializer_class = VisitorRequestSerializer

    def get_queryset(self):
        qs = VisitorRequest.objects.filter(resident=self.request.user).select_related(
            'property', 'resident', 'reviewed_by'
        )
        status_filter = self.request.query_params.get('status')
        if status_filter in {VisitorRequest.STATUS_PENDING, VisitorRequest.STATUS_APPROVED, VisitorRequest.STATUS_REJECTED}:
            qs = qs.filter(status=status_filter)
        return qs

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        req = serializer.save()
        Notification.objects.create(
            user=req.property.owner,
            message=f"New visitor request from {req.resident.username} for {req.property.name}.",
        )


class OwnerVisitorRequestListView(generics.ListAPIView):
    """Owner can review visitor requests for owned properties."""
    permission_classes = [IsOwner]
    serializer_class = VisitorRequestSerializer

    def get_queryset(self):
        qs = VisitorRequest.objects.filter(property__owner=self.request.user).select_related(
            'property', 'resident', 'reviewed_by'
        )
        status_filter = self.request.query_params.get('status')
        if status_filter in {VisitorRequest.STATUS_PENDING, VisitorRequest.STATUS_APPROVED, VisitorRequest.STATUS_REJECTED}:
            qs = qs.filter(status=status_filter)
        search_term = self.request.query_params.get('search', '').strip()
        if search_term:
            qs = qs.filter(
                Q(visitor_name__icontains=search_term)
                | Q(visitor_phone__icontains=search_term)
                | Q(resident__username__icontains=search_term)
                | Q(property__name__icontains=search_term)
            )
        return qs


class OwnerVisitorRequestReviewView(APIView):
    """Owner approves/rejects a visitor request."""
    permission_classes = [IsOwner]

    def patch(self, request, pk):
        req = VisitorRequest.objects.filter(pk=pk, property__owner=request.user).select_related(
            'property', 'resident'
        ).first()
        if not req:
            return Response({'detail': 'Visitor request not found.'}, status=status.HTTP_404_NOT_FOUND)
        if req.status != VisitorRequest.STATUS_PENDING:
            return Response(
                {'detail': 'This request has already been reviewed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        next_status = (request.data.get('status') or '').strip().lower()
        if next_status not in {VisitorRequest.STATUS_APPROVED, VisitorRequest.STATUS_REJECTED}:
            return Response(
                {'detail': 'Status must be either approved or rejected.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        owner_note = (request.data.get('owner_note') or '').strip()
        if not req.requested_check_out:
            return Response(
                {'detail': 'Expected check-out is required before approval.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if req.requested_check_out <= req.requested_check_in:
            return Response(
                {'detail': 'Expected check-out must be later than expected check-in.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        req.status = next_status
        req.owner_note = owner_note
        req.reviewed_by = request.user
        req.reviewed_at = timezone.now()
        req.save(update_fields=['status', 'owner_note', 'reviewed_by', 'reviewed_at', 'updated_at'])

        if next_status == VisitorRequest.STATUS_APPROVED:
            VisitorLog.objects.create(
                property=req.property,
                resident=req.resident,
                visitor_name=req.visitor_name,
                visitor_phone=req.visitor_phone,
                purpose=req.purpose,
                check_in=req.requested_check_in,
                check_out=req.requested_check_out,
                logged_by=request.user,
                notes=req.notes,
            )
            message = (
                f"Visitor request approved: {req.visitor_name} for {req.property.name}."
            )
        else:
            message = (
                f"Visitor request rejected: {req.visitor_name} for {req.property.name}."
            )
        if owner_note:
            message += f" Note: {owner_note}"
        Notification.objects.create(user=req.resident, message=message)

        return Response(
            VisitorRequestSerializer(req, context={'request': request}).data,
            status=status.HTTP_200_OK,
        )


# --- VISITOR LOGS ---

class ResidentVisitorLogListView(generics.ListAPIView):
    """Resident can see approved visitor logs associated with them."""
    permission_classes = [IsResident]
    serializer_class = VisitorLogSerializer

    def get_queryset(self):
        return VisitorLog.objects.filter(resident=self.request.user).select_related('property', 'resident', 'logged_by')


# --- OWNER VIEWS ---

class OwnerVisitorLogListView(generics.ListAPIView):
    """Owner sees approved visitor logs only."""
    permission_classes = [IsOwner]
    serializer_class = VisitorLogSerializer

    def get_queryset(self):
        return VisitorLog.objects.filter(property__owner=self.request.user).select_related(
            'property', 'resident', 'logged_by'
        )


class OwnerVisitorLogDetailView(generics.RetrieveUpdateAPIView):
    """Owner can update a visitor log (e.g., set check_out time)."""
    permission_classes = [IsOwner]
    serializer_class = VisitorLogSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return VisitorLog.objects.filter(property__owner=self.request.user).select_related(
            'property', 'resident', 'logged_by'
        )


# --- SUPERADMIN ---

class AllVisitorLogsListView(generics.ListAPIView):
    """Superadmin sees all visitor logs."""
    permission_classes = [IsSuperAdmin]
    serializer_class = VisitorLogSerializer
    queryset = VisitorLog.objects.all().select_related('property', 'resident', 'logged_by')
