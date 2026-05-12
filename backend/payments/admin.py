from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'resident', 'property', 'amount', 'month', 'year', 'status', 'due_date']
    list_filter = ['status', 'year', 'month']
    search_fields = ['resident__username', 'property__name', 'transaction_id']
