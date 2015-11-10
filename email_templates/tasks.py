from djcelery import celery
from models import EmailTemplate
from django.contrib.auth import get_user_model


@celery.task
def send_email_to_all(eid):

    email = EmailTemplate.objects.get(pk=eid.replace('_5F', '_'))
    for user in get_user_model().objects.all():
        if user.is_active:
            email.send(user.email)