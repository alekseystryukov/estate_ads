from django import forms
from postman.forms import WriteForm, AnonymousWriteForm
from postman.fields import CommaSeparatedUserField
from fields import CommaSeparatedUserIdField
from postman.models import Message
from django.forms import HiddenInput
from django.utils.translation import ugettext_lazy as _

from email_templates.models import EmailTemplate


class IdBasedForm(forms.ModelForm):

    def clean_recipients(self):
        """Check no filter prohibit the exchange."""
        recipients = self.cleaned_data['recipients']
        exchange_filter = getattr(self, 'exchange_filter', None)
        if exchange_filter:
            errors = []
            filtered_names = []
            recipients_list = recipients[:]
            for u in recipients_list:
                try:
                    reason = exchange_filter(self.instance.sender, u, recipients_list)
                    if reason is not None:
                        recipients.remove(u)
                        filtered_names.append(
                            self.error_messages[
                                'filtered_user_with_reason' if reason else 'filtered_user'
                            ].format(username=u.get_username(), reason=reason)
                        )
                except forms.ValidationError as e:
                    recipients.remove(u)
                    errors.extend(e.messages)
            if filtered_names:
                errors.append(self.error_messages['filtered'].format(users=', '.join(filtered_names)))
            if errors:
                raise forms.ValidationError(errors)
        return recipients


# set my model to WriteForm and AnonymousWriteForm
# def email(subject_template, message_template, recipient_list, object, action, site):
#     """Compose and send an email."""
#     ctx_dict = {'site': site, 'object': object, 'action': action}
#     subject = render_to_string(subject_template, ctx_dict)
#     # Email subject *must not* contain newlines
#     subject = ''.join(subject.splitlines())
#     message = render_to_string(message_template, ctx_dict)
#     # during the development phase, consider using the setting: EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)
#
# def email_visitor(object, action, site):
#     """Email a visitor."""
#     email('postman/email_visitor_subject.txt', 'postman/email_visitor.txt', [object.email], object, action, site)
#
#
# def notify_user(object, action, site):
#     """Notify a user."""
#     if action == 'rejection':
#         user = object.sender
#         label = 'postman_rejection'
#     elif action == 'acceptance':
#         user = object.recipient
#         parent = object.parent
#         label = 'postman_reply' if (parent and parent.sender_id == object.recipient_id) else 'postman_message'
#     else:
#         return
#     if notification:
#         # the context key 'message' is already used in django-notification/models.py/send_now() (v0.2.0)
#         notification.send(users=[user], label=label, extra_context={'pm_message': object, 'pm_action': action})
#     else:
#         if not DISABLE_USER_EMAILING and user.email and user.is_active:
#             email('postman/email_user_subject.txt', 'postman/email_user.txt', [user.email], object, action, site)

# def notify_users(self, initial_status, site, is_auto_moderated=True):
#         """Notify the rejection (to sender) or the acceptance (to recipient) of the message."""
#         if initial_status == 'p':
#             if self.is_rejected():
#                 # Bypass: for an online user, no need to notify when rejection is immediate.
#                 # Only useful for a visitor as an archive copy of the message, otherwise lost.
#                 if not (self.sender_id is not None and is_auto_moderated):
#                     (notify_user if self.sender_id is not None else email_visitor)(self, 'rejection', site)
#             elif self.is_accepted():
#                 (notify_user if self.recipient_id is not None else email_visitor)(self, 'acceptance', site)
#
# setattr(Message, 'notify_users', notify_users)


class ContactForm(WriteForm, IdBasedForm):
    recipients = CommaSeparatedUserIdField(label=(_("Recipients"), _("Recipient")), help_text='',
                                           max=1, widget=HiddenInput)  # one recipient is enough

    # def __init__(self, *args, **kwargs):
    #     super(ContactForm, self).__init__(*args, **kwargs)
    #     self.fields['subject'].initial = 'text'


class AnonymousContactForm(AnonymousWriteForm, IdBasedForm):

    recipients = CommaSeparatedUserIdField(label=(_("Recipients"), _("Recipient")), help_text='',
                                           max=1, widget=HiddenInput)  # one recipient is enough