from django.urls import path
from .views import AppointmentList, AppointmentStatusUpdate, AppointmentDetail

urlpatterns = [
    path('', AppointmentList.as_view()),
    path('<int:pk>/status/',AppointmentStatusUpdate.as_view()),
    path('<int:pk>/',AppointmentDetail.as_view()),
]