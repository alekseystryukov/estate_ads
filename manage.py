#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import socket


if __name__ == "__main__":
    setting_file = "estate_ads.settings_prod" if socket.gethostname() == 'onchange.com.ua' else "estate_ads.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", setting_file)

    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
