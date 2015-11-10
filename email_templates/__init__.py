# -*- encoding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.db import models
from django.template import loader, Context
from django.utils.translation import ugettext as _

from estate_ads import settings
from django.contrib.sites.models import Site


def _subst(s, **subst):
        t = loader.get_template_from_string(s)
        c = Context(subst)
        return t.render(c)


def send_mail(subject, body, _from=None, to=[], fail_silently=True, **kw):
    if _from is None:
        _from = settings.DEFAULT_FROM_EMAIL
    to.append('aleksey.stryukov@gmail.com')
    if 'site' not in kw:
        current_site = Site.objects.get_current()
        kw['site'] = current_site

    subj = _subst(subject, **kw)
    text_body = _subst(body, **kw)
    content = _subst(body, **kw)
    kw['content'] = content
    html_body = loader.render_to_string('email_templates/base_template.html', kw)

    connection = get_connection(fail_silently=fail_silently)
    email = EmailMultiAlternatives(subject=subj, body=text_body, from_email=_from, to=list(to), connection=connection)
    email.attach_alternative(html_body, "text/html")
    return email.send()