from django.db import models
from django.conf import settings


def default_nearby_places():
    return {
        'grocery_stores': [],
        'hospitals': [],
        'restaurants': [],
        'gyms': [],
        'cafes': [],
        'colleges': [],
    }


class Property(models.Model):
    """A PG Building registered by an Owner."""
    PROPERTY_TYPE_CHOICES = (
        ('pg', 'PG Accommodation'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        limit_choices_to={'role': 'owner'}
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES, default='pg')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    # Amenities
    has_wifi = models.BooleanField(default=False)
    has_ac = models.BooleanField(default=False)
    has_food = models.BooleanField(default=False)
    has_parking = models.BooleanField(default=False)
    has_laundry = models.BooleanField(default=False)
    has_gym = models.BooleanField(default=False)
    custom_amenities = models.JSONField(default=list, blank=True)
    # Owner-managed detail sections
    lifestyle_highlights = models.TextField(blank=True)
    suitable_for = models.CharField(max_length=50, blank=True, default='students_and_professionals')
    overview_custom_text = models.TextField(blank=True)
    smoking_policy = models.CharField(max_length=120, blank=True, default='Not allowed indoors')
    visitor_rules = models.CharField(max_length=160, blank=True, default='Day visitors till 8:00 PM')
    gate_closing_time = models.CharField(max_length=60, blank=True, default='11:00 PM')
    drinking_rules = models.CharField(max_length=160, blank=True, default='No public-area drinking')
    quiet_hours = models.CharField(max_length=120, blank=True, default='10:30 PM to 6:30 AM')
    nearby_landmarks = models.JSONField(default=list, blank=True)
    nearby_colleges = models.JSONField(default=list, blank=True)
    nearby_transit = models.JSONField(default=list, blank=True)
    google_maps_url = models.URLField(blank=True)
    nearby_places = models.JSONField(default=default_nearby_places, blank=True)
    pricing_monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_security_deposit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_maintenance_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_food_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    alternate_contact = models.CharField(max_length=15, blank=True)
    videos = models.JSONField(default=list, blank=True)
    # Admin approval gate
    is_approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({'Approved' if self.is_approved else 'Pending'})"


class PropertyImage(models.Model):
    """Photos uploaded by the owner for a property."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='property_images/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'uploaded_at']

    def __str__(self):
        return f"Image for {self.property.name}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unset all other primary images for this property
        if self.is_primary:
            PropertyImage.objects.filter(
                property=self.property, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class Room(models.Model):
    """An individual room/unit inside a Property."""
    ROOM_TYPE_CHOICES = (
        ('single', 'Single Occupancy'),
        ('double', 'Double Occupancy'),
        ('triple', 'Triple Occupancy'),
        ('dormitory', 'Dormitory'),
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='rooms'
    )
    room_number = models.CharField(max_length=20)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='single')
    total_beds = models.PositiveIntegerField(default=1)
    available_beds = models.PositiveIntegerField(default=1)
    rent_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    is_available = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_number} - {self.property.name}"

    def save(self, *args, **kwargs):
        self.is_available = self.available_beds > 0
        super().save(*args, **kwargs)


class Review(models.Model):
    """Rating and review for a Property by a Resident."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='property_reviews'
    )
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    review_text = models.TextField(blank=True)
    stay_duration = models.CharField(max_length=120, blank=True)
    is_verified_resident = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('property', 'user')

    def __str__(self):
        return f"{self.user.username} - {self.property.name} ({self.rating}/5)"


class Inquiry(models.Model):
    """Basic inquiry from an anonymous user or resident."""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    sender_phone = models.CharField(max_length=15, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry by {self.sender_name} for {self.property.name}"
