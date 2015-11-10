from django import forms
from tinymce.widgets import TinyMCE


class EmailTemplateAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EmailTemplateAdminForm, self).__init__(*args, **kwargs)
        self.fields['html'].widget = TinyMCE(attrs={'cols': 160, 'rows': 60},
                                             mce_attrs={'plugin_preview_width': 1000})