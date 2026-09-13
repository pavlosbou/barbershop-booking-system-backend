from rest_framework import generics, permissions

from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer


class AppointmentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)

