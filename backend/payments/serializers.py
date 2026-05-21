from decimal import Decimal
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import serializers

from bookings.models import Booking
from properties.models import Property
from .models import Invoice, PaymentSubmission, PropertyPaymentSettings

ALLOWED_PROOF_TYPES = {'image/jpeg', 'image/png', 'image/webp'}
MAX_PROOF_BYTES = 5 * 1024 * 1024


def validate_proof_file(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_PROOF_TYPES:
        raise serializers.ValidationError('Screenshot must be JPG, PNG, or WEBP.')
    if uploaded_file.size > MAX_PROOF_BYTES:
        raise serializers.ValidationError('Screenshot must be 5 MB or less.')


def build_media_url(request, file_field):
    if not file_field:
        return None
    if request:
        return request.build_absolute_uri(file_field.url)
    return file_field.url


class PropertyPaymentSettingsSerializer(serializers.ModelSerializer):
    qr_code_url = serializers.SerializerMethodField()
    property_name = serializers.CharField(source='property.name', read_only=True)

    class Meta:
        model = PropertyPaymentSettings
        fields = [
            'id', 'property', 'property_name', 'upi_id', 'qr_code', 'qr_code_url',
            'account_holder_name', 'bank_name', 'payment_instructions', 'updated_at',
        ]
        read_only_fields = ['id', 'updated_at', 'qr_code_url']
        extra_kwargs = {'qr_code': {'write_only': True}}

    def get_qr_code_url(self, obj):
        return build_media_url(self.context.get('request'), obj.qr_code)


class InvoiceSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    month_display = serializers.CharField(source='get_month_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'amount', 'maintenance_charge', 'food_charge', 'total_amount',
            'month', 'month_display', 'year', 'status', 'status_display',
            'due_date', 'payment_date', 'transaction_id',
            'payment_method', 'payment_method_display', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_amount(self, obj):
        return obj.get_total_amount()


class InvoiceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            'resident', 'property', 'amount', 'maintenance_charge', 'food_charge',
            'month', 'year', 'due_date', 'notes',
        ]

    def validate(self, attrs):
        prop = attrs['property']
        if prop.owner != self.context['request'].user:
            raise serializers.ValidationError({'property': 'You can only invoice for your own properties.'})
        return attrs


class PaymentSubmissionSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    submission_type_display = serializers.CharField(source='get_submission_type_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    screenshot_url = serializers.SerializerMethodField()
    invoice_period = serializers.SerializerMethodField()
    rent_month = serializers.SerializerMethodField()

    class Meta:
        model = PaymentSubmission
        fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'invoice', 'submission_type', 'submission_type_display', 'amount',
            'transaction_id', 'payment_method', 'payment_method_display',
            'screenshot_url', 'status', 'status_display', 'owner_note',
            'reviewed_at', 'submitted_at', 'invoice_period', 'rent_month',
        ]
        read_only_fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'invoice', 'submission_type', 'submission_type_display', 'amount',
            'transaction_id', 'payment_method', 'payment_method_display',
            'screenshot_url', 'status', 'status_display', 'owner_note',
            'reviewed_at', 'submitted_at', 'invoice_period', 'rent_month',
        ]

    def get_screenshot_url(self, obj):
        return build_media_url(self.context.get('request'), obj.screenshot)

    def get_invoice_period(self, obj):
        if not obj.invoice_id:
            return None
        inv = obj.invoice
        return f"{inv.get_month_display()} {inv.year}"

    def get_rent_month(self, obj):
        if not obj.invoice_id:
            return None
        return obj.invoice.month


class PaymentProofSubmitSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
    payment_method = serializers.ChoiceField(choices=Invoice.PAYMENT_METHOD_CHOICES, default='upi')
    screenshot = serializers.ImageField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    def validate_screenshot(self, value):
        validate_proof_file(value)
        return value


class DepositProofSubmitSerializer(serializers.Serializer):
    transaction_id = serializers.CharField(max_length=100)
    payment_method = serializers.ChoiceField(choices=Invoice.PAYMENT_METHOD_CHOICES, default='upi')
    screenshot = serializers.ImageField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_screenshot(self, value):
        validate_proof_file(value)
        return value


class PaymentReviewSerializer(serializers.Serializer):
    owner_note = serializers.CharField(required=False, allow_blank=True)


def get_active_booking(user):
    return (
        Booking.objects.filter(resident=user, status='approved')
        .select_related('property')
        .first()
    )


def compute_deposit_summary(user, prop):
    required = prop.pricing_security_deposit or Decimal('0')
    paid = (
        PaymentSubmission.objects.filter(
            resident=user,
            property=prop,
            submission_type='deposit',
            status='approved',
        ).aggregate(total=Sum('amount'))['total']
        or Decimal('0')
    )
    pending_submissions = PaymentSubmission.objects.filter(
        resident=user,
        property=prop,
        submission_type='deposit',
        status='pending_verification',
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    pending = max(required - paid - pending_submissions, Decimal('0'))
    return {
        'total_required': str(required),
        'amount_paid': str(paid),
        'pending_verification': str(pending_submissions),
        'pending_amount': str(pending),
        'refundable_amount': str(paid),
    }


def build_resident_payment_summary(user, request):
    booking = get_active_booking(user)
    if not booking:
        return {
            'has_active_stay': False,
            'payment_settings': None,
            'rent_summary': None,
            'deposit': None,
        }

    prop = booking.property
    settings_obj = PropertyPaymentSettings.objects.filter(property=prop).first()
    settings_data = (
        PropertyPaymentSettingsSerializer(settings_obj, context={'request': request}).data
        if settings_obj
        else None
    )

    now = timezone.now()
    invoices = list(
        Invoice.objects.filter(resident=user, property=prop).order_by('-year', '-month')
    )
    current = next(
        (i for i in invoices if i.month == now.month and i.year == now.year),
        invoices[0] if invoices else None,
    )

    unpaid = [i for i in invoices if i.status in ('unpaid', 'rejected')]
    due_amount = sum((i.get_total_amount() for i in unpaid), Decimal('0'))
    total_paid = sum(
        (
            i.get_total_amount()
            for i in invoices
            if i.status == 'paid'
        ),
        Decimal('0'),
    )

    rent_summary = {
        'current_month_rent': str(prop.pricing_monthly_rent or (current.amount if current else 0)),
        'due_amount': str(due_amount),
        'due_date': current.due_date.isoformat() if current else None,
        'maintenance_charges': str(
            current.maintenance_charge if current else (prop.pricing_maintenance_charge or 0)
        ),
        'food_charges': str(
            current.food_charge if current else (prop.pricing_food_charge or 0)
        ),
        'total_paid_amount': str(total_paid),
        'current_invoice_id': current.id if current else None,
        'current_invoice_status': current.status if current else None,
    }

    return {
        'has_active_stay': True,
        'property': {'id': prop.id, 'name': prop.name},
        'booking_id': booking.id,
        'payment_settings': settings_data,
        'rent_summary': rent_summary,
        'deposit': compute_deposit_summary(user, prop),
    }
