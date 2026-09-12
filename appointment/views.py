from rest_framework import generics

from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer


class AppointmentList(generics.ListCreateAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer


