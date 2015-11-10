from custom_user.models import AbstractEmailUser
from django.db import models
from django.utils.translation import ugettext_lazy as _



class MyCustomEmailUser(AbstractEmailUser):
    """
    Example of an EmailUser with a new field date_of_birth
    """
    banned = models.BooleanField(default=False, help_text=_('User will not be able login or register again'))
    name = models.CharField(null=True, blank=True, max_length='50')
    phone = models.CharField(null=True, blank=True, max_length='50')
    score = models.IntegerField(default=0, max_length=4)
    is_private = models.BooleanField(default=False)

    def get_full_name(self):
        """ Return the email."""
        return self.name or self.email[:self.email.index('@')]

    # def set_password(self):
    #     print('set password')

