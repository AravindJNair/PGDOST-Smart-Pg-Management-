from django.contrib import admin
from .models import CustomUser, Notification, OwnerIdentityDocument, OwnerOtp, OwnerProfile

admin.site.register(CustomUser)
admin.site.register(Notification)
admin.site.register(OwnerOtp)
admin.site.register(OwnerIdentityDocument)
admin.site.register(OwnerProfile)
