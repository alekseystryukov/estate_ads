#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WSGI config for estate_ads project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
"""

import os
import socket

setting_file = "estate_ads.settings_prod" if socket.gethostname() == 'onchange.com.ua' else "estate_ads.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", setting_file)

# import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

# os.environ['LC_ALL'] = "ru_RU.UTF-8"

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import djcelery
djcelery.setup_loader()
