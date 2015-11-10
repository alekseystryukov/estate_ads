from django.core.mail import EmailMessage
from estate_ads import settings

INBOXES = {
    'gmail': 'https://mail.google.com/',
    'yandex': 'https://mail.yandex.com/',
    'rambler': 'https://mail.rambler.com/',
    'yahoo': 'https://mail.yahoo.com/',
    'outlook': 'https://mail.live.com/',
    'mail': 'https://e.mail.ru/messages/inbox/',
}
INBOXES['ymail'] = INBOXES['yahoo']
INBOXES['hotmail'] = INBOXES['live'] = INBOXES['outlook']


def get_mailbox_by_email(email):
    email = email[email.index('@')+1:]
    if email.find('.'):
        email = email[:email.index('.')]
    try:
        return INBOXES[email]
    except KeyError:
        return None


def send_log(text):
    email = EmailMessage('log',  text, to=[admin[1] for admin in settings.ADMINS])
    email.send()

