from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from bookings.models import Booking
from properties.models import Property
from visitors.models import VisitorLog


User = get_user_model()


class VisitorApprovalWorkflowTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username='owner1',
            password='OwnerPass123!',
            role='owner',
            email='owner@example.com',
        )
        self.resident = User.objects.create_user(
            username='resident1',
            password='ResidentPass123!',
            role='resident',
            email='resident@example.com',
        )
        self.property = Property.objects.create(
            owner=self.owner,
            name='Green Nest PG',
            description='Test',
            property_type='pg',
            address='MG Road',
            city='Bengaluru',
            state='Karnataka',
            pincode='560001',
            is_approved=True,
        )
        Booking.objects.create(
            resident=self.resident,
            property=self.property,
            status='approved',
            move_in_date=timezone.now().date(),
        )
        self.request_payload = {
            'property': self.property.id,
            'visitor_name': 'Anita Rao',
            'visitor_phone': '9876543210',
            'purpose': 'personal',
            'requested_check_in': (timezone.now() + timedelta(hours=3)).isoformat(),
            'requested_check_out': (timezone.now() + timedelta(hours=6)).isoformat(),
            'notes': 'Family visit',
        }

    def test_approved_request_creates_visitor_log(self):
        self.client.force_authenticate(user=self.resident)
        create_res = self.client.post('/api/visitors/requests/my/', self.request_payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_res.data['status'], 'pending')
        req_id = create_res.data['id']

        self.client.force_authenticate(user=self.owner)
        pre_logs = self.client.get('/api/visitors/owner/')
        self.assertEqual(pre_logs.status_code, status.HTTP_200_OK)
        self.assertEqual(len(pre_logs.data), 0)

        review_res = self.client.patch(
            f'/api/visitors/requests/owner/{req_id}/review/',
            {'status': 'approved', 'owner_note': 'Allowed till 8 PM'},
            format='json',
        )
        self.assertEqual(review_res.status_code, status.HTTP_200_OK)
        self.assertEqual(review_res.data['status'], 'approved')

        owner_logs = self.client.get('/api/visitors/owner/')
        self.assertEqual(owner_logs.status_code, status.HTTP_200_OK)
        self.assertEqual(len(owner_logs.data), 1)
        self.assertIsNotNone(owner_logs.data[0]['check_out'])

        self.client.force_authenticate(user=self.resident)
        resident_logs = self.client.get('/api/visitors/my/')
        self.assertEqual(resident_logs.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resident_logs.data), 1)
        self.assertEqual(VisitorLog.objects.count(), 1)

    def test_rejected_request_does_not_create_visitor_log(self):
        self.client.force_authenticate(user=self.resident)
        create_res = self.client.post('/api/visitors/requests/my/', self.request_payload, format='json')
        req_id = create_res.data['id']

        self.client.force_authenticate(user=self.owner)
        review_res = self.client.patch(
            f'/api/visitors/requests/owner/{req_id}/review/',
            {'status': 'rejected', 'owner_note': 'Not permitted on this date'},
            format='json',
        )
        self.assertEqual(review_res.status_code, status.HTTP_200_OK)
        self.assertEqual(review_res.data['status'], 'rejected')
        self.assertEqual(VisitorLog.objects.count(), 0)

    def test_request_requires_expected_checkout(self):
        self.client.force_authenticate(user=self.resident)
        payload = dict(self.request_payload)
        payload.pop('requested_check_out')
        create_res = self.client.post('/api/visitors/requests/my/', payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('requested_check_out', create_res.data)

    def test_request_rejects_invalid_visit_window(self):
        self.client.force_authenticate(user=self.resident)
        payload = dict(self.request_payload)
        payload['requested_check_out'] = payload['requested_check_in']
        create_res = self.client.post('/api/visitors/requests/my/', payload, format='json')
        self.assertEqual(create_res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('requested_check_out', create_res.data)
