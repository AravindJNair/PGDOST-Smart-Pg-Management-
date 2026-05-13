from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, UserProfileView, SuperadminUserListView,
    NotificationListView, NotificationUpdateView,
    OwnerSignupView, OwnerLoginView,
    OwnerEmailOtpRequestView, OwnerEmailOtpVerifyView,
    OwnerForgotPasswordRequestView, OwnerForgotPasswordConfirmView,
    OwnerOnboardingStatusView, OwnerProfileView,
    OwnerIdentityDocumentListCreateView, OwnerIdentityDocumentDetailView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_alt'),  # alias for frontend
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('users/', SuperadminUserListView.as_view(), name='superadmin_user_list'),
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/<int:pk>/', NotificationUpdateView.as_view(), name='notification_update'),
    path('owner/signup/', OwnerSignupView.as_view(), name='owner_signup'),
    path('owner/login/', OwnerLoginView.as_view(), name='owner_login'),
    path('owner/verify-email/request/', OwnerEmailOtpRequestView.as_view(), name='owner_verify_email_request'),
    path('owner/verify-email/confirm/', OwnerEmailOtpVerifyView.as_view(), name='owner_verify_email_confirm'),
    path('owner/password/forgot/request/', OwnerForgotPasswordRequestView.as_view(), name='owner_password_forgot_request'),
    path('owner/password/forgot/confirm/', OwnerForgotPasswordConfirmView.as_view(), name='owner_password_forgot_confirm'),
    path('owner/onboarding-status/', OwnerOnboardingStatusView.as_view(), name='owner_onboarding_status'),
    path('owner/profile/', OwnerProfileView.as_view(), name='owner_profile'),
    path('owner/identity-documents/', OwnerIdentityDocumentListCreateView.as_view(), name='owner_identity_document_list'),
    path('owner/identity-documents/<int:pk>/', OwnerIdentityDocumentDetailView.as_view(), name='owner_identity_document_detail'),
]
