from django.contrib import admin
from .models import Invoice, PaymentSubmission, PropertyPaymentSettings


@admin.register(PropertyPaymentSettings)
class PropertyPaymentSettingsAdmin(admin.ModelAdmin):
    list_display = ('property', 'upi_id', 'account_holder_name', 'updated_at')
    search_fields = ('property__name', 'upi_id', 'account_holder_name')


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'resident', 'property', 'amount', 'month', 'year',
        'status', 'due_date', 'payment_date',
    )
    list_filter = ('status', 'year', 'month')
    search_fields = ('resident__username', 'property__name', 'transaction_id')


@admin.register(PaymentSubmission)
class PaymentSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'resident', 'property', 'submission_type', 'amount',
        'status', 'submitted_at', 'reviewed_at',
    )
    list_filter = ('status', 'submission_type', 'payment_method')
    search_fields = ('transaction_id', 'resident__username', 'property__name')
