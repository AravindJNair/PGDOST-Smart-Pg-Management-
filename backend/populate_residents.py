"""
populate_residents.py  —  PGDOST Rich Demo Data Generator
==========================================================
Creates per PG property:
  • 3 residents with approved bookings
  • 3 invoices each (mix of paid / unpaid)
  • 1-2 complaints with varied priority/status
  • 1-2 visitor log entries

Usage (from the backend/ directory, with venv activated):
    python populate_residents.py

Safe to re-run — skips users/invoices/tickets that already exist.
"""

import os
import sys
import django
import random
from datetime import date, timedelta, datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pgdost_backend.settings')
django.setup()

from django.utils import timezone
from accounts.models import CustomUser
from properties.models import Property, Room
from bookings.models import Booking
from payments.models import Invoice
from complaints.models import Ticket
from visitors.models import VisitorLog

# ─── 30 diverse resident profiles ────────────────────────────────────────────
RESIDENT_POOL = [
    # (username,        first,      last,       email,                          phone,        password)
    ("arjun_s",         "Arjun",    "Sharma",   "arjun.sharma@pgdost.demo",     "9876501001", "Resident@123"),
    ("priya_n",         "Priya",    "Nair",     "priya.nair@pgdost.demo",       "9876501002", "Resident@123"),
    ("rohan_v",         "Rohan",    "Verma",    "rohan.verma@pgdost.demo",      "9876501003", "Resident@123"),
    ("sneha_i",         "Sneha",    "Iyer",     "sneha.iyer@pgdost.demo",       "9876501004", "Resident@123"),
    ("kiran_m",         "Kiran",    "Mehta",    "kiran.mehta@pgdost.demo",      "9876501005", "Resident@123"),
    ("divya_p",         "Divya",    "Pillai",   "divya.pillai@pgdost.demo",     "9876501006", "Resident@123"),
    ("amit_k",          "Amit",     "Kumar",    "amit.kumar@pgdost.demo",       "9876501007", "Resident@123"),
    ("neha_g",          "Neha",     "Gupta",    "neha.gupta@pgdost.demo",       "9876501008", "Resident@123"),
    ("vikram_s",        "Vikram",   "Singh",    "vikram.singh@pgdost.demo",     "9876501009", "Resident@123"),
    ("ananya_r",        "Ananya",   "Reddy",    "ananya.reddy@pgdost.demo",     "9876501010", "Resident@123"),
    ("rahul_t",         "Rahul",    "Tiwari",   "rahul.tiwari@pgdost.demo",     "9876501011", "Resident@123"),
    ("pooja_b",         "Pooja",    "Bhatia",   "pooja.bhatia@pgdost.demo",     "9876501012", "Resident@123"),
    ("suresh_c",        "Suresh",   "Chavan",   "suresh.chavan@pgdost.demo",    "9876501013", "Resident@123"),
    ("lakshmi_d",       "Lakshmi",  "Das",      "lakshmi.das@pgdost.demo",      "9876501014", "Resident@123"),
    ("manoj_j",         "Manoj",    "Joshi",    "manoj.joshi@pgdost.demo",      "9876501015", "Resident@123"),
    ("gayatri_a",       "Gayatri",  "Akhil",    "gayatri.akhil@pgdost.demo",    "9876501016", "Resident@123"),
    ("deepak_w",        "Deepak",   "Wagh",     "deepak.wagh@pgdost.demo",      "9876501017", "Resident@123"),
    ("kavya_mn",        "Kavya",    "Menon",    "kavya.menon@pgdost.demo",      "9876501018", "Resident@123"),
    ("siddharth_r",     "Siddharth","Rao",      "siddharth.rao@pgdost.demo",    "9876501019", "Resident@123"),
    ("meera_k",         "Meera",    "Krishnan", "meera.krishnan@pgdost.demo",   "9876501020", "Resident@123"),
    ("aarav_p",         "Aarav",    "Patel",    "aarav.patel@pgdost.demo",      "9876501021", "Resident@123"),
    ("ritika_s",        "Ritika",   "Sinha",    "ritika.sinha@pgdost.demo",     "9876501022", "Resident@123"),
    ("yash_b",          "Yash",     "Bhatt",    "yash.bhatt@pgdost.demo",       "9876501023", "Resident@123"),
    ("nisha_a",         "Nisha",    "Agarwal",  "nisha.agarwal@pgdost.demo",    "9876501024", "Resident@123"),
    ("tarun_kh",        "Tarun",    "Khanna",   "tarun.khanna@pgdost.demo",     "9876501025", "Resident@123"),
    ("swati_m",         "Swati",    "Mishra",   "swati.mishra@pgdost.demo",     "9876501026", "Resident@123"),
    ("nikhil_d",        "Nikhil",   "Desai",    "nikhil.desai@pgdost.demo",     "9876501027", "Resident@123"),
    ("preeti_g",        "Preeti",   "George",   "preeti.george@pgdost.demo",    "9876501028", "Resident@123"),
    ("varun_s",         "Varun",    "Shah",     "varun.shah@pgdost.demo",       "9876501029", "Resident@123"),
    ("anjali_c",        "Anjali",   "Choudhary","anjali.choudhary@pgdost.demo", "9876501030", "Resident@123"),
]

