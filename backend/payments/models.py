from django.db import models
from django.conf import settings
from properties.models import Property


class Invoice(models.Model):
    """A rent invoice issued by an owner to a resident for a given month."""
    STATUS_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('paid', 'Paid'),
    )
    MONTH_CHOICES = (
        (1, 'January'), (2, 'February'), (3, 'March'),
        (4, 'April'), (5, 'May'), (6, 'June'),
        (7, 'July'), (8, 'August'), (9, 'September'),
        (10, 'October'), (11, 'November'), (12, 'December'),
    )

    resident = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='invoices',
        limit_choices_to={'role': 'resident'}
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='invoices'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')
    due_date = models.DateField()
    payment_date = models.DateTimeField(null=True, blank=True)
    # Reference / Transaction ID for proof of payment
    transaction_id = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-year', '-month']
        unique_together = ('resident', 'property', 'month', 'year')

    def __str__(self):
        return f"Invoice #{self.pk} - {self.resident.username} [{self.get_month_display()} {self.year}] - {self.get_status_display()}"
