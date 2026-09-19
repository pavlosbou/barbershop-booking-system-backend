from django.test import TestCase
from datetime import time

from rest_framework import status
from rest_framework.test import APIClient

import appointment
from users.models import User
from barbers.models import Barber
from services.models import Service
from working_schedule.models import  WorkingSchedule
from appointment.models import Appointment


# Create your tests here.

class BarberAvailabilityTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.customer = User.objects.create_user(
            email='customer@test.com',
            password='password123',
            first_name='John',
            last_name='Doe',
            phone_number='6912345678'
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

        self.schedule = WorkingSchedule.objects.create(
            barber=self.barber,
            day_of_the_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0),
        )

        self.appointment = Appointment.objects.create(
            customer=self.customer,
            barber=self.barber,
            service=self.service,
            start_time='2026-09-21T12:00:00+03:00',
            status='PENDING'
        )

    def test_barber_availability(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/?date=2026-09-21',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)

    def test_barber_availability_with_invalid_date(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/?date=hello',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_barber_availability_without_date(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_barber_availability_with_invalid_barber_id(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/barbers/225/availability/?date=2026-09-21',
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_barber_availability_with_date_not_in_schedule(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/?date=2026-09-20',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)

    def test_barber_availability_confirmed_appointment(self):
        self.client.force_authenticate(user=self.barber_user)

        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status': 'CONFIRMED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.customer)
        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/?date=2026-09-21',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)

    def test_barber_availability_cancelled_appointment(self):
        self.client.force_authenticate(user=self.customer)
        print(self.appointment)
        response = self.client.patch(
            f'/api/appointment/{self.appointment.id}/status/',
            {'status': 'CANCELED'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(
            f'/api/barbers/{self.barber.id}/availability/?date=2026-09-21',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(response.data)