from rest_framework import serializers
from datetime import timedelta

import appointment
from appointment.models import Appointment
from barbers.models import Barber
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
        existing_appointments = Appointment.objects.filter(barber=barber)


        for existing_appointment in existing_appointments:
            existing_end_time = existing_appointment.start_time + timedelta(minutes=existing_appointment.service.duration)

            if existing_appointment.start_time < end_time_to_compare and existing_end_time > start_time:
                raise serializers.ValidationError('The barber already has an appointment at this time!')



        return attrs

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ('customer', 'status')


class AppointmentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ('status',)