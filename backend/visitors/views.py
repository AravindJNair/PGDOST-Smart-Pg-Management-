from rest_framework import generics, permissions
from .models import VisitorLog
from .serializers import VisitorLogSerializer


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


# --- RESIDENT VIEWS ---

class ResidentVisitorLogListView(generics.ListAPIView):
    """Resident can see visitor logs associated with them."""
    permission_classes = [IsResident]
    serializer_class = VisitorLogSerializer

    def get_queryset(self):
        return VisitorLog.objects.filter(resident=self.request.user)


# --- OWNER VIEWS ---

class OwnerVisitorLogListCreateView(generics.ListCreateAPIView):
    """Owner can list and log visitors for their properties."""
    permission_classes = [IsOwner]
    serializer_class = VisitorLogSerializer

    def get_queryset(self):
        return VisitorLog.objects.filter(property__owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class OwnerVisitorLogDetailView(generics.RetrieveUpdateAPIView):
    """Owner can update a visitor log (e.g., set check_out time)."""
    permission_classes = [IsOwner]
    serializer_class = VisitorLogSerializer
    http_method_names = ['get', 'patch']

    def get_queryset(self):
        return VisitorLog.objects.filter(property__owner=self.request.user)


# --- SUPERADMIN ---

class AllVisitorLogsListView(generics.ListAPIView):
    """Superadmin sees all visitor logs."""
    permission_classes = [IsSuperAdmin]
    serializer_class = VisitorLogSerializer
    queryset = VisitorLog.objects.all()
