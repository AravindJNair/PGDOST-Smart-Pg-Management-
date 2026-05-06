from django.db import models
from django.conf import settings
from properties.models import Property


class VisitorLog(models.Model):
    """A log entry for a visitor visiting a resident at a property."""
    PURPOSE_CHOICES = (
        ('personal', 'Personal Visit'),
        ('delivery', 'Delivery'),
        ('official', 'Official / Work'),
        ('other', 'Other'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='visitor_logs'
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visitor_logs',
        limit_choices_to={'role': 'resident'}
    )
    visitor_name = models.CharField(max_length=150)
    visitor_phone = models.CharField(max_length=15, blank=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='personal')
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    # Who logged this entry (owner/guard/resident)
    logged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logged_entries'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-check_in']

    def __str__(self):
        return f"{self.visitor_name} visiting {self.resident.username} @ {self.property.name}"
