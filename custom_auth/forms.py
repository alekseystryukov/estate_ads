from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordResetForm
from django.utils.translation import ugettext_lazy as _



from django.contrib.auth import get_user_model
from django.contrib.sites.models import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.template import loader
from email_templates.models import EmailTemplate

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext


def make_label_req(text):
    return mark_safe(ugettext(text) + "&nbsp;<em>*</em>")


class MyAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if user.banned:
            raise forms.ValidationError(
                _('This E-mail was banned by admin.'),
                code='banned',
            )
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )


class MyPasswordResetForm(PasswordResetForm):
    def __init__(self,  *args, **kwargs):
        super(MyPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = _("Email address")
        self.fields['email'].widget.attrs['required'] = "required"

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             html_email_template_name=None,
             email_template_name='registration/password_reset_email.html',
             use_https=False, token_generator=default_token_generator,
             from_email=None, request=None):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        from django.core.mail import send_mail
        UserModel = get_user_model()
        email = self.cleaned_data["email"]
        active_users = UserModel._default_manager.filter(email__iexact=email, banned=False)
        for user in active_users:
            # Make sure that no email is sent to a user that actually has
            # a password marked as unusable
            if not user.has_usable_password():
                continue
            if not domain_override:
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
            else:
                site_name = domain = domain_override
            c = {
                'email': user.email,
                'domain': domain,
                'site_name': site_name,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
            }

            try:
                email = EmailTemplate.objects.get(pk='reset_user_password')
                print('sent')
                email.send(user.email, None, **c)
            except EmailTemplate.DoesNotExist:
                subject = loader.render_to_string(subject_template_name, c)
                # Email subject *must not* contain newlines
                subject = ''.join(subject.splitlines())
                email = loader.render_to_string(email_template_name, c)
                send_mail(subject, email, from_email, [user.email])



class MySetPasswordForm(SetPasswordForm):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(MySetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs['required'] = "required"
        self.fields['new_password2'].widget.attrs['required'] = "required"
        self.fields['new_password2'].widget.attrs["data-parsley-equalto"] = "#id_new_password1"
        self.fields['new_password1'].label = make_label_req('New password')
        self.fields['new_password2'].label = make_label_req('Password confirmation')