RESIDENTS_PER_PG = 3

# ─── Complaint templates ──────────────────────────────────────────────────────
COMPLAINTS = [
    ("Leaking tap in bathroom", "The tap in my bathroom has been leaking continuously for 3 days.", "maintenance", "high",   "in_progress", "Plumber has been scheduled for this week."),
    ("Wi-Fi down since yesterday", "The Wi-Fi connection is very slow / not working in Room 201.", "maintenance", "urgent",  "pending",     ""),
    ("Dirty common area", "The hallway and staircase haven't been cleaned in over a week.", "cleanliness", "medium", "resolved",    "Cleaning staff has been informed. Issue resolved."),
    ("Noise from adjacent room", "Loud music from Room 105 every night past 11 PM.", "noise",       "high",   "pending",     ""),
    ("AC not cooling properly", "The AC in my room stops cooling after 1-2 hours of use.", "maintenance", "medium", "in_progress", "Technician will visit on Monday."),
    ("Water heater broken", "Hot water geyser has not been working for 5 days.", "maintenance", "urgent",  "resolved",    "Geyser replaced with new unit. Working fine now."),
    ("Billing discrepancy", "My invoice shows a higher amount than agreed in my contract.", "billing",     "medium", "pending",     ""),
    ("Security camera not working", "The camera at the main gate entrance seems to be offline.", "security",    "high",   "in_progress", "Security vendor has been notified."),
    ("Bed mattress worn out", "The mattress in my room is very uncomfortable and sagging.", "maintenance", "low",    "pending",     ""),
    ("Dustbin overflowing", "The dustbin near Room 204 area has not been emptied in 3 days.", "cleanliness", "medium", "resolved",    "Cleaned and new schedule set."),
    ("Room lock is broken", "My room's door lock is faulty and doesn't latch properly.", "security",    "urgent",  "in_progress", "New lock being procured. Temporary fix applied."),
    ("Cockroach infestation", "Found cockroaches near the kitchen area. Needs pest control.", "cleanliness", "high",   "pending",     ""),
]

# ─── Visitor name templates ───────────────────────────────────────────────────
VISITORS = [
    ("Rajesh Sharma",  "9900001111", "personal",  True),
    ("Sunita Nair",    "9900002222", "personal",  True),
    ("Amazon Delivery","",           "delivery",  True),
    ("Ravi Mehta",     "9900003333", "official",  False),
    ("Flipkart Parcel","",           "delivery",  True),
    ("Preethi Rao",    "9900004444", "personal",  True),
    ("ICICI Bank Rep", "9900005555", "official",  True),
    ("Ramesh Kumar",   "9900006666", "personal",  False),
    ("Zomato Delivery","",           "delivery",  True),
    ("Dr. Anand Pillai","9900007777","other",     True),
]


def get_or_create_resident(profile, suffix=""):
    username, first, last, email, phone, password = profile
    if suffix:
        username = f"{username}{suffix}"
    if CustomUser.objects.filter(username=username).exists():
        return CustomUser.objects.get(username=username), False
    user = CustomUser.objects.create_user(
        username=username,
        email=email.replace("@", f"{suffix}@") if suffix else email,
        password=password,
        role='resident',
        first_name=first,
        last_name=last,
        phone_number=phone,
    )
    return user, True


def create_invoices_for_resident(resident, prop, room_rent):
    """Create 3 months of invoices: 2 paid, 1 unpaid."""
    today = date.today()
    created = 0
    months = [
        (today.month - 2 if today.month > 2 else today.month + 10,  today.year if today.month > 2 else today.year - 1, 'paid'),
        (today.month - 1 if today.month > 1 else 12,                 today.year if today.month > 1 else today.year - 1, 'paid'),
        (today.month,                                                  today.year,                                         'unpaid'),
    ]
    for month, year, status in months:
        if Invoice.objects.filter(resident=resident, property=prop, month=month, year=year).exists():
            continue
        inv = Invoice(
            resident=resident,
            property=prop,
            amount=room_rent,
            month=month,
            year=year,
            due_date=date(year, month, 5),
            status=status,
            notes="Monthly rent",
        )
        if status == 'paid':
            inv.payment_date = timezone.make_aware(datetime(year, month, random.randint(1, 4), 10, 0))
            inv.transaction_id = f"UPI{random.randint(100000000, 999999999)}"
        inv.save()
        created += 1
    return created


