from decimal import Decimal
from django.db.models import Sum, Q, Count
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking
from properties.models import Property
from .models import Invoice, PaymentSubmission, PropertyPaymentSettings
from .serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    PropertyPaymentSettingsSerializer,
    PaymentSubmissionSerializer,
    PaymentProofSubmitSerializer,
    DepositProofSubmitSerializer,
    PaymentReviewSerializer,
    build_resident_payment_summary,
    get_active_booking,
)


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsResident(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'resident'


class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'superadmin'


def owner_property_or_404(user, property_id):
    return Property.objects.get(pk=property_id, owner=user)


# ── RESIDENT ──────────────────────────────────────────────────

class ResidentInvoiceListView(generics.ListAPIView):
    permission_classes = [IsResident]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(resident=self.request.user).select_related('property', 'resident')


class ResidentPaymentSummaryView(APIView):
    permission_classes = [IsResident]

    def get(self, request):
        return Response(build_resident_payment_summary(request.user, request))


class ResidentPaymentHistoryView(generics.ListAPIView):
    permission_classes = [IsResident]
    serializer_class = PaymentSubmissionSerializer

    def get_queryset(self):
        return PaymentSubmission.objects.filter(resident=self.request.user).select_related(
            'property', 'resident', 'invoice'
        )


class ResidentSubmitRentProofView(APIView):
    permission_classes = [IsResident]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        try:
            invoice = Invoice.objects.get(pk=pk, resident=request.user)
        except Invoice.DoesNotExist:
            return Response({'detail': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)

        if invoice.status == 'paid':
            return Response({'detail': 'This invoice is already paid.'}, status=status.HTTP_400_BAD_REQUEST)
        if invoice.status == 'pending_verification':
            return Response(
                {'detail': 'Payment proof is already under review.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PaymentProofSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        amount = serializer.validated_data.get('amount') or invoice.get_total_amount()
        submission = PaymentSubmission.objects.create(
            resident=request.user,
            property=invoice.property,
            invoice=invoice,
            submission_type='rent',
            amount=amount,
            transaction_id=serializer.validated_data['transaction_id'],
            payment_method=serializer.validated_data['payment_method'],
            screenshot=serializer.validated_data['screenshot'],
            status='pending_verification',
        )
        invoice.status = 'pending_verification'
        invoice.transaction_id = submission.transaction_id
        invoice.payment_method = submission.payment_method
        invoice.save(update_fields=['status', 'transaction_id', 'payment_method', 'updated_at'])

        return Response(
            {
                'submission': PaymentSubmissionSerializer(submission, context={'request': request}).data,
                'invoice': InvoiceSerializer(invoice).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ResidentSubmitDepositProofView(APIView):
    permission_classes = [IsResident]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        booking = get_active_booking(request.user)
        if not booking:
            return Response({'detail': 'No active stay found.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = DepositProofSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        submission = PaymentSubmission.objects.create(
            resident=request.user,
            property=booking.property,
            submission_type='deposit',
            amount=serializer.validated_data['amount'],
            transaction_id=serializer.validated_data['transaction_id'],
            payment_method=serializer.validated_data['payment_method'],
            screenshot=serializer.validated_data['screenshot'],
            status='pending_verification',
        )
        return Response(
            PaymentSubmissionSerializer(submission, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


# Legacy instant-pay (kept for backward compatibility, redirects behavior via message)
class ResidentPayInvoiceView(APIView):
    permission_classes = [IsResident]

    def patch(self, request, pk):
        return Response(
            {
                'detail': 'Please submit payment proof with screenshot via POST /payments/my/<id>/submit-proof/',
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


# ── OWNER ─────────────────────────────────────────────────────

class OwnerCreateInvoiceView(generics.CreateAPIView):
    permission_classes = [IsOwner]
    serializer_class = InvoiceCreateSerializer

    def perform_create(self, serializer):
        prop = serializer.validated_data['property']
        if prop.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only create invoices for your own properties.')
        serializer.save()


class OwnerInvoiceListView(generics.ListAPIView):
    permission_classes = [IsOwner]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(property__owner=self.request.user).select_related(
            'property', 'resident'
        )


class OwnerInvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOwner]
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        return Invoice.objects.filter(property__owner=self.request.user)


class OwnerPaymentOverviewView(APIView):
    permission_classes = [IsOwner]

    def get(self, request):
        props = Property.objects.filter(owner=request.user)
        invoices = Invoice.objects.filter(property__in=props)
        submissions = PaymentSubmission.objects.filter(property__in=props)

        now = timezone.now()
        monthly_paid = invoices.filter(
            status='paid',
            payment_date__year=now.year,
            payment_date__month=now.month,
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')

        return Response({
            'pending_verifications': submissions.filter(status='pending_verification').count(),
            'unpaid_invoices': invoices.filter(status__in=['unpaid', 'rejected']).count(),
            'overdue_invoices': invoices.filter(
                status__in=['unpaid', 'rejected'],
                due_date__lt=now.date(),
            ).count(),
            'paid_this_month': str(monthly_paid),
            'total_invoices': invoices.count(),
            'recent_payments': PaymentSubmissionSerializer(
                submissions.filter(status='approved').order_by('-reviewed_at')[:8],
                many=True,
                context={'request': request},
            ).data,
            'pending_submissions': PaymentSubmissionSerializer(
                submissions.filter(status='pending_verification').order_by('-submitted_at')[:12],
                many=True,
                context={'request': request},
            ).data,
            'unpaid_residents': [
                {
                    'resident_username': inv.resident.username,
                    'property_name': inv.property.name,
                    'amount': str(inv.get_total_amount()),
                    'due_date': inv.due_date.isoformat(),
                    'invoice_id': inv.id,
                    'status': inv.status,
                }
                for inv in invoices.filter(status__in=['unpaid', 'rejected']).select_related(
                    'resident', 'property'
                )[:20]
            ],
        })


class OwnerPaymentSettingsView(APIView):
    permission_classes = [IsOwner]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, property_id):
        try:
            prop = owner_property_or_404(request.user, property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)
        settings_obj, _ = PropertyPaymentSettings.objects.get_or_create(property=prop)
        return Response(
            PropertyPaymentSettingsSerializer(settings_obj, context={'request': request}).data
        )

    def put(self, request, property_id):
        return self._save(request, property_id, partial=False)

    def patch(self, request, property_id):
        return self._save(request, property_id, partial=True)

    def _save(self, request, property_id, partial):
        try:
            prop = owner_property_or_404(request.user, property_id)
        except Property.DoesNotExist:
            return Response({'detail': 'Property not found.'}, status=status.HTTP_404_NOT_FOUND)
        settings_obj, _ = PropertyPaymentSettings.objects.get_or_create(property=prop)
        serializer = PropertyPaymentSettingsSerializer(
            settings_obj,
            data=request.data,
            partial=partial,
            context={'request': request},
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OwnerSubmissionListView(generics.ListAPIView):
    permission_classes = [IsOwner]
    serializer_class = PaymentSubmissionSerializer

    def get_queryset(self):
        qs = PaymentSubmission.objects.filter(
            property__owner=self.request.user
        ).select_related('resident', 'property', 'invoice')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return qs


class OwnerApproveSubmissionView(APIView):
    permission_classes = [IsOwner]

    def post(self, request, pk):
        try:
            submission = PaymentSubmission.objects.select_related('invoice', 'property').get(
                pk=pk, property__owner=request.user
            )
        except PaymentSubmission.DoesNotExist:
            return Response({'detail': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

        if submission.status != 'pending_verification':
            return Response({'detail': 'Submission is not pending review.'}, status=status.HTTP_400_BAD_REQUEST)

        note_serializer = PaymentReviewSerializer(data=request.data)
        note_serializer.is_valid(raise_exception=True)
        owner_note = note_serializer.validated_data.get('owner_note', '')

        submission.status = 'approved'
        submission.owner_note = owner_note
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.save()

        if submission.invoice_id:
            inv = submission.invoice
            inv.status = 'paid'
            inv.payment_date = timezone.now()
            inv.transaction_id = submission.transaction_id
            inv.payment_method = submission.payment_method
            inv.save(update_fields=['status', 'payment_date', 'transaction_id', 'payment_method', 'updated_at'])

        return Response(PaymentSubmissionSerializer(submission, context={'request': request}).data)


class OwnerRejectSubmissionView(APIView):
    permission_classes = [IsOwner]

    def post(self, request, pk):
        try:
            submission = PaymentSubmission.objects.select_related('invoice').get(
                pk=pk, property__owner=request.user
            )
        except PaymentSubmission.DoesNotExist:
            return Response({'detail': 'Submission not found.'}, status=status.HTTP_404_NOT_FOUND)

        if submission.status != 'pending_verification':
            return Response({'detail': 'Submission is not pending review.'}, status=status.HTTP_400_BAD_REQUEST)

        note_serializer = PaymentReviewSerializer(data=request.data)
        note_serializer.is_valid(raise_exception=True)
        owner_note = note_serializer.validated_data.get('owner_note', '')

        submission.status = 'rejected'
        submission.owner_note = owner_note
        submission.reviewed_by = request.user
        submission.reviewed_at = timezone.now()
        submission.save()

        if submission.invoice_id:
            inv = submission.invoice
            inv.status = 'rejected'
            inv.save(update_fields=['status', 'updated_at'])

        return Response(PaymentSubmissionSerializer(submission, context={'request': request}).data)


# ── SUPERADMIN ────────────────────────────────────────────────

class AllInvoicesListView(generics.ListAPIView):
    permission_classes = [IsSuperAdmin]
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().select_related('property', 'resident')
