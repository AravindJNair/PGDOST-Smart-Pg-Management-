from django.contrib import admin
from .models import Property, Room

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'city', 'property_type', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'property_type', 'city']
    search_fields = ['name', 'owner__username', 'city']
    actions = ['approve_properties']
    inlines = [RoomInline]

    @admin.action(description='Approve selected properties')
    def approve_properties(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_approved=True, approved_at=timezone.now())
