"""
Populate Bangalore-focused demo PG listings for the public marketplace.

Run from the project root:
    backend\\venv\\Scripts\\python.exe backend\\populate_bangalore_properties.py
"""
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pgdost_backend.settings")

import django

django.setup()

from django.utils import timezone

from accounts.models import CustomUser
from properties.models import Property, Room


OWNER_PASSWORD = "Owner@123"


BANGALORE_PROPERTIES = [
    {
        "name": "Greenfield Estate",
        "owner_username": "owner_greenfield",
        "owner_email": "owner.greenfield@pgdost.com",
        "property_type": "pg",
        "address": "12th Main Road, Indiranagar",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560038",
        "phone": "9876543210",
        "email": "greenfield@pgdost.com",
        "description": "Premium studio-style PG near cafes, metro access, and startup offices in Indiranagar.",
        "amenities": {
            "has_wifi": True,
            "has_ac": True,
            "has_food": True,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": False,
        },
        "rooms": [
            ("I-101", "single", 1, 1, 24500, "Private studio room with work desk and balcony light."),
            ("I-202", "double", 2, 2, 18500, "Twin-sharing premium room with attached bath."),
        ],
    },
    {
        "name": "Sage Residency",
        "owner_username": "owner_sage_residency",
        "owner_email": "owner.sage@pgdost.com",
        "property_type": "pg",
        "address": "5th Block, Koramangala",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560095",
        "phone": "9876543211",
        "email": "sage@pgdost.com",
        "description": "Shared luxury PG for working professionals close to Koramangala tech parks and restaurants.",
        "amenities": {
            "has_wifi": True,
            "has_ac": True,
            "has_food": True,
            "has_parking": False,
            "has_laundry": True,
            "has_gym": True,
        },
        "rooms": [
            ("K-301", "single", 1, 1, 26500, "Single occupancy suite with AC and weekly housekeeping."),
            ("K-302", "double", 2, 1, 18200, "Shared luxury room with food and laundry included."),
        ],
    },
    {
        "name": "Whitefield Urban Nest",
        "owner_username": "owner_whitefield_nest",
        "owner_email": "owner.whitefield@pgdost.com",
        "property_type": "apartment",
        "address": "ITPL Main Road, Whitefield",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560066",
        "phone": "9876543212",
        "email": "whitefieldnest@pgdost.com",
        "description": "Managed apartment-style accommodation near ITPL, EPIP Zone, and major tech campuses.",
        "amenities": {
            "has_wifi": True,
            "has_ac": True,
            "has_food": False,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": True,
        },
        "rooms": [
            ("W-1101", "single", 1, 1, 28000, "Private furnished apartment room with city view."),
            ("W-1102", "double", 2, 2, 19800, "Spacious twin-sharing apartment room."),
        ],
    },
    {
        "name": "HSR Comfort House",
        "owner_username": "owner_hsr_comfort",
        "owner_email": "owner.hsr@pgdost.com",
        "property_type": "pg",
        "address": "Sector 2, HSR Layout",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560102",
        "phone": "9876543213",
        "email": "hsrcomfort@pgdost.com",
        "description": "Calm residential PG in HSR Layout with quick access to Bellandur and Silk Board.",
        "amenities": {
            "has_wifi": True,
            "has_ac": False,
            "has_food": True,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": False,
        },
        "rooms": [
            ("H-201", "single", 1, 1, 22000, "Single room with attached bath and study desk."),
            ("H-204", "triple", 3, 3, 14500, "Budget triple-sharing room with meals included."),
        ],
    },
    {
        "name": "Manyata Executive Stay",
        "owner_username": "owner_manyata_exec",
        "owner_email": "owner.manyata@pgdost.com",
        "property_type": "pg",
        "address": "Nagavara Junction, Manyata Tech Park Road",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560045",
        "phone": "9876543214",
        "email": "manyataexec@pgdost.com",
        "description": "Executive PG for professionals working around Manyata Tech Park and Hebbal.",
        "amenities": {
            "has_wifi": True,
            "has_ac": True,
            "has_food": True,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": True,
        },
        "rooms": [
            ("M-501", "single", 1, 1, 25500, "Executive single room with AC and high-speed WiFi."),
            ("M-502", "double", 2, 2, 17500, "Twin-sharing room with all meals included."),
        ],
    },
    {
        "name": "Electronic City CoLiving",
        "owner_username": "owner_ecity_coliving",
        "owner_email": "owner.ecity@pgdost.com",
        "property_type": "hostel",
        "address": "Phase 1, Electronic City",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560100",
        "phone": "9876543215",
        "email": "ecitycoliving@pgdost.com",
        "description": "Affordable co-living hostel near Electronic City offices, ideal for interns and freshers.",
        "amenities": {
            "has_wifi": True,
            "has_ac": False,
            "has_food": True,
            "has_parking": False,
            "has_laundry": True,
            "has_gym": False,
        },
        "rooms": [
            ("E-101", "double", 2, 2, 13500, "Double-sharing room with meals and WiFi."),
            ("E-102", "dormitory", 4, 4, 9800, "Budget dormitory bed with shared facilities."),
        ],
    },
    {
        "name": "Jayanagar Garden PG",
        "owner_username": "owner_jayanagar_garden",
        "owner_email": "owner.jayanagar@pgdost.com",
        "property_type": "pg",
        "address": "4th Block, Jayanagar",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560011",
        "phone": "9876543216",
        "email": "jayanagargarden@pgdost.com",
        "description": "Peaceful garden-side PG in Jayanagar with homely food and metro connectivity.",
        "amenities": {
            "has_wifi": True,
            "has_ac": False,
            "has_food": True,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": False,
        },
        "rooms": [
            ("J-301", "single", 1, 1, 21000, "Private room in a quiet residential location."),
            ("J-302", "double", 2, 2, 15800, "Double-sharing room with homely meals."),
        ],
    },
    {
        "name": "Bellandur Lakeview Suites",
        "owner_username": "owner_bellandur_suites",
        "owner_email": "owner.bellandur@pgdost.com",
        "property_type": "apartment",
        "address": "Outer Ring Road, Bellandur",
        "city": "Bangalore",
        "state": "Karnataka",
        "pincode": "560103",
        "phone": "9876543217",
        "email": "bellandurlakeview@pgdost.com",
        "description": "Premium managed suites close to ORR offices, Bellandur, and Marathahalli.",
        "amenities": {
            "has_wifi": True,
            "has_ac": True,
            "has_food": False,
            "has_parking": True,
            "has_laundry": True,
            "has_gym": True,
        },
        "rooms": [
            ("B-701", "single", 1, 1, 30000, "Lakeview private suite with AC and work zone."),
            ("B-702", "double", 2, 1, 21500, "Premium twin-sharing suite near ORR."),
        ],
    },
]


