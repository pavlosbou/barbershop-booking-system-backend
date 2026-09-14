from datetime import datetime, time, timedelta

from rest_framework import status
from rest_framework.test import APIClient

from django.test import TestCase
from django.utils import timezone

from .models import Appointment
from .serializers import AppointmentSerializer
from barbers.models import Barber
from services.models import Service
from users.models import User
from working_schedule.models import WorkingSchedule

class AppointmentSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='test1234',
            first_name='John',
            last_name='Doe',
            phone_number='+30 5555555555',
        )

        self.service = Service.objects.create(
            name='Test Service',
            description='Test Service',
            price=15.00,
            duration=30,
        )

        self.barber = Barber.objects.create(
            user=self.user,
        )

        self.barber.services.add(self.service)

        self.schedule = WorkingSchedule.objects.create(
            barber=self.barber,
            day_of_the_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

    def test_valid_appointment_time(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T12:00:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_before_working_hours(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T08:00:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_after_working_hours(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T19:00:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_appointment_on_non_working_day(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-15T12:00:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_appointment_fits_schedule_end_time(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T16:00:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertTrue(serializer.is_valid())

    def test_appointment_does_not_fits_schedule_end_time(self):
        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T16:55:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_overlapping_appointments(self):
        Appointment.objects.create(
            customer=self.user,
            barber=self.barber,
            service=self.service,
            start_time='2026-09-21T12:00:00+03:00',
            status='PENDING'
        )

        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T12:05:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)

        self.assertFalse(serializer.is_valid())

    def test_appointment_can_start_when_previous_ends(self):
        Appointment.objects.create(
            customer=self.user,
            barber=self.barber,
            service=self.service,
            start_time='2026-09-21T12:00:00+03:00',
            status='PENDING'
        )

        data = {
            'barber': self.barber.id,
            'service': self.service.id,
            'start_time': '2026-09-21T12:30:00+03:00'
        }

        serializer = AppointmentSerializer(data=data)
        self.assertTrue(serializer.is_valid())


class AppointmentStatusTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            email='customer@test.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            phone_number='6912345678'
        )

        self.other_customer = User.objects.create_user(
            email='other@test.com',
            password='password123',
            first_name='Jane',
            last_name='Doe',
            phone_number='6912345679'
        )

        self.barber_user = User.objects.create_user(
            email='barber@test.com',
            password='password123',
            first_name='Mike',
            last_name='Barber',
            phone_number='6912345680'
        )

        self.barber = Barber.objects.create(
            user=self.barber_user,
        )

        self.service = Service.objects.create(
            name='Haircut',
            price=15.00,
            duration=30,
        )

        self.barber.services.add(self.service)

        self.appointment = Appointment.objects.create(
            customer=self.customer,
            barber=self.barber,
            service=self.service,
            start_time='2026-09-21T12:00:00+03:00',
            status='PENDING'
        )

    def test_customer_can_cancel_appointment(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'CANCELED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.appointment.refresh_from_db()

        self.assertEqual(self.appointment.status, 'CANCELED')

    def test_customer_cannot_confirm_appointment(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'CONFIRMED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'PENDING')

    def test_other_customer_cannot_confirm_appointment(self):
        self.client.force_authenticate(user=self.other_customer)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'CONFIRMED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.other_customer.refresh_from_db()
        self.assertEqual(self.appointment.status, 'PENDING')

    def test_barber_can_confirm_appointment(self):
        self.client.force_authenticate(user=self.barber_user)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'CONFIRMED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'CONFIRMED')

    def test_barber_can_complete_appointment(self):
        self.client.force_authenticate(user=self.barber_user)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'COMPLETED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'COMPLETED')

    def test_barber_cannot_set_appointment_to_pending(self):
        self.client.force_authenticate(user=self.barber_user)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status':'PENDING'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, 'PENDING')