# -*- encoding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from tasks import send_email_to_all
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from email_templates.models import EmailTemplate
from forms import EmailTemplateAdminForm


class EmailTemplateAdmin(admin.ModelAdmin):

    def get_urls(self):
        urls = super(EmailTemplateAdmin, self).get_urls()
        my_urls = [
            url(r'(?P<eid>\w+)/send_to_all/$', self.admin_site.admin_view(self.send_to_all), name='send_to_all'),
        ]
        return my_urls + urls

    def send_to_all(self, request, eid):
        send_email_to_all.delay(eid)
        messages.success(request, _('Email will be send to all users'))
        return redirect(reverse("admin:email_templates_emailtemplate_change", args=(eid,)))

    list_display = ['desc', 'subject']
    form = EmailTemplateAdminForm

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('uid',)
        return self.readonly_fields

admin.site.register(EmailTemplate, EmailTemplateAdmin)