def get_owner(username, email):
    owner, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            "role": "owner",
            "email": email,
            "first_name": "PG",
            "last_name": "Owner",
            "phone_number": "9876500000",
        },
    )
    if created or owner.role != "owner":
        owner.role = "owner"
    if owner.email != email:
        owner.email = email
    owner.set_password(OWNER_PASSWORD)
    owner.save()
    return owner


def populate():
    created_count = 0
    updated_count = 0

    for item in BANGALORE_PROPERTIES:
        owner = get_owner(item["owner_username"], item["owner_email"])
        amenities = item["amenities"]
        prop_defaults = {
            "owner": owner,
            "description": item["description"],
            "property_type": item["property_type"],
            "address": item["address"],
            "city": item["city"],
            "state": item["state"],
            "pincode": item["pincode"],
            "phone": item["phone"],
            "email": item["email"],
            "is_approved": True,
            "approved_at": timezone.now(),
            **amenities,
        }
        prop, created = Property.objects.update_or_create(
            name=item["name"],
            defaults=prop_defaults,
        )
        created_count += int(created)
        updated_count += int(not created)

        existing_rooms = set()
        for room_number, room_type, total_beds, available_beds, rent, description in item["rooms"]:
            Room.objects.update_or_create(
                property=prop,
                room_number=room_number,
                defaults={
                    "room_type": room_type,
                    "total_beds": total_beds,
                    "available_beds": available_beds,
                    "rent_per_month": rent,
                    "description": description,
                },
            )
            existing_rooms.add(room_number)

        prop.rooms.exclude(room_number__in=existing_rooms).delete()

    print(f"Owner password for all seeded owners: {OWNER_PASSWORD}")
    print(f"Created {created_count} properties, updated {updated_count} properties.")
    print(f"Total Bangalore listings: {Property.objects.filter(city='Bangalore').count()}")


if __name__ == "__main__":
    populate()
