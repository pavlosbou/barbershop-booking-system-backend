from django.db import models

from barbers.models import Barber


# Create your models here.

DAYS_OF_WEEK = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

class WorkingSchedule(models.Model):
    barber = models.ForeignKey(Barber, on_delete=models.CASCADE)
    day_of_the_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    def __str__(self):
        return f'{self.barber.user.first_name} {self.barber.user.last_name} - {self.get_day_of_the_week_display()} : {self.start_time} - {self.end_time}'
