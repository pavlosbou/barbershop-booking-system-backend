from django.urls import path
from .views import BarberList, BarberAvailability

urlpatterns = [
    path('', BarberList.as_view()),
    path('<int:barber_id>/availability/',BarberAvailability.as_view(), name='barber-availability'),
]