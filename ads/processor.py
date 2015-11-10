from django.conf import settings
from django.contrib.sites.models import Site


def settings_processor(request):
    settings.BASE_SITE_URL = settings.PROTOCOL + (request.META['HTTP_HOST'] if 'HTTP_HOST' in request.META else Site.objects.get_current().domain)
    return {'settings': settings}


def site_processor(request):
    return {'site': Site.objects.get_current()}
