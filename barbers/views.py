from django.shortcuts import render
from rest_framework import generics

from barbers.models import Barber
from barbers.serializers import BarberSerializer


# Create your views here.


class BarberList(generics.ListCreateAPIView):
    queryset = Barber.objects.all()
    serializer_class = BarberSerializer