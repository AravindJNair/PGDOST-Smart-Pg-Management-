from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    ROLE_CHOICES = (
        ('resident', 'Resident'),
        ('owner', 'Owner'),
        ('superadmin', 'Superadmin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_email_verified = models.BooleanField(default=True)

    # Required to prevent clash with Django's built-in User model
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def has_uploaded_identity_documents(self):
        return self.owner_identity_documents.exists()

    @property
    def can_list_properties(self):
        if self.role != 'owner':
            return False
        return self.is_email_verified and self.has_uploaded_identity_documents

    @property
    def can_request_booking(self):
        return self.role == 'resident'


class OwnerOtp(models.Model):
    id = models.AutoField(primary_key=True)
    PURPOSE_CHOICES = (
        ('email_verification', 'Email Verification'),
        ('password_reset', 'Password Reset'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_otps',
        limit_choices_to={'role': 'owner'},
    )
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.purpose}"


class OwnerIdentityDocument(models.Model):
    id = models.AutoField(primary_key=True)
    DOC_TYPE_CHOICES = (
        ('aadhaar', 'Aadhaar Card'),
        ('pan', 'PAN Card'),
        ('government_id', 'Government ID'),
        ('business_proof', 'Business Proof'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_identity_documents',
        limit_choices_to={'role': 'owner'},
    )
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES)
    document_file = models.FileField(upload_to='owner_identity_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rejection_reason = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('owner', 'document_type')
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.owner.username} - {self.get_document_type_display()}"


class OwnerProfile(models.Model):
    id = models.AutoField(primary_key=True)
    CONTACT_METHOD_CHOICES = (
        ('phone', 'Phone'),
        ('whatsapp', 'WhatsApp'),
        ('email', 'Email'),
    )
    PROPERTY_TYPE_CHOICES = (
        ('pg', 'PG'),
        ('hostel', 'Hostel'),
        ('apartment', 'Apartment'),
        ('mixed', 'Mixed'),
    )
    TENANT_TYPE_CHOICES = (
        ('students', 'Students'),
        ('professionals', 'Professionals'),
        ('families', 'Families'),
        ('mixed', 'Mixed'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owner_profile',
        limit_choices_to={'role': 'owner'},
    )
    profile_photo = models.ImageField(upload_to='owner_profiles/', blank=True, null=True)
    business_name = models.CharField(max_length=200, blank=True)
    alternate_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    number_of_properties = models.PositiveIntegerField(default=0)
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPE_CHOICES, blank=True)
    preferred_tenant_type = models.CharField(max_length=30, choices=TENANT_TYPE_CHOICES, blank=True)
    whatsapp_number = models.CharField(max_length=15, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=CONTACT_METHOD_CHOICES,
        default='phone',
    )
    show_phone_publicly = models.BooleanField(default=True)
    show_whatsapp_publicly = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Owner Profile - {self.user.username}"

    @property
    def is_profile_complete(self):
        required_fields = [
            self.business_name,
            self.address,
            self.city,
            self.state,
            self.pincode,
        ]
        return all(bool(v and str(v).strip()) for v in required_fields)


class Notification(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:20]}"
