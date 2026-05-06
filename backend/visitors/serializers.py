from rest_framework import serializers
from .models import VisitorLog


class VisitorLogSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    logged_by_username = serializers.CharField(source='logged_by.username', read_only=True, default=None)
    purpose_display = serializers.CharField(source='get_purpose_display', read_only=True)

    class Meta:
        model = VisitorLog
        fields = [
            'id', 'property', 'property_name', 'resident', 'resident_username',
            'visitor_name', 'visitor_phone', 'purpose', 'purpose_display',
            'check_in', 'check_out', 'logged_by', 'logged_by_username',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'logged_by', 'created_at']

    def create(self, validated_data):
        validated_data['logged_by'] = self.context['request'].user
        return super().create(validated_data)
