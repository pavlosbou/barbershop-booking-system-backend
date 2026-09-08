from django.db import models

from services.models import Service
from users.models import User
from barbers.models import Barber

# Create your models here.

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('CONFIRMED', 'Confirmed'),
    ('CANCELED', 'Canceled'),
    ('COMPLETED', 'Completed'),
]
class Appointment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    barber = models.ForeignKey(Barber, on_delete=models.PROTECT)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    start_time = models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES, default='PENDING', max_length=10)

    def __str__(self):
        return (
            f'{self.customer.first_name} {self.customer.last_name} has an appointment '
            f'for {self.service.name} with '
            f'{self.barber.user.first_name} {self.barber.user.last_name} '
            f'at {self.start_time} with status {self.get_status_display()}'
        )