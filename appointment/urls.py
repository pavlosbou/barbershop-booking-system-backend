from django.urls import path
from .views import AppointmentList, AppointmentStatusUpdate

urlpatterns = [
    path('', AppointmentList.as_view()),
    path('<int:pk>/status/',AppointmentStatusUpdate.as_view()),
]