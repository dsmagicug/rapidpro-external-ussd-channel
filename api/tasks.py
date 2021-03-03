from celery import shared_task
from channel.models import USSDSession
from handlers.models import Handler
from datetime import datetime, timedelta
from django.utils import timezone


@shared_task
def clear_timed_out_sessions():
    timed_out_sessions = USSDSession.objects.filter(status="Timed Out")
    if len(timed_out_sessions) > 0:
        '''
            We are not deleting these sessions since this will restart the contact from the beginning of the flow
            so we just change them to In Progress so we can pick from the previous step.
        '''
        for session in timed_out_sessions:
            session.status = "In Progress"
            session.save()
        return "Timed-out sessions cleared"
    return True


@shared_task
def expire_contacts_on_idle_handler():
    """
    This task uses if handler's set expire_on_inactivity_of (seconds) to determine in activity
    and expire all contacts from their flows,
    NOTE that this only works if, during flow creation (attached to this handler) in rapidPro, the "Ignore triggers"
    checkbox is not checked.
    """
    time_now = timezone.now()
    handlers = Handler.objects.all()
    if len(handlers) > 0:
        for handler in handlers:
            last_accessed_at = handler.last_accessed_at
            time_threshold = last_accessed_at + timedelta(seconds=handler.expire_on_inactivity_of)
            if time_now > time_threshold:
                # get all session attached to this handler and delete them
                sessions = USSDSession.objects.filter(handler=handler)
                # delete them
                sessions.delete()
    return True
