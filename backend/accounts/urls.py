from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, CustomTokenObtainPairView, UserProfileView, SuperadminUserListView,
    NotificationListView, NotificationUpdateView
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
]
