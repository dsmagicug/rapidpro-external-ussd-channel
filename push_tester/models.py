from django.db import models
from django.utils import timezone


# Create your models here.
class Tester(models.Model):
    msisdn = models.CharField(max_length=20, unique=True)
    device_unique_id = models.CharField(max_length=50)
    registered_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.msisdn

