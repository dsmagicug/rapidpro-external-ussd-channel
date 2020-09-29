from django.db import models
from core.utils import AuthSignature
from contacts.models import Contact
from handlers.models import Handler


# Create your models here.

class USSDChannel(AuthSignature):
    send_url = models.URLField(
        max_length=100
    )
    rapidpro_receive_url = models.URLField(
        max_length=100
    )
    timeout_after = models.IntegerField(
        default=10
    )
    trigger_word = models.CharField(
        max_length=20,
        default="USSD"
    )


#
class USSDSession(models.Model):
    session_id = models.CharField(
        max_length=30,
        unique=True
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.CASCADE
    )
    handler = models.ForeignKey(
        Handler,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        default='In Progress'
    )
    badge = models.CharField(
        max_length=15,
        default='info'
    )
    started_at = models.DateTimeField(
        auto_now_add=True
    )
    last_access_at = models.DateTimeField()
    ended_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.session_id
