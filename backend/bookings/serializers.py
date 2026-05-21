from rest_framework import serializers
from django.utils import timezone

from .models import Booking, BookingDocument

ALLOWED_UPLOAD_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf',
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

DOCUMENT_SPECS = {
    'aadhaar': {'required': True, 'label': 'Aadhaar / PAN Card'},
    'passport_photo': {'required': True, 'label': 'Passport Photo'},
    'college_id': {'required': False, 'label': 'College ID'},
    'company_id': {'required': False, 'label': 'Company ID'},
    'address_proof': {'required': False, 'label': 'Address Proof'},
}

STUDENT_OCCUPATIONS = {'student', 'intern'}
WORKING_PROFESSIONAL_OCCUPATIONS = {'working-professional'}


def validate_upload_file(uploaded_file):
    content_type = getattr(uploaded_file, 'content_type', '') or ''
    if content_type not in ALLOWED_UPLOAD_CONTENT_TYPES:
        raise serializers.ValidationError('Unsupported file format. Use JPG, PNG, WEBP, or PDF.')
    if uploaded_file.size > MAX_UPLOAD_BYTES:
        raise serializers.ValidationError('File size must be 5 MB or less.')


class BookingDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = BookingDocument
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'document_url',
            'uploaded_at',
        ]

    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and request:
            return request.build_absolute_uri(obj.document_file.url)
        if obj.document_file:
            return obj.document_file.url
        return None


class BookingSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    resident_status_display = serializers.SerializerMethodField()

    def get_resident_status_display(self, obj):
        return obj.get_resident_status_display()
    requested_room_type_display = serializers.CharField(
        source='get_requested_room_type_display',
        read_only=True,
    )
    documents = BookingDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'room', 'room_number', 'status', 'status_display', 'resident_status_display',
            'move_in_date', 'move_out_date', 'message', 'owner_note',
            'resident_full_name', 'resident_phone', 'resident_email',
            'gender', 'occupation', 'emergency_phone', 'occupants',
            'duration_months', 'requested_room_type', 'requested_room_type_display',
            'documents', 'applied_at', 'updated_at',
        ]
        read_only_fields = ['id', 'resident', 'applied_at', 'updated_at', 'status']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Used when a resident applies for a PG with supporting documents."""

    class Meta:
        model = Booking
        fields = [
            'property',
            'move_in_date',
            'message',
            'resident_full_name',
            'resident_phone',
            'resident_email',
            'gender',
            'occupation',
            'emergency_phone',
            'occupants',
            'duration_months',
            'requested_room_type',
        ]

    def validate(self, attrs):
        user = self.context['request'].user
        property_obj = attrs.get('property')
        move_in_date = attrs.get('move_in_date')
        occupation = (attrs.get('occupation') or '').strip()

        if move_in_date and move_in_date < timezone.now().date():
            raise serializers.ValidationError({'move_in_date': 'Move-in date cannot be in the past.'})

        if property_obj is None:
            return attrs

        existing = Booking.objects.filter(resident=user, property=property_obj).order_by('-updated_at').first()
        if existing and existing.status in ['pending', 'approved']:
            message = (
                'You already have a pending request for this property.'
                if existing.status == 'pending'
                else 'You already have an active booking for this property.'
            )
            raise serializers.ValidationError({'property': message})

        request = self.context['request']
        errors = {}
        for doc_type, spec in DOCUMENT_SPECS.items():
            uploaded = request.FILES.get(f'doc_{doc_type}')
            if spec['required'] and not uploaded:
                errors[f'doc_{doc_type}'] = f'{spec["label"]} is required.'
            elif uploaded:
                try:
                    validate_upload_file(uploaded)
                except serializers.ValidationError as exc:
                    errors[f'doc_{doc_type}'] = exc.detail[0] if isinstance(exc.detail, list) else str(exc.detail)

        if occupation in STUDENT_OCCUPATIONS and not request.FILES.get('doc_college_id'):
            errors['doc_college_id'] = 'College ID is required for students and interns.'
        if occupation in WORKING_PROFESSIONAL_OCCUPATIONS and not request.FILES.get('doc_company_id'):
            errors['doc_company_id'] = 'Company ID is required for working professionals.'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def validate_property(self, value):
        if not value.is_approved:
            raise serializers.ValidationError('This property is not yet approved by admin.')
        return value

    def _save_documents(self, booking, request):
        for doc_type in DOCUMENT_SPECS:
            uploaded = request.FILES.get(f'doc_{doc_type}')
            if not uploaded:
                BookingDocument.objects.filter(booking=booking, document_type=doc_type).delete()
                continue
            BookingDocument.objects.update_or_create(
                booking=booking,
                document_type=doc_type,
                defaults={'document_file': uploaded},
            )

    def create(self, validated_data):
        resident = self.context['request'].user
        request = self.context['request']
        property_obj = validated_data['property']
        existing = Booking.objects.filter(resident=resident, property=property_obj).order_by('-updated_at').first()

        if existing and existing.status in ['rejected', 'vacated']:
            for field, value in validated_data.items():
                setattr(existing, field, value)
            existing.status = 'pending'
            existing.room = None
            existing.move_out_date = None
            existing.owner_note = ''
            existing.save()
            self._save_documents(existing, request)
            return existing

        validated_data['resident'] = resident
        booking = super().create(validated_data)
        self._save_documents(booking, request)
        return booking


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by owners to approve/reject bookings."""

    class Meta:
        model = Booking
        fields = ['status', 'room', 'owner_note', 'move_in_date']

    def validate_status(self, value):
        allowed = ['approved', 'rejected', 'vacated']
        if value not in allowed:
            raise serializers.ValidationError(f'Status must be one of: {allowed}')
        return value
