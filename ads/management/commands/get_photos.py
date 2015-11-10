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
    option_list = BaseCommand.option_list + (make_option('--delete', action='store_true', dest='delete',
                                                         default=False,
                                                         help='Remove imported ads, if limit for category reached'),)

    @staticmethod
    def get_photos(ad_id):
        try:
            ad = Ad.objects.get(pk=ad_id)
            print(ad)
        except Ad.DoesNotExist:
            return False
        for img in ad.imageattachment_set.all():
            img.delete()
        if ad.url:
            for ur in Crawler.get_attacments_urls(ad.url):
                att = ImageAttachment(ad=ad)
                att.get_remote_image(ur)

    def handle(self, *args, **options):
        from django.utils import translation
        translation.activate('en')  # with en-us everything crashes
        print(args)
        print(options)
        if args:
            for ad_id in args:
                self.get_photos(ad_id)
        else:
            first = Ad.objects.all().order_by('id')[0]
            last = Ad.objects.all().order_by('-id')[0]
            print(first.id)
            print(last.id)
            for ad_id in range(first.id, last.id):
                self.get_photos(ad_id)


#153425
