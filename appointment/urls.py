from django.urls import path
from .views import AppointmentList

urlpatterns = [
    path('', AppointmentList.as_view()),
]