from django.db import models
from core.utils import AuthSignature


class Handler(AuthSignature):
    aggregator = models.CharField(
        max_length=50
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

    def __str__(self):
        return self.aggregator
