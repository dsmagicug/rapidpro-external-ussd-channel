from celery import shared_task
from channel.models import USSDSession


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
