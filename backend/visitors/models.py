from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property


class VisitorRequest(models.Model):
    """Resident-submitted visitor request that requires owner approval."""
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    PURPOSE_CHOICES = (
        ('personal', 'Personal Visit'),
        ('delivery', 'Delivery'),
        ('official', 'Official / Work'),
        ('other', 'Other'),
    )

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='visitor_requests',
    )
    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visitor_requests',
        limit_choices_to={'role': 'resident'},
    )
    visitor_name = models.CharField(max_length=150)
    visitor_phone = models.CharField(max_length=15, blank=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='personal')
    requested_check_in = models.DateTimeField()
    requested_check_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_visitor_requests',
        limit_choices_to={'role': 'owner'},
    )
    owner_note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.visitor_name} request for {self.resident.username} ({self.status})"


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

    def get_visit_status(self, at_time=None):
        current_time = at_time or timezone.now()
        if self.check_out and current_time >= self.check_out:
            return 'completed'
        if current_time < self.check_in:
            return 'upcoming'
        return 'active'
