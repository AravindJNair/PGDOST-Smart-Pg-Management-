from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from bookings.models import Booking
from .models import VisitorLog, VisitorRequest


class VisitorRequestSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_username = serializers.CharField(source='reviewed_by.username', read_only=True, default=None)
    can_owner_act = serializers.SerializerMethodField()

    class Meta:
        model = VisitorRequest
        fields = [
            'id',
            'property',
            'property_name',
            'resident',
            'resident_username',
            'visitor_name',
            'visitor_phone',
            'purpose',
            'purpose_display',
            'requested_check_in',
            'requested_check_out',
            'notes',
            'status',
            'status_display',
            'owner_note',
            'reviewed_at',
            'reviewed_by',
            'reviewed_by_username',
            'created_at',
            'updated_at',
            'can_owner_act',
        ]
        read_only_fields = [
            'id',
            'resident',
            'status',
            'owner_note',
            'reviewed_at',
            'reviewed_by',
            'created_at',
            'updated_at',
        ]

    def get_can_owner_act(self, obj):
        return obj.status == VisitorRequest.STATUS_PENDING

    def validate(self, attrs):
        request = self.context['request']
        prop = attrs.get('property')
        check_in = attrs.get('requested_check_in')
        check_out = attrs.get('requested_check_out')
        if request.user.role != 'resident':
            raise serializers.ValidationError('Only residents can submit visitor requests.')
        has_booking = Booking.objects.filter(
            resident=request.user,
            property=prop,
            status='approved',
        ).exists()
        if not has_booking:
            raise serializers.ValidationError(
                {'property': 'You can request visitors only for your active approved booking.'}
            )

        if self.instance is None and not check_out:
            raise serializers.ValidationError(
                {'requested_check_out': 'Expected check-out date and time is required.'}
            )
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {'requested_check_out': 'Expected check-out must be later than expected check-in.'}
            )
        if check_in and check_in < timezone.now() - timedelta(minutes=15):
            raise serializers.ValidationError(
                {'requested_check_in': 'Expected check-in cannot be in the past.'}
            )
        return attrs

    def create(self, validated_data):
        validated_data['resident'] = self.context['request'].user
        return super().create(validated_data)


class VisitorLogSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    logged_by_username = serializers.CharField(source='logged_by.username', read_only=True, default=None)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)
    visit_status = serializers.SerializerMethodField()
    visit_status_display = serializers.SerializerMethodField()

    class Meta:
        model = VisitorLog
        fields = [
            'id', 'property', 'property_name', 'resident', 'resident_username',
            'visitor_name', 'visitor_phone', 'purpose', 'purpose_display',
            'check_in', 'check_out', 'logged_by', 'logged_by_username',
            'notes', 'created_at', 'visit_status', 'visit_status_display'
        ]
        read_only_fields = [
            'id', 'property', 'resident', 'visitor_name', 'visitor_phone',
            'purpose', 'check_in', 'logged_by', 'notes', 'created_at',
        ]

    def get_visit_status(self, obj):
        return obj.get_visit_status()

    def get_visit_status_display(self, obj):
        status_map = {
            'upcoming': 'Upcoming',
            'active': 'Active / Inside',
            'completed': 'Completed',
        }
        return status_map.get(obj.get_visit_status(), 'Upcoming')

    def validate_check_out(self, value):
        if self.instance and value and value <= self.instance.check_in:
            raise serializers.ValidationError('Check-out must be later than check-in.')
        return value

    def create(self, validated_data):
        validated_data['logged_by'] = self.context['request'].user
        return super().create(validated_data)
