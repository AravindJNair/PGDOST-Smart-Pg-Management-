import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgdost_backend.settings')
django.setup()

from accounts.models import CustomUser

# Try to find an existing superadmin
superadmins = CustomUser.objects.filter(role='superadmin')

if superadmins.exists():
    # Update the first superadmin found
    admin = superadmins.first()
    admin.username = 'Aravind'
    admin.set_password('aravind@0106')
    admin.save()
    print(f"Updated existing superadmin. Username is now '{admin.username}'.")
else:
    # Create a new superadmin
    admin = CustomUser.objects.create_superuser(
        username='Aravind',
        email='aravind@admin.com',
        password='aravind@0106',
        role='superadmin'
    )
    print(f"Created new superadmin '{admin.username}'.")
