#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from ads.models import Ad, Category
from optparse import make_option
from django.core.management import call_command
from recipes.email import send_log


class Command(BaseCommand):
    args = ''
    help = ''
    br = None
    option_list = BaseCommand.option_list + (make_option('--delete', action='store_true', dest='delete',
                                                         default=False,
                                                         help='Remove imported ads, if limit for category reached'),)

    def handle(self, *args, **options):
        from django.utils import translation
        translation.activate('en')  # with en-us everything crashes
        print(args)
        print(options)
        remove = options.get('delete', False)
        rebuild = False
        log = '------------------'
        for cat in Category.objects.all():
            for sub_cat in cat.subcategory_set.all():
                kws = {'sub_category': sub_cat, 'gkey__isnull': False, 'private': False}
                count = Ad.objects.filter(**kws).count()
                log += cat.name + ' - ' + sub_cat.name + ': ' + str(count)
                times = (count - 1000)/200
                if times > 0 and remove:
                    rebuild = True
                    for i in range(times):
                        to_remove = Ad.objects.filter(**kws).order_by('pub_date')[:200].values('id')
                        Ad.objects.filter(pk__in=[it['id'] for it in to_remove]).delete()

                    log += 'after remove'
                    count = Ad.objects.filter(**kws).count()
                    log += cat.name + ' - ' + sub_cat.name + ': ' + str(count)

            kws = {'category': cat, 'gkey__isnull': False, 'private': False}
            all_count = Ad.objects.filter(**kws).count()
            log += cat.name + ": " + str(all_count)
            log += '------------------'

            times = (all_count - 2000)/200
            if times > 0 and remove:
                rebuild = True
                for i in range(times):
                    to_remove = Ad.objects.filter(**kws).order_by('pub_date')[:200].values('id')
                    Ad.objects.filter(pk__in=[it['id'] for it in to_remove]).delete()

                all_count = Ad.objects.filter(**kws).count()
                log += cat.name + ": " + str(all_count)
        send_log(log)
        if rebuild:
            call_command('rebuild_index', interactive=False)

