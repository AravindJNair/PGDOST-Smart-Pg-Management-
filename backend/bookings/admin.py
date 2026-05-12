from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'resident', 'property', 'room', 'status', 'applied_at']
    list_filter = ['status', 'property']
    search_fields = ['resident__username', 'property__name']
    list_select_related = ['resident', 'property', 'room']
