from django.db import models
from django.conf import settings
from properties.models import Property, Room


class Booking(models.Model):
    """Links a resident to a room in a property."""
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('approved', 'Approved / Active'),
        ('rejected', 'Rejected'),
        ('vacated', 'Vacated'),
    )
    ROOM_TYPE_CHOICES = (
        ('single', 'Single'),
        ('double', 'Double'),
        ('triple', 'Triple'),
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
    message = models.TextField(blank=True)
    owner_note = models.TextField(blank=True)
    resident_full_name = models.CharField(max_length=200, blank=True)
    resident_phone = models.CharField(max_length=15, blank=True)
    resident_email = models.EmailField(blank=True)
    gender = models.CharField(max_length=10, blank=True)
    occupation = models.CharField(max_length=50, blank=True)
    emergency_phone = models.CharField(max_length=15, blank=True)
    occupants = models.PositiveSmallIntegerField(default=1)
    duration_months = models.PositiveSmallIntegerField(null=True, blank=True)
    requested_room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ('resident', 'property')

    def __str__(self):
        return f"{self.resident.username} @ {self.property.name} [{self.get_status_display()}]"

    def get_resident_status_display(self):
        mapping = {
            'pending': 'Pending Owner Approval',
            'approved': 'Approved',
            'rejected': 'Rejected',
            'vacated': 'Vacated',
        }
        return mapping.get(self.status, self.get_status_display())


class BookingDocument(models.Model):
    DOC_TYPE_CHOICES = (
        ('aadhaar', 'Aadhaar / PAN Card'),
        ('college_id', 'College ID'),
        ('company_id', 'Company ID'),
        ('passport_photo', 'Passport Photo'),
        ('address_proof', 'Address Proof'),
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    document_file = models.FileField(upload_to='booking_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('booking', 'document_type')
        ordering = ['document_type']

    def __str__(self):
        return f"{self.booking_id} - {self.get_document_type_display()}"
