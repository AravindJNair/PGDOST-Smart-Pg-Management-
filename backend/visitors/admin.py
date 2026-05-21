from django.contrib import admin
from .models import VisitorLog, VisitorRequest


@admin.register(VisitorRequest)
class VisitorRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'visitor_name', 'resident', 'property', 'status', 'requested_check_in',
        'requested_check_out',
        'created_at', 'reviewed_at',
    ]
    list_filter = ['status', 'purpose', 'property']
    search_fields = ['visitor_name', 'resident__username', 'property__name']

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'visitor_name', 'resident', 'property', 'purpose', 'check_in', 'check_out']
    list_filter = ['purpose', 'property']
    search_fields = ['visitor_name', 'resident__username', 'property__name']
