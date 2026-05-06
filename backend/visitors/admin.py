from django.contrib import admin
from .models import VisitorLog

@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'visitor_name', 'resident', 'property', 'purpose', 'check_in', 'check_out']
    list_filter = ['purpose', 'property']
    search_fields = ['visitor_name', 'resident__username', 'property__name']
