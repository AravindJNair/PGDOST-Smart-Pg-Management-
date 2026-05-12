"""
show_owners.py  — Reset all owner passwords and print credentials.
Run from backend/ with venv activated:
    python show_owners.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgdost_backend.settings')
django.setup()

from accounts.models import CustomUser
from properties.models import Property

NEW_PASSWORD = "Owner@123"

owners = CustomUser.objects.filter(role='owner').order_by('id')

print("\n" + "=" * 80)
print("  PG OWNER CREDENTIALS")
print("=" * 80)
print("  %-22s %-15s %-35s %s" % ('Username', 'Password', 'Email', 'PG Properties'))
print("  " + "-" * 76)

for owner in owners:
    # Reset password to known value
    owner.set_password(NEW_PASSWORD)
    owner.save()

    props = Property.objects.filter(owner=owner).values_list('name', flat=True)
    props_str = ', '.join(props) if props else '(no property yet)'
    print("  %-22s %-15s %-35s %s" % (owner.username, NEW_PASSWORD, owner.email, props_str))

print("=" * 80)
print("\n  All owner passwords have been RESET to: Owner@123")
print("  Total owners: %d\n" % owners.count())
