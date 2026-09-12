from django.urls import path
from .views import WorkingScheduleList

urlpatterns = [
    path('', WorkingScheduleList.as_view()),
]