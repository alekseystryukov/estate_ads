from django.conf import settings
from registration.models import RegistrationProfile
from email_templates.models import EmailTemplate


class HtmlRegistrationProfile(RegistrationProfile):
    class Meta:
        proxy = True

    def send_activation_email(self, site):
        """Send the activation mail"""


        ctx_dict = {'activation_key': self.activation_key, 'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site}

        email = EmailTemplate.objects.get(pk='registration_activation_email')
        email.send(self.user.email, None, **ctx_dict)
        # from django.core.mail import EmailMultiAlternatives
        # from django.template.loader import render_to_string
        # subject = render_to_string('registration/activation_email_subject.txt', ctx_dict)
        # # Email subject *must not* contain newlines
        # subject = ''.join(subject.splitlines())
        #
        # message_text = render_to_string('registration/activation_email.txt', ctx_dict)
        # message_html = render_to_string('registration/activation_email.html', ctx_dict)
        #
        # msg = EmailMultiAlternatives(subject, message_text, settings.DEFAULT_FROM_EMAIL, [self.user.email])
        # msg.attach_alternative(message_html, "text/html")
        # msg.send()