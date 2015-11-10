from django.core.mail import send_mail
from django.conf import settings

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        send_mail('Test Email', "Test Email", settings.DEFAULT_FROM_EMAIL, [admin[1] for admin in settings.ADMINS])