def create_complaint_for_resident(resident, prop, complaint_data):
    title, desc, category, priority, status, owner_response = complaint_data
    if Ticket.objects.filter(raised_by=resident, property=prop, title=title).exists():
        return False
    Ticket.objects.create(
        raised_by=resident,
        property=prop,
        title=title,
        description=desc,
        category=category,
        priority=priority,
        status=status,
        owner_response=owner_response,
    )
    return True


def create_visitor_for_resident(resident, prop, owner, visitor_data):
    visitor_name, visitor_phone, purpose, checked_out = visitor_data
    # Avoid exact duplicates
    if VisitorLog.objects.filter(resident=resident, visitor_name=visitor_name, property=prop).exists():
        return False
    past_days = random.randint(1, 30)
    check_in = timezone.now() - timedelta(days=past_days, hours=random.randint(0, 6))
    check_out = check_in + timedelta(hours=random.randint(1, 4)) if checked_out else None
    VisitorLog.objects.create(
        property=prop,
        resident=resident,
        visitor_name=visitor_name,
        visitor_phone=visitor_phone,
        purpose=purpose,
        check_in=check_in,
        check_out=check_out,
        logged_by=owner,
    )
    return True


def main():
    properties = list(Property.objects.all().order_by('id'))
    if not properties:
        print("\n  ERROR: No properties in the database!")
        print("  Add at least one property via the owner dashboard first.")
        sys.exit(1)

    print(f"\n  Found {len(properties)} propert{'y' if len(properties)==1 else 'ies'}.\n")
    print("=" * 90)

    created_accounts = []
    total_invoices = 0
    total_tickets = 0
    total_visitors = 0
    pool_idx = 0

    for prop in properties:
        owner = prop.owner
        rooms = list(Room.objects.filter(property=prop))
        default_rent = rooms[0].rent_per_month if rooms else 8000

        print(f"  +-- [{prop.id}] {prop.name}  (owner: {owner.username})")

        for slot in range(RESIDENTS_PER_PG):
            profile = RESIDENT_POOL[pool_idx % len(RESIDENT_POOL)]
            pool_idx += 1

            # Suffix to avoid username collisions across multiple PGs
            suffix = f"_p{prop.id}" if slot >= len(RESIDENT_POOL) else ""
            user, is_new = get_or_create_resident(profile, suffix if pool_idx > len(RESIDENT_POOL) else "")

            status_label = "created" if is_new else "exists "

            # Booking
            booking_qs = Booking.objects.filter(resident=user, property=prop, status='approved')
            if booking_qs.exists():
                booking = booking_qs.first()
            else:
                room = rooms[slot % len(rooms)] if rooms else None
                booking = Booking.objects.create(
                    resident=user,
                    property=prop,
                    room=room,
                    status='approved',
                    move_in_date=(date.today() - timedelta(days=random.randint(30, 180))),
                    message="Added by populate script.",
                )
                if room and room.available_beds > 0:
                    room.available_beds -= 1
                    room.save()

            # Invoices
            inv_count = create_invoices_for_resident(user, prop, float(default_rent))
            total_invoices += inv_count

            # Complaints (assign 1 per resident, rotating through list)
            comp_data = COMPLAINTS[(pool_idx - 1) % len(COMPLAINTS)]
            if create_complaint_for_resident(user, prop, comp_data):
                total_tickets += 1

            # Second complaint for every 2nd resident
            if slot % 2 == 1:
                comp_data2 = COMPLAINTS[(pool_idx) % len(COMPLAINTS)]
                if create_complaint_for_resident(user, prop, comp_data2):
                    total_tickets += 1

            # Visitor log (1-2 per resident)
            vis_data = VISITORS[(pool_idx - 1) % len(VISITORS)]
            if create_visitor_for_resident(user, prop, owner, vis_data):
                total_visitors += 1
            if slot % 2 == 0:
                vis_data2 = VISITORS[pool_idx % len(VISITORS)]
                if create_visitor_for_resident(user, prop, owner, vis_data2):
                    total_visitors += 1

            created_accounts.append((prop.name, user.username, "Resident@123", user.email, status_label))
            print(f"  |  [{status_label}] {user.username:20s}  booking#{booking.id}  invoices+{inv_count}")

        print("  |")

    print("=" * 90)
    print("  RESIDENT CREDENTIALS SUMMARY")
    print("=" * 90)
    print(f"  {'PG Name':<35} {'Username':<22} {'Status':<10} Email")
    print("  " + "-" * 86)
    for pg_name, username, pwd, email, status_label in created_accounts:
        print(f"  {pg_name:<35} {username:<22} {status_label:<10} {email}")
    print("=" * 90)
    print(f"\n  [OK] Residents processed : {len(created_accounts)}")
    print(f"  [OK] Invoices created    : {total_invoices}")
    print(f"  [OK] Complaints created  : {total_tickets}")
    print(f"  [OK] Visitor logs created: {total_visitors}")
    print(f"\n  All residents use password: Resident@123\n")


if __name__ == '__main__':
    main()
