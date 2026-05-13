from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import (
    CustomUser,
    Notification,
    OwnerIdentityDocument,
    OwnerOtp,
    OwnerProfile,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'phone_number',
            'role',
            'password',
            'first_name',
            'last_name',
            'is_email_verified',
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            validate_password(password)
        return attrs

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', 'resident'),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id',
            'username',
            'email',
            'phone_number',
            'role',
            'first_name',
            'last_name',
            'date_joined',
            'is_active',
            'is_email_verified',
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'message', 'created_at']


def _normalize_phone(value):
    if not value:
        return ''
    return ''.join(ch for ch in str(value) if ch.isdigit())


class OwnerSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=15)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate_email(self, value):
        if CustomUser.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Email address is already registered.')
        return value

    def validate_phone_number(self, value):
        normalized = _normalize_phone(value)
        if CustomUser.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError('Phone number is already registered.')
        return normalized

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        validate_password(attrs['password'])
        return attrs


class OwnerOtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)


class OwnerForgotPasswordRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=254)


class OwnerForgotPasswordConfirmSerializer(serializers.Serializer):
    identifier = serializers.CharField(max_length=254)
    otp = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'Passwords do not match.'})
        validate_password(attrs['new_password'])
        return attrs


class OwnerIdentityDocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    document_url = serializers.SerializerMethodField()

    class Meta:
        model = OwnerIdentityDocument
        fields = [
            'id',
            'document_type',
            'document_type_display',
            'document_file',
            'document_url',
            'status',
            'status_display',
            'rejection_reason',
            'uploaded_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'status', 'rejection_reason', 'uploaded_at', 'updated_at']

    def get_document_url(self, obj):
        request = self.context.get('request')
        if obj.document_file and request:
            return request.build_absolute_uri(obj.document_file.url)
        if obj.document_file:
            return obj.document_file.url
        return None


class OwnerProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    profile_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = OwnerProfile
        fields = [
            'profile_photo',
            'profile_photo_url',
            'full_name',
            'business_name',
            'email',
            'phone_number',
            'alternate_phone',
            'address',
            'city',
            'state',
            'pincode',
            'years_of_experience',
            'number_of_properties',
            'property_type',
            'preferred_tenant_type',
            'whatsapp_number',
            'emergency_contact',
            'preferred_contact_method',
            'show_phone_publicly',
            'show_whatsapp_publicly',
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.user.first_name} {obj.user.last_name}".strip()
        return full_name or obj.user.username

    def get_profile_photo_url(self, obj):
        request = self.context.get('request')
        if obj.profile_photo and request:
            return request.build_absolute_uri(obj.profile_photo.url)
        if obj.profile_photo:
            return obj.profile_photo.url
        return None


class OwnerOnboardingStatusSerializer(serializers.Serializer):
    email_verified = serializers.BooleanField()
    identity_uploaded = serializers.BooleanField()
    identity_status = serializers.CharField()
    profile_completed = serializers.BooleanField()
    verification_badge = serializers.BooleanField()
    can_list_properties = serializers.BooleanField()
    prompt_message = serializers.CharField()

