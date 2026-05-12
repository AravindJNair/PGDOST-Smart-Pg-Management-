from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Invoice
from .serializers import InvoiceSerializer, InvoiceCreateSerializer, InvoicePaySerializer


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

class ResidentInvoiceListView(generics.ListAPIView):
    """Resident views all their invoices."""
    permission_classes = [IsResident]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(resident=self.request.user)


class ResidentPayInvoiceView(APIView):
    """Resident marks an invoice as paid by providing a transaction ID."""
    permission_classes = [IsResident]

    def patch(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk, resident=request.user)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.status == 'paid':
            return Response({'detail': 'This invoice is already paid.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = InvoicePaySerializer(invoice, data=request.data, partial=True)
        if serializer.is_valid():
            invoice.status = 'paid'
            invoice.payment_date = timezone.now()
            invoice.transaction_id = serializer.validated_data.get('transaction_id', '')
            invoice.save()
            return Response(InvoiceSerializer(invoice).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- OWNER VIEWS ---

class OwnerCreateInvoiceView(generics.CreateAPIView):
    """Owner creates an invoice for a resident."""
    permission_classes = [IsOwner]
    serializer_class = InvoiceCreateSerializer

    def perform_create(self, serializer):
        # Ensure the property belongs to this owner
        prop = serializer.validated_data['property']
        if prop.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only create invoices for your own properties.")
        serializer.save()


class OwnerInvoiceListView(generics.ListAPIView):
    """Owner views all invoices for their properties."""
    permission_classes = [IsOwner]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(property__owner=self.request.user)


class OwnerInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Owner can retrieve/update/delete specific invoices."""
    permission_classes = [IsOwner]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(property__owner=self.request.user)


# --- SUPERADMIN VIEWS ---

class AllInvoicesListView(generics.ListAPIView):
    """Superadmin sees all invoices."""
    permission_classes = [IsSuperAdmin]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all()
