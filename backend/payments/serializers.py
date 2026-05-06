from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    resident_username = serializers.CharField(source='resident.username', read_only=True)
    property_name = serializers.CharField(source='property.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    month_display = serializers.CharField(source='get_month_display', read_only=True)

    class Meta:
        model = Invoice
        fields = [
            'id', 'resident', 'resident_username', 'property', 'property_name',
            'amount', 'month', 'month_display', 'year', 'status', 'status_display',
            'due_date', 'payment_date', 'transaction_id', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceCreateSerializer(serializers.ModelSerializer):
    """Owner creates an invoice for a resident."""
    class Meta:
        model = Invoice
        fields = ['resident', 'property', 'amount', 'month', 'year', 'due_date', 'notes']


class InvoicePaySerializer(serializers.ModelSerializer):
    """Resident marks an invoice as paid."""
    class Meta:
        model = Invoice
        fields = ['transaction_id']
