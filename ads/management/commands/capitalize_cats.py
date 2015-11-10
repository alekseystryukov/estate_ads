#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from ads.models import Ad, Category, ImageAttachment
from optparse import make_option
from django.core.management import call_command
from recipes.parser import Crawler


class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = ''
    br = None


    def handle(self, *args, **options):
        from django.utils import translation
        translation.activate('en')  # with en-us everything crashes
        print(args)
        print(options)
        for cat in Category.objects.all():
            cat.name_en = cat.name_en.capitalize()
            cat.name_ru = cat.name_ru.capitalize()
            cat.name_uk = cat.name_uk.capitalize()
            cat.save()