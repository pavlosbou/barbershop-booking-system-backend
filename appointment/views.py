from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from appointment.models import Appointment
from barbers.models import Barber
from appointment.serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if Barber.objects.filter(user=self.request.user).exists():
            barber = Barber.objects.get(user=self.request.user)
            return Appointment.objects.filter(barber=barber)

        return Appointment.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):

        if Barber.objects.filter(user=self.request.user).exists():
            serializer.save()
        else:
            customer = serializer.validated_data.get('customer')

            if customer and self.request.user != customer:
                raise serializers.ValidationError({'detail': 'You can create appointments only for yourself'})

            serializer.save(customer=self.request.user)


class AppointmentStatusUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusSerializer

class AppointmentDetail(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        if Barber.objects.filter(user=self.request.user).exists():
            return Appointment.objects.filter(barber__user=self.request.user)
        return Appointment.objects.filter(customer=self.request.user)