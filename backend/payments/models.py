from django.db import models
from django.conf import settings
from django.utils import timezone
from properties.models import Property


class PropertyPaymentSettings(models.Model):
    """Owner UPI / QR configuration per property."""
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name='payment_settings',
    )
    upi_id = models.CharField(max_length=120, blank=True)
    qr_code = models.ImageField(upload_to='payment_qr/%Y/%m/', blank=True, null=True)
    account_holder_name = models.CharField(max_length=150, blank=True)
    bank_name = models.CharField(max_length=120, blank=True)
    payment_instructions = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment settings — {self.property.name}"


class Invoice(models.Model):
    """Rent invoice issued by owner to resident for a given month."""
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('pending_verification', 'Pending Verification'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    )
    MONTH_CHOICES = (
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('upi', 'UPI'),
        ('gpay', 'Google Pay'),
        ('phonepe', 'PhonePe'),
        ('paytm', 'Paytm'),
        ('bhim', 'BHIM UPI'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    )

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        limit_choices_to={'role': 'resident'},
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='invoices',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    food_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='unpaid')
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ('resident', 'property', 'month', 'year')

    def get_total_amount(self):
        return self.amount + self.maintenance_charge + self.food_charge

    def __str__(self):
        return (
            f"Invoice #{self.pk} - {self.resident.username} "
            f"[{self.get_month_display()} {self.year}] - {self.get_status_display()}"
        )


class PaymentSubmission(models.Model):
    """Resident-submitted payment proof for rent or security deposit."""
    TYPE_CHOICES = (
        ('rent', 'Rent'),
        ('deposit', 'Security Deposit'),
    )
    STATUS_CHOICES = (
        ('pending_verification', 'Pending Verification'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    )
    PAYMENT_METHOD_CHOICES = Invoice.PAYMENT_METHOD_CHOICES

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_submissions',
        limit_choices_to={'role': 'resident'},
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='payment_submissions',
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='submissions',
    )
    submission_type = models.CharField(max_length=12, choices=TYPE_CHOICES, default='rent')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='upi')
    screenshot = models.ImageField(upload_to='payment_proofs/%Y/%m/')
    status = models.CharField(max_length=24, choices=STATUS_CHOICES, default='pending_verification')
    owner_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_payment_submissions',
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Payment #{self.pk} — {self.resident.username} ({self.get_submission_type_display()})"
