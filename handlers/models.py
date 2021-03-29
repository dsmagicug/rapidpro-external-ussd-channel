from django.db import models
from core.utils import AuthSignature
from django.utils import timezone
from contacts.models import Contact
from channel.models import USSDChannel


class Handler(AuthSignature):
    aggregator = models.CharField(
        max_length=50
    )
    channel = models.ForeignKey(
        USSDChannel, on_delete=models.CASCADE
    )
    short_code = models.CharField(
        max_length=10,
        unique=True
    )
    request_format = models.TextField()
    response_content_type = models.CharField(
        max_length=10,
        default='json'
    )
    response_method = models.CharField(
        max_length=15,
        default='POST'
    )
    response_format = models.IntegerField(
        default=1
    )
    response_structure = models.TextField()
    signal_reply_string = models.CharField(
        max_length=15
    )
    signal_end_string = models.CharField(
        max_length=10
    )
    push_support = models.BooleanField(
        default=False
    )
    push_url = models.URLField(
        null=True, blank=True
    )
    NONE = "NONE"
    TOKEN = "TOKEN"
    BASIC = "BASIC"

    AUTH_SCHEMES = [
        (NONE, "NONE"),
        (TOKEN, "TOKEN")
    ]
    auth_scheme = models.CharField(max_length=30, default=TOKEN)

    trigger_word = models.CharField(max_length=50, default="USSD")
    repeat_trigger = models.CharField(
        max_length=20,
        default=" "
    )
    expire_on_inactivity_of = models.IntegerField(default=300)  # 5 minutes
    last_accessed_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return self.aggregator


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
    last_access_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.session_id
