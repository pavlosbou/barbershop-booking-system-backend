from django.http import Http404
from django.shortcuts import render
from datetime import datetime
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from appointment.serializers import AppointmentAvailabilitySerializer
from working_schedule.models import WorkingSchedule
from barbers.models import Barber
from barbers.serializers import BarberSerializer
from appointment.models import Appointment

# Create your views here.


class BarberList(generics.ListCreateAPIView):
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer


class BarberAvailability(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request,barber_id):

        try:
            barber = Barber.objects.get(id=barber_id)
        except Barber.DoesNotExist:
            raise Http404("Barber does not exist")

        date = request.query_params.get('date')
        if not date:
            raise serializers.ValidationError("You need to provide a date")

        try:
            date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            raise serializers.ValidationError("Invalid date. Use format: YYYY-MM-DD")

        working_schedule = WorkingSchedule.objects.filter(barber=barber, day_of_the_week=date.weekday()).first()

        if not working_schedule:
            return Response(
                {
                    "barber": {
                        "id": barber_id,
                        "First_name": barber.user.first_name,
                        "Last_name": barber.user.last_name,
                    },
                    'date': date.isoformat(),
                    'working_hours': None,
                    'appointments': [],
                },
                status=status.HTTP_200_OK,
            )

        appointments = Appointment.objects.filter(
            barber=barber,
            start_time__date=date,
            status__in=['PENDING','CONFIRMED'],
        )

        appointments_serializer = AppointmentAvailabilitySerializer(appointments, many=True)

        return Response(
            {
                "barber": {
                    "id": barber_id,
                    "first_name": barber.user.first_name,
                    "last_name": barber.user.last_name,
                },
                'date': date.isoformat(),
                'working_hours': {
                    "start_time": working_schedule.start_time.isoformat(),
                    "end_time": working_schedule.end_time.isoformat(),
                },
                'appointments': appointments_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


