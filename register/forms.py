from django import forms
from custom_captcha.fields import MyCaptchaField
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext


def make_label_req(text):
    return mark_safe(ugettext(text) + "&nbsp;<em>*</em>")


class MyRegistrationForm(forms.Form):
    required_css_class = 'required'

    email = forms.EmailField(label=make_label_req("E-mail"), widget=forms.EmailInput(attrs={"required": "required"}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"required": "required"}), label=make_label_req("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"required": "required",
                                                                  "data-parsley-equalto": "#id_password1"}),
                                label=make_label_req("Password (again)"))
    captcha = MyCaptchaField(label=make_label_req("I'm a human"))
    terms = forms.BooleanField(label=make_label_req('I agree with <a href="/terms/" target="_blank">Terms of Use of service</a>'),
                               widget=forms.CheckboxInput(attrs={"required": "required"}))

    def __init__(self,  *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(MyRegistrationForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.

        """
        try:
            user = get_user_model().objects.get(email__iexact=self.cleaned_data['email'])
        except get_user_model().DoesNotExist:
            pass
        else:
            if user.is_active or user.banned or user.registrationprofile_set.all():
                raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data





