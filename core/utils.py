from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import threading
from logzero import setup_logger
import logging

# logging
log_folder = f"{settings.BASE_DIR}/logs"
access_logger = setup_logger(name="debugger_logger", logfile=f"{log_folder}/access.log", backupCount=10,
                               level=logging.INFO)
error_logger = setup_logger(name="error_logger", logfile=f"{log_folder}/error.log", backupCount=10,
                            level=logging.DEBUG)

_thread_locals = threading.local()


def set_current_user(user):
    _thread_locals.user = user


def get_current_user():
    return getattr(_thread_locals, 'user', None)


def remove_current_user():
    _thread_locals.user = None


class AuthSignature(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, editable=False,
                                   related_name='%(class)s_created')
    modified_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, editable=False,
                                    related_name='%(class)s_modified')
    created_on = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_on = models.DateTimeField(auto_now=True, db_index=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.modified_by = user
            if not self.id:
                self.created_by = user
        super(AuthSignature, self).save(*args, **kwargs)

    class Meta:
        abstract = True
