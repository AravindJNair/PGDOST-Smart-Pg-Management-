from django.contrib import admin
from .models import Ticket, TicketReply

class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 0

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'raised_by', 'property', 'category', 'priority', 'status', 'created_at']
    list_filter = ['status', 'category', 'priority']
    search_fields = ['title', 'raised_by__username', 'property__name']
    inlines = [TicketReplyInline]
