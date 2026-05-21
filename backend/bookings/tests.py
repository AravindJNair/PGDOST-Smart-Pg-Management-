from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import CustomUser
from properties.models import Property, Room
from .models import Booking


class OwnerBookingUpdateViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = CustomUser.objects.create_user(
            username='owner1',
            email='owner1@example.com',
            password='pass12345',
            role='owner',
        )
        self.resident = CustomUser.objects.create_user(
            username='resident1',
            email='resident1@example.com',
            password='pass12345',
            role='resident',
        )
        self.property = Property.objects.create(
            owner=self.owner,
            name='Test PG',
            address='123 Street',
            city='Bengaluru',
            state='Karnataka',
            pincode='560001',
            is_approved=True,
        )

    def _booking_update_url(self, booking_id):
        return f'/api/bookings/owner/{booking_id}/update/'

    def test_repeated_approve_does_not_decrement_beds_twice(self):
        room = Room.objects.create(
            property=self.property,
            room_number='101',
            total_beds=2,
            available_beds=2,
            rent_per_month=10000,
        )
        booking = Booking.objects.create(
            resident=self.resident,
            property=self.property,
            status='pending',
        )
        self.client.force_authenticate(user=self.owner)

        first = self.client.patch(
            self._booking_update_url(booking.id),
            {'status': 'approved', 'room': room.id},
            format='json',
        )
        self.assertEqual(first.status_code, 200)
        room.refresh_from_db()
        self.assertEqual(room.available_beds, 1)

        second = self.client.patch(
            self._booking_update_url(booking.id),
            {'status': 'approved', 'room': room.id, 'owner_note': 'Still approved'},
            format='json',
        )
        self.assertEqual(second.status_code, 200)
        room.refresh_from_db()
        self.assertEqual(room.available_beds, 1)

    def test_cannot_approve_when_room_has_no_available_beds(self):
        room = Room.objects.create(
            property=self.property,
            room_number='102',
            total_beds=1,
            available_beds=0,
            rent_per_month=9000,
        )
        booking = Booking.objects.create(
            resident=self.resident,
            property=self.property,
            status='pending',
        )
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self._booking_update_url(booking.id),
            {'status': 'approved', 'room': room.id},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        booking.refresh_from_db()
        room.refresh_from_db()
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(room.available_beds, 0)
