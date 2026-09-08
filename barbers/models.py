from django.db import models

from services.models import Service
from users.models import User


# Create your models here.

class Barber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    services = models.ManyToManyField(Service, blank=True)
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'