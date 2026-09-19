from rest_framework import serializers
from datetime import timedelta
from django.utils import timezone

from rest_framework.exceptions import PermissionDenied

import appointment
from appointment.models import Appointment
from barbers.models import Barber
from services.serializers import AppointmentAvailabilityServiceSerializer
from working_schedule.models import WorkingSchedule


class AppointmentSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        barber = attrs['barber']
        service = attrs['service']

        if not barber.services.filter(id=service.id).exists():
            raise serializers.ValidationError('Barber does not provide this service')

        start_time = attrs['start_time']
        day = start_time.weekday()
        time = start_time.time()

        schedule = WorkingSchedule.objects.filter(
            barber=barber,
            day_of_the_week=day,
        ).first()

        end_time = start_time + timedelta(minutes=service.duration)
        end_time = end_time.time()

        if not schedule:
            raise serializers.ValidationError('Barber does not work this day!')

        if time < schedule.start_time or end_time > schedule.end_time:
            raise serializers.ValidationError('The appointment time is out of the schedule!')


        end_time_to_compare = start_time + timedelta(minutes=service.duration)
        existing_appointments = Appointment.objects.filter(
            barber=barber,
            status__in=['PENDING', 'CONFIRMED'],
        )


        for existing_appointment in existing_appointments:
            existing_end_time = existing_appointment.start_time + timedelta(minutes=existing_appointment.service.duration)

            if existing_appointment.start_time < end_time_to_compare and existing_end_time > start_time:
                raise serializers.ValidationError('The barber already has an appointment at this time!')



        return attrs

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('status',)
        extra_kwargs = {
            'customer': {'required': False},
        }


class AppointmentStatusSerializer(serializers.ModelSerializer):

    def validate_status(self, status):

        current_status = self.instance.status

        if current_status == 'PENDING':
            if status != 'CONFIRMED' and status != 'CANCELED':
                raise serializers.ValidationError('A pending appointment can only be confirmed or canceled')

        if current_status == 'COMPLETED':
            if status == 'CANCELED':
                raise serializers.ValidationError('A completed appointment cannot be canceled')

        if current_status == 'CANCELED':
            if status == 'CONFIRMED':
                raise serializers.ValidationError('A canceled appointment cannot be confirmed')

        return status

    def validate(self, attrs):
        appointment = self.instance
        user = self.context['request'].user
        new_status = attrs.get('status')

        is_customer = appointment.customer == user
        is_barber = appointment.barber.user == user

        if not is_customer and not is_barber:
            raise PermissionDenied({'status': "You cannot modify the appointment!"})

        if is_customer and new_status != 'CANCELED':
            raise serializers.ValidationError('You can only cancel this appointment')

        return attrs

    class Meta:
        model = Appointment
        fields = ('status',)


class AppointmentAvailabilitySerializer(serializers.ModelSerializer):
    end_time = serializers.SerializerMethodField()
    service =  AppointmentAvailabilityServiceSerializer(read_only=True)

    def get_end_time(self, obj):
        end_time = obj.start_time + timedelta(minutes=obj.service.duration)

        return timezone.localtime(end_time).isoformat()


    class Meta:
        model = Appointment
        fields = ('id','start_time', 'end_time', 'service')