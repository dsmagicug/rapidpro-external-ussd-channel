from django.db import models
from core.utils import AuthSignature
from countries_plus.models import Country
from django.utils.safestring import mark_safe

DEFAULT_COUNTRY = "UG"


# Create your models here.

class USSDChannel(AuthSignature):
    channel_name = models.CharField(
        max_length=100
    )
    send_url = models.URLField(
        max_length=100
    )
    rapidpro_receive_url = models.URLField(
        max_length=100
    )
    timeout_after = models.IntegerField(
        default=10
    )
    country = models.ForeignKey(
        Country,
        help_text=mark_safe("<pre style='font-size:8pt;color:#757575'>The country this channel is in.(Important for "
                            "standard phone contacts)<pre>"),
        on_delete=models.CASCADE,
        default=DEFAULT_COUNTRY
    )

    def __str__(self):
        return self.channel_name

