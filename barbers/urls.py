from django.urls import path
from .views import BarberList

urlpatterns = [
    path('', BarberList.as_view()),
]