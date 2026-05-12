from django.db import models
from django.conf import settings
from properties.models import Property, Room


class Booking(models.Model):
    """Links a resident to a room in a property."""
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved / Active'),
        ('rejected', 'Rejected'),
        ('vacated', 'Vacated'),
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'role': 'resident'}
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    move_in_date = models.DateField(null=True, blank=True)
    move_out_date = models.DateField(null=True, blank=True)
    # Optional message from resident during application
    message = models.TextField(blank=True)
    # Owner's notes / rejection reason
    owner_note = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        # Prevent duplicate active bookings for same resident+property
        unique_together = ('resident', 'property')

    def __str__(self):
        return f"{self.resident.username} @ {self.property.name} [{self.get_status_display()}]"
