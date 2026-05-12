from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import CustomUser
from .serializers import UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializer


class CustomTokenObtainPairView(APIView):
    """
    Custom login view — uses Django's authenticate() directly,
    then creates JWT tokens via RefreshToken.for_user().
    Returns: access, refresh, username, role
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        username = request.data.get('username', '').strip()
        password = request.data.get('password', '')

        if not username or not password:
            return Response(
                {'detail': 'Username and password are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(request=request, username=username, password=password)

        if user is None:
            return Response(
                {'detail': 'Invalid username or password. Please try again.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'detail': 'This account has been disabled.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        refresh['username'] = user.username
        refresh['role'] = user.role

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'username': user.username,
            'role': user.role,
        }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class SuperadminUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all().order_date_joined_desc() if hasattr(CustomUser.objects, 'order_date_joined_desc') else CustomUser.objects.all().order_by('-date_joined')
    from .serializers import AdminUserSerializer
    serializer_class = AdminUserSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated(), type('IsSuperAdmin', (permissions.BasePermission,), {'has_permission': lambda self, request, view: getattr(request.user, 'role', '') == 'superadmin'})()]


from .models import Notification
from .serializers import NotificationSerializer

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
