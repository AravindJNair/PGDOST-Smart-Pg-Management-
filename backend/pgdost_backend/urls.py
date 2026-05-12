"""
URL configuration for pgdost_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from pgdost_backend.views import api_docs

urlpatterns = [
    path('', api_docs, name='api_home'),
    path('api/', api_docs, name='api_root'),
    path('api/docs/', api_docs, name='api_docs'),
    path('api/auth/', include('accounts.urls')),
    path('api/properties/', include('properties.urls')),
    path('api/bookings/', include('bookings.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/complaints/', include('complaints.urls')),
    path('api/visitors/', include('visitors.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

