from registration.backends.default.views import RegistrationView
from models import HtmlRegistrationProfile
from forms import MyRegistrationForm

from registration import signals

from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site


class ExtendedRegistrationView(RegistrationView):

    form_class = MyRegistrationForm

    def register(self, request, **cleaned_data):

            email, password = cleaned_data['email'], cleaned_data['password1']
            if Site._meta.installed:
                site = Site.objects.get_current()
            else:
                site = RequestSite(request)
            new_user = HtmlRegistrationProfile.objects.create_inactive_user(email, password, site)
            signals.user_registered.send(sender=self.__class__,
                                         user=new_user,
                                         request=request)
            return new_user