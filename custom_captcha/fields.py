from captcha.fields import CaptchaField, BaseCaptchaTextInput
from django.forms.fields import CharField, MultiValueField
from django.forms import ValidationError
from django.core.exceptions import ImproperlyConfigured
from captcha.models import CaptchaStore, get_safe_now
from captcha.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms


class MyCaptchaTextInput(BaseCaptchaTextInput):
    def __init__(self, attrs=None, **kwargs):
        self._args = kwargs
        self._args['output_format'] = self._args.get('output_format') or settings.CAPTCHA_OUTPUT_FORMAT
        self._args['id_prefix'] = self._args.get('id_prefix')
        for key in ('image', 'hidden_field', 'text_field'):
            if '%%(%s)s' % key not in self._args['output_format']:
                raise ImproperlyConfigured('All of %s must be present in your CAPTCHA_OUTPUT_FORMAT setting. Could not find %s' % (
                    ', '.join(['%%(%s)s' % k for k in ('image', 'hidden_field', 'text_field')]),
                    '%%(%s)s' % key
                ))
        super(MyCaptchaTextInput, self).__init__(attrs)

    def build_attrs(self, extra_attrs=None, **kwargs):
        ret = super(MyCaptchaTextInput, self).build_attrs(extra_attrs, **kwargs)
        if self._args.get('id_prefix') and 'id' in ret:
            ret['id'] = '%s_%s' % (self._args.get('id_prefix'), ret['id'])
        return ret

    def id_for_label(self, id_):
        ret = super(MyCaptchaTextInput, self).id_for_label(id_)
        if self._args.get('id_prefix') and 'id' in ret:
            ret = '%s_%s' % (self._args.get('id_prefix'), ret)
        return ret

    def format_output(self, rendered_widgets):
        hidden_field, text_field = rendered_widgets
        text_field = text_field.replace('<input', '<input autocomplete="off" required="required"')
        return self._args['output_format'] % {
            'image': self.image_and_audio,
            'hidden_field': hidden_field,
            'text_field': text_field,
            'ref_button': self.ref_button
        }

    def render(self, name, value, attrs=None):
        self.fetch_captcha_store(name, value, attrs)

        self.image_and_audio = '<img src="%s" alt="captcha" class="captcha" />' % self.image_url()
        self.ref_button = '<button type="button" data-url="%s"  class="captchaRefresh" ><em class="sprite ico_refresh"></em></button>' % self.refresh_url()
        if settings.CAPTCHA_FLITE_PATH:
            self.image_and_audio = '<a href="%s" title="%s">%s</a>' % (self.audio_url(), _('Play CAPTCHA as audio file'), self.image_and_audio)
        return super(MyCaptchaTextInput, self).render(name, self._value, attrs=attrs)


class MyCaptchaField(MultiValueField):
    def __init__(self, *args, **kwargs):
        fields = (
            CharField(show_hidden_initial=True),
            CharField(),
        )
        if 'error_messages' not in kwargs or 'invalid' not in kwargs.get('error_messages'):
            if 'error_messages' not in kwargs:
                kwargs['error_messages'] = {}
            kwargs['error_messages'].update({'invalid': _('Invalid CAPTCHA')})

        kwargs['widget'] = kwargs.pop('widget', MyCaptchaTextInput(
            output_format=kwargs.pop('output_format', None),
            id_prefix=kwargs.pop('id_prefix', None)
        ))

        super(MyCaptchaField, self).__init__(fields, *args, **kwargs)

    def compress(self, data_list):
        if data_list:
            return ','.join(data_list)
        return None

    def clean(self, value):
        super(MyCaptchaField, self).clean(value)
        response, value[1] = (value[1] or '').strip().lower(), ''
        CaptchaStore.remove_expired()
        if settings.CAPTCHA_TEST_MODE and response.lower() == 'passed':
            # automatically pass the test
            try:
                # try to delete the captcha based on its hash
                CaptchaStore.objects.get(hashkey=value[0]).delete()
            except CaptchaStore.DoesNotExist:
                # ignore errors
                pass
        elif not self.required and not response:
            pass
        else:
            try:
                CaptchaStore.objects.get(response=response, hashkey=value[0], expiration__gt=get_safe_now()).delete()
            except CaptchaStore.DoesNotExist:
                raise ValidationError(getattr(self, 'error_messages', {}).get('invalid', _('Invalid CAPTCHA')))
        return value
