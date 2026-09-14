from rest_framework import generics, permissions, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from appointment.models import Appointment
from appointment.serializers import AppointmentSerializer, AppointmentStatusSerializer


class AppointmentList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(customer=self.request.user)

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class AppointmentStatusUpdate(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Appointment.objects.all()
    serializer_class = AppointmentStatusSerializer

    def update(self, request, *args, **kwargs):
        appointment = self.get_object()
        new_status = request.data.get('status')

        is_customer = appointment.customer == self.request.user
        is_barber = appointment.barber.user == self.request.user

        if is_customer and new_status != 'CANCELED':
            raise serializers.ValidationError({'status': "Unacceptable status provided!"})

        if not is_barber and not is_customer:
            raise PermissionDenied({'status': "You cannot modify the appointment!"})

        if is_barber and new_status == 'PENDING':
            raise serializers.ValidationError({'status': "Appointment cannot be updated to pending!"})

        appointment.status = new_status

        serializer = self.get_serializer(appointment,data={'status':new_status},partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)