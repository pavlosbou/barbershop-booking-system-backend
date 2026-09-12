from rest_framework import serializers
from .models import WorkingSchedule

class WorkingScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingSchedule
        fields = '__all__'