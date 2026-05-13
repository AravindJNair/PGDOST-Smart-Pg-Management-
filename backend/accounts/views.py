from datetime import timedelta
import random
import string

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Notification, OwnerIdentityDocument, OwnerOtp, OwnerProfile
from .serializers import (
    AdminUserSerializer,
    NotificationSerializer,
    OwnerForgotPasswordConfirmSerializer,
    OwnerForgotPasswordRequestSerializer,
    OwnerIdentityDocumentSerializer,
    OwnerOnboardingStatusSerializer,
    OwnerOtpVerifySerializer,
    OwnerProfileSerializer,
    OwnerSignupSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


def _generate_owner_username(email):
    base = (email.split('@')[0] or 'owner').strip().lower()
    safe = ''.join(ch for ch in base if ch.isalnum() or ch in {'_', '.'})[:110] or 'owner'
    while True:
        suffix = ''.join(random.choices(string.digits, k=4))
        username = f"{safe}_{suffix}"
        if not User.objects.filter(username=username).exists():
            return username


def _normalize_phone(value):
    if not value:
        return ''
    return ''.join(ch for ch in str(value) if ch.isdigit())


def _generate_otp():
    return ''.join(random.choices(string.digits, k=6))


def _send_owner_otp(user, purpose):
    otp_code = _generate_otp()
    expiry = timezone.now() + timedelta(minutes=10)
    OwnerOtp.objects.create(
        user=user,
        otp_code=otp_code,
        purpose=purpose,
        expires_at=expiry,
    )
    subject = 'PGDOST Owner Verification OTP'
    if purpose == 'password_reset':
        subject = 'PGDOST Password Reset OTP'
    body = (
        f"Hello {user.first_name or user.username},\n\n"
        f"Your OTP is {otp_code}. It is valid for 10 minutes.\n\n"
        "If this was not you, please ignore this email."
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@pgdost.com'),
        recipient_list=[user.email],
        fail_silently=True,
    )
    return expiry


def _owner_onboarding_payload(user):
    profile = getattr(user, 'owner_profile', None)
    docs = list(user.owner_identity_documents.all())
    identity_uploaded = len(docs) > 0
    identity_status = 'not_submitted'
    if identity_uploaded:
        statuses = {doc.status for doc in docs}
        if 'rejected' in statuses:
            identity_status = 'rejected'
        elif 'pending' in statuses:
            identity_status = 'pending'
        else:
            identity_status = 'verified'
    profile_completed = profile.is_profile_complete if profile else False
    can_list_properties = user.can_list_properties
    payload = {
        'email_verified': bool(user.is_email_verified),
        'identity_uploaded': identity_uploaded,
        'identity_status': identity_status,
        'profile_completed': profile_completed,
        'verification_badge': can_list_properties,
        'can_list_properties': can_list_properties,
        'prompt_message': (
            '' if can_list_properties else 'Verify your account to continue listing properties.'
        ),
    }
    serializer = OwnerOnboardingStatusSerializer(payload)
    return serializer.data


class CustomTokenObtainPairView(APIView):
    """
    Legacy login endpoint that accepts username + password.
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid username or password. Please try again.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {'detail': 'This account has been disabled.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['role'] = user.role

        response_payload = {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'role': user.role,
        }
        if user.role == 'owner':
            response_payload['onboarding'] = _owner_onboarding_payload(user)
        return Response(response_payload, status=status.HTTP_200_OK)


class OwnerSignupView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = OwnerSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        full_name = data['full_name'].strip()
        parts = full_name.split()
        first_name = parts[0] if parts else ''
        last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=_generate_owner_username(data['email']),
            email=data['email'].strip().lower(),
            phone_number=_normalize_phone(data['phone_number']),
            role='owner',
            first_name=first_name,
            last_name=last_name,
            is_email_verified=False,
        )
        user.set_password(data['password'])
        user.save()

        OwnerProfile.objects.get_or_create(user=user)
        expiry = _send_owner_otp(user, 'email_verification')
        return Response(
            {
                'detail': 'Account created successfully. Verify your email to continue.',
                'email': user.email,
                'otp_expires_at': expiry.isoformat(),
            },
            status=status.HTTP_201_CREATED,
        )


class OwnerLoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        identifier = request.data.get('identifier', '').strip()
        password = request.data.get('password', '')
        if not identifier or not password:
            return Response(
                {'detail': 'Email/phone and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        normalized_identifier = _normalize_phone(identifier)
        user = User.objects.filter(
            Q(role='owner')
            & (
                Q(email__iexact=identifier)
                | Q(phone_number=identifier)
                | Q(username__iexact=identifier)
            )
        ).first()
        if not user and normalized_identifier:
            user = next(
                (
                    u for u in User.objects.filter(role='owner').exclude(phone_number__isnull=True)
                    if _normalize_phone(u.phone_number) == normalized_identifier
                ),
                None,
            )
        if not user:
            return Response({'detail': 'Account not found.'}, status=status.HTTP_404_NOT_FOUND)

        auth_user = authenticate(request=request, username=user.username, password=password)
        if auth_user is None:
            return Response(
                {'detail': 'Invalid credentials. Please try again.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not auth_user.is_active:
            return Response({'detail': 'This account has been disabled.'}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(auth_user)
        refresh['username'] = auth_user.username
        refresh['role'] = auth_user.role
        return Response(
            {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'username': auth_user.username,
                'role': auth_user.role,
                'email': auth_user.email,
                'onboarding': _owner_onboarding_payload(auth_user),
            },
            status=status.HTTP_200_OK,
        )


class OwnerEmailOtpRequestView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        email = request.data.get('email', '').strip().lower()
        if not email:
            return Response({'detail': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(email__iexact=email, role='owner').first()
        if not user:
            return Response({'detail': 'Owner account not found.'}, status=status.HTTP_404_NOT_FOUND)
        expiry = _send_owner_otp(user, 'email_verification')
        otp_code = ''
        if settings.DEBUG:
            otp_obj = OwnerOtp.objects.filter(user=user, purpose='email_verification').order_by('-created_at').first()
            otp_code = otp_obj.otp_code if otp_obj else ''
        return Response(
            {
                'detail': 'OTP sent successfully.',
                'otp_expires_at': expiry.isoformat(),
                'otp_code': otp_code,
            },
            status=status.HTTP_200_OK,
        )


class OwnerEmailOtpVerifyView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = OwnerOtpVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email'].strip().lower()
        otp = serializer.validated_data['otp'].strip()
        user = User.objects.filter(email__iexact=email, role='owner').first()
        if not user:
            return Response({'detail': 'Owner account not found.'}, status=status.HTTP_404_NOT_FOUND)
        otp_obj = OwnerOtp.objects.filter(
            user=user,
            purpose='email_verification',
            otp_code=otp,
            is_used=False,
        ).order_by('-created_at').first()
        if not otp_obj:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        if otp_obj.expires_at < timezone.now():
            return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        return Response({'detail': 'Email verified successfully.'}, status=status.HTTP_200_OK)


class OwnerForgotPasswordRequestView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = OwnerForgotPasswordRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier'].strip()
        user = User.objects.filter(
            role='owner'
        ).filter(
            Q(email__iexact=identifier) | Q(phone_number=identifier) | Q(username__iexact=identifier)
        ).first()
        if not user:
            return Response({'detail': 'Owner account not found.'}, status=status.HTTP_404_NOT_FOUND)
        if not user.email:
            return Response({'detail': 'No email linked to this account.'}, status=status.HTTP_400_BAD_REQUEST)
        expiry = _send_owner_otp(user, 'password_reset')
        otp_code = ''
        if settings.DEBUG:
            otp_obj = OwnerOtp.objects.filter(user=user, purpose='password_reset').order_by('-created_at').first()
            otp_code = otp_obj.otp_code if otp_obj else ''
        return Response(
            {
                'detail': 'Password reset OTP sent successfully.',
                'email': user.email,
                'otp_expires_at': expiry.isoformat(),
                'otp_code': otp_code,
            },
            status=status.HTTP_200_OK,
        )


class OwnerForgotPasswordConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = OwnerForgotPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        identifier = serializer.validated_data['identifier'].strip()
        otp = serializer.validated_data['otp'].strip()
        user = User.objects.filter(role='owner').filter(
            Q(email__iexact=identifier) | Q(phone_number=identifier) | Q(username__iexact=identifier)
        ).first()
        if not user:
            return Response({'detail': 'Owner account not found.'}, status=status.HTTP_404_NOT_FOUND)
        otp_obj = OwnerOtp.objects.filter(
            user=user,
            purpose='password_reset',
            otp_code=otp,
            is_used=False,
        ).order_by('-created_at').first()
        if not otp_obj:
            return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
        if otp_obj.expires_at < timezone.now():
            return Response({'detail': 'OTP has expired. Please request a new one.'}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        return Response({'detail': 'Password reset successful.'}, status=status.HTTP_200_OK)


class OwnerOnboardingStatusView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        if request.user.role != 'owner':
            return Response({'detail': 'Only owners can access this endpoint.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(_owner_onboarding_payload(request.user), status=status.HTTP_200_OK)


class OwnerProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OwnerProfileSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_object(self):
        if self.request.user.role != 'owner':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only owners can access this endpoint.')
        profile, _ = OwnerProfile.objects.get_or_create(user=self.request.user)
        return profile


class OwnerIdentityDocumentListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OwnerIdentityDocumentSerializer
    parser_classes = [JSONParser, FormParser, MultiPartParser]

    def get_queryset(self):
        if self.request.user.role != 'owner':
            return OwnerIdentityDocument.objects.none()
        return OwnerIdentityDocument.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != 'owner':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Only owners can upload documents.')
        serializer.save(owner=self.request.user, status='pending', rejection_reason='')


class OwnerIdentityDocumentDetailView(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = OwnerIdentityDocumentSerializer

    def get_queryset(self):
        if self.request.user.role != 'owner':
            return OwnerIdentityDocument.objects.none()
        return OwnerIdentityDocument.objects.filter(owner=self.request.user)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class SuperadminUserListView(generics.ListAPIView):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = AdminUserSerializer

    def get_permissions(self):
        return [
            permissions.IsAuthenticated(),
            type(
                'IsSuperAdmin',
                (permissions.BasePermission,),
                {'has_permission': lambda self, request, view: getattr(request.user, 'role', '') == 'superadmin'},
            )(),
        ]


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationUpdateView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['patch']

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
