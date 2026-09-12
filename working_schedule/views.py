from rest_framework import generics

from working_schedule.models import WorkingSchedule
from working_schedule.serializers import WorkingScheduleSerializer


class WorkingScheduleList(generics.ListCreateAPIView):
    queryset = WorkingSchedule.objects.all()
    serializer_class = WorkingScheduleSerializer

# Create your views here.
