from django.urls import path
from .views import (
    PublicPropertyListView, PublicPropertyDetailView,
    OwnerPropertyListCreateView, OwnerPropertyDetailView,
    OwnerRoomListCreateView, OwnerRoomDetailView,
    OwnerPropertyImageUploadView, OwnerPropertyImageDetailView,
    AdminPropertyListView, AdminPropertyApproveView, AdminPropertyDetailView,
    ReviewListCreateView, InquiryCreateView, OwnerInquiryListView,
    OwnerPropertyReviewsAnalyticsView
)

urlpatterns = [
    # Public marketplace
    path('', PublicPropertyListView.as_view(), name='public-properties'),
    path('<int:pk>/', PublicPropertyDetailView.as_view(), name='public-property-detail'),
    path('<int:property_pk>/reviews/', ReviewListCreateView.as_view(), name='property-reviews'),
    path('<int:property_pk>/inquire/', InquiryCreateView.as_view(), name='property-inquire'),
    # Owner management (more specific paths first)
    path('owner/', OwnerPropertyListCreateView.as_view(), name='owner-properties'),
    path('owner/inquiries/', OwnerInquiryListView.as_view(), name='owner-inquiries'),
    path('owner/<int:property_pk>/reviews/analytics/', OwnerPropertyReviewsAnalyticsView.as_view(), name='owner-property-reviews-analytics'),
    path('owner/rooms/<int:pk>/', OwnerRoomDetailView.as_view(), name='owner-room-detail'),
    path('owner/<int:property_pk>/rooms/', OwnerRoomListCreateView.as_view(), name='owner-rooms'),
    path('owner/<int:property_pk>/images/', OwnerPropertyImageUploadView.as_view(), name='owner-property-images'),
    path('owner/<int:property_pk>/images/<int:image_pk>/', OwnerPropertyImageDetailView.as_view(), name='owner-property-image-detail'),
    path('owner/<int:pk>/', OwnerPropertyDetailView.as_view(), name='owner-property-detail'),
    # Superadmin
    path('admin/all/', AdminPropertyListView.as_view(), name='admin-properties'),
    path('admin/<int:pk>/approve/', AdminPropertyApproveView.as_view(), name='admin-approve-property'),
    path('admin/<int:pk>/', AdminPropertyDetailView.as_view(), name='admin-property-detail'),
]
