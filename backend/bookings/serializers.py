from rest_framework import serializers
from .models import Booking
from properties.models import Property, Room


class BookingSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True, default=None)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'room', 'room_number', 'status', 'status_display',
            'move_in_date', 'move_out_date', 'message', 'owner_note',
            'applied_at', 'updated_at'
        ]
        read_only_fields = ['id', 'resident', 'applied_at', 'updated_at', 'status']


class BookingCreateSerializer(serializers.ModelSerializer):
    """Used when a resident applies for a PG."""
    class Meta:
        model = Booking
        fields = ['property', 'move_in_date', 'message']

    def validate_property(self, value):
        if not value.is_approved:
            raise serializers.ValidationError("This property is not yet approved by admin.")
        return value

    def create(self, validated_data):
        validated_data['resident'] = self.context['request'].user
        return super().create(validated_data)


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    """Used by owners to approve/reject bookings."""
    class Meta:
        model = Booking
        fields = ['status', 'room', 'owner_note', 'move_in_date']

    def validate_status(self, value):
        allowed = ['approved', 'rejected', 'vacated']
        if value not in allowed:
            raise serializers.ValidationError(f"Status must be one of: {allowed}")
        return value
