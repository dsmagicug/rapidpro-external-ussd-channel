from django.db import models
from django.utils import timezone


# Create your models here.

class Msg(models.Model):
    msg_type = models.CharField(max_length=10)
    msg_body = models.TextField()
    status = models.CharField(max_length=20)
    contact = models.CharField(max_length=50)
    sender = models.CharField(max_length=50)
    receiver = models.CharField(max_length=50)
    sent_on = models.DateTimeField(default=timezone.now)
