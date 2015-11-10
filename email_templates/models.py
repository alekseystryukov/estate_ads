# -*- encoding: utf-8 -*-

from django.core.mail import EmailMultiAlternatives
from django.core.mail import get_connection
from django.db import models
from django.template import loader, Context
from django.utils.translation import ugettext as _

from estate_ads import settings
from django.contrib.sites.models import Site


class EmailTemplate(models.Model):
    """
    e-mail template
    """

    uid = models.CharField(max_length=50, primary_key=True)
    desc = models.CharField(max_length=200)

    subject = models.CharField(max_length=200)
    html = models.TextField()
    text = models.TextField()

    class Meta:
        verbose_name = _("Mail template")
        verbose_name_plural = _("Mail templates")
        
    def __unicode__(self):
        return self.desc

    def _subst(self, s, **subst):
        t = loader.get_template_from_string(s)
        c = Context(subst)
        return t.render(c)

    def send(self, to, _from=None, subject=None, **kw):

        if _from is None:
            _from = settings.DEFAULT_FROM_EMAIL

        if 'site' not in kw:
            current_site = Site.objects.get_current()
            kw['site'] = current_site

        subj = self._subst((subject or self.subject), **kw)
        text_body = self._subst(self.text, **kw)
        content = self._subst(self.html, **kw)
        kw['content'] = content
        html_body = loader.render_to_string('email_templates/base_template.html', kw)

        connection = get_connection(fail_silently=False)
        email = EmailMultiAlternatives(subject=subj, body=text_body, from_email=_from, to=[to], connection=connection)
        email.attach_alternative(html_body, "text/html")
        return email.send()