from django import forms
from django.conf import settings
from models import AnonymousFeedback, Feedback
from django.forms import Textarea, Select
from django.utils.translation import ugettext_lazy as _


class FeedbackForm(forms.ModelForm):
    type = forms.ChoiceField(choices=(("", _("Select"),),) + settings.FEEDBACK_CHOICES,
                             widget=Select(attrs={}))

    class Meta:
        model = Feedback
        exclude = ('user',)
        widgets = {
            "message": Textarea(attrs={}),
        }


class AnonymousFeedbackForm(FeedbackForm):
    class Meta:
        model = AnonymousFeedback
        exclude = ('user',)
        widgets = {
            #"type": Select(attrs={"class": "form-control", "required": "required"}),
            "message": Textarea(attrs={}),
        }