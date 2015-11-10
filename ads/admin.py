#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.contrib import admin
from ads.models import *
from django.conf.urls import url

from django.shortcuts import get_object_or_404, render, redirect
from ads import tasks
from estate_ads import settings
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

import csv
from ads.forms import MatchFieldsForm, CompareFieldsForm, SetConstantValueForm
from django.forms import Form

from django.core.files.base import ContentFile

from recipes.persistent_dict import PersistentDict

from djcelery.models import TaskState, WorkerState, PeriodicTask, IntervalSchedule, CrontabSchedule


# rebuild search index after each deleting of file
from django.db.models.signals import post_delete
from django.core.management import call_command


def rebuild_index_callback(sender, **kwargs):
    call_command('rebuild_index', interactive=False)

post_delete.connect(rebuild_index_callback, sender=ImportFile)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'form_add', 'form_filter')


class AdAdmin(admin.ModelAdmin):
    list_display = ('title', 'pub_date')
    list_filter = ['pub_date', 'blocked', 'category']
    search_fields = ['title']
    exclude = ('similar', 'gkey',)

    # formfield_overrides = {
    #     models.TextField: {'widget': TinyMCE(attrs={'cols': 80, 'rows': 30})},
    # }

    # def get_form(self, request, obj=None, **kwargs):
    #     current_user = request.user
    #     if not current_user.profile.is_manager:
    #         self.exclude = ('added_by',)
    #         self.list_display = ('name', 'finish')
    #     form = super(AdAdmin, self).get_form(request, obj, **kwargs)
    #     form.current_user = current_user
    #     return form


class PaidOptionAdmin(admin.ModelAdmin):

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('uid',)
        return self.readonly_fields


class ImportFileAdmin(admin.ModelAdmin):

    readonly_fields = ('date',)
    fields = ('file', 'date')

    def get_urls(self):
        urls = super(ImportFileAdmin, self).get_urls()
        my_urls = [
            url(r'(?P<file_id>\d+)/import_data/$', self.admin_site.admin_view(self.import_data), name='import_file'),
            url(r'(?P<file_id>\d+)/import_data/delete/$',
                self.admin_site.admin_view(self.delete_items), name='delete_import_items'),
        ]
        return my_urls + urls

    shelve_set_path = os.path.join(settings.MEDIA_ROOT, settings.IMPORT_SETTINGS_PATH)
    if not os.path.isdir(shelve_set_path):
        os.makedirs(shelve_set_path)

    @staticmethod
    def get_csv_content(file_path):
        headers = lines = []
        with open(file_path, 'rU') as csvfile:
            spam_reader = csv.reader(csvfile, delimiter=',', quotechar='"', dialect=csv.excel_tab)
            headers = spam_reader.next()
            for line in spam_reader:
                lines.append(line)
        return headers, lines


    def delete_items(self, request, file_id):
        imported_file = get_object_or_404(ImportFile, id=file_id)
        if request.method == 'POST':
            Ad.objects.filter(imported=imported_file).delete()
            post_delete.send(sender=ImportFile)
            print('send')
            with PersistentDict(imported_file.settings.path, 'w', format='json') as params:
                del params['ids']

            return redirect('/admin/ads/importfile/%d/import_data/' % imported_file.id)
        return render(request, 'admin/ads/importfile/delete_items.html', {'file': imported_file})

    def import_data(self, request, file_id):

        imported_file = get_object_or_404(ImportFile, id=file_id)
        label = _('Compare imported data with our DB model')

        # from recipes.parser import Crawler
        # print(Crawler.get_from_khforum('http://www.kharkovforum.com/showthread.php?t=3904983'))
        if imported_file.settings:
            file_path = imported_file.settings.path
        else:
            file_path = os.path.join(self.shelve_set_path, str(file_id)+'.db')
            imported_file.settings.save(os.path.basename(file_path), ContentFile(""))
            imported_file.save()
        form = None
        info = {}
        curr_url = request.get_full_path()
        if curr_url.find('?') > 0:
            curr_url = curr_url[:curr_url.index('?')]

        with PersistentDict(file_path, 'w', format='json') as params:
            if 'datetime' not in params or params['datetime'] != str(imported_file.date):
                params['datetime'] = str(imported_file.date)
                params['stage'] = 1

            stage = int(request.GET.get('stage')) if request.GET.get('stage') and int(request.GET.get('stage')) < params['stage'] \
                else params['stage']
            # 1. MATCHING
            if stage == 1:
                if params['stage'] == 1:
                    params['headers'], params['lines'] = ImportFileAdmin.get_csv_content(imported_file.file.path)

                if request.method == 'POST':
                    form = MatchFieldsForm(request.POST, match_fields=params['headers'])
                    if form.is_valid():
                        params['matching'] = form.cleaned_data
                        if 'comparing' in params:
                            del params['comparing']
                        if 'curr_comp' in params:
                            del params['curr_comp']
                        params.sync()
                        info['task_id'] = tasks.prep_compare.delay(file_path).task_id
                        form = None
                        # return redirect(curr_url)
                elif 'matching' in params:
                    form = MatchFieldsForm(params['matching'], match_fields=params['headers'])
                else:
                    form = MatchFieldsForm(match_fields=params['headers'])

            # 2. COMPARING FIELDS: YES - TRUE, SOME CATEGORY - OUR CATEGORY
            elif stage == 2:
                # if request.GET.get('stage') == '2':
                #     params['to_compare'] = params['compared']
                #     params['compared'] = []

                if 'curr_comp' not in params:
                    params['curr_comp'] = 0

                label = 'Compare values founded in file. Page (%d / %d)' % (params['curr_comp']+1, len(params['to_compare']))
                if request.method == 'POST':
                    form = CompareFieldsForm(request.POST, compare_fields=params['comparing'],
                                             current_field=params['to_compare'][params['curr_comp']])
                    if form.is_valid():
                        if params['curr_comp'] < len(params['to_compare']) - 1:
                            params['curr_comp'] += 1
                        else:
                            params['stage'] = 3
                            del params['curr_comp']
                        return redirect(curr_url)
                else:
                    form = CompareFieldsForm(compare_fields=params['comparing'],
                                             current_field=params['to_compare'][params['curr_comp']])

            elif stage == 3:
                if request.method == 'POST':
                    form = SetConstantValueForm(request.POST, matching=params['matching'])
                    if form.is_valid():
                        params['constants'] = form.cleaned_data
                        params['stage'] = 4

                        return redirect(curr_url)
                elif 'constants' in params:
                    form = SetConstantValueForm(params['constants'], matching=params['matching'])
                else:
                    form = SetConstantValueForm(matching=params['matching'])

            elif stage == 4:
                # del params['ids']
                # from recipes.parser import Crawler
                # print(Crawler.get_attacments_urls('http://premier.ua/adv-9094511.aspx'))
                if request.method == 'POST':
                    if 'ids' not in params:
                        label = _('Wait until the process is finished')
                        info['task_id'] = tasks.import_ads.delay(file_id)
                        #params['ids'] = tasks.import_ads(file_id)
                else:
                    if 'ids' not in params:
                        label = _('Click "Next" to import %d ads') % len(params['lines'])
                        form = Form()
                    else:
                        info['results'] = Ad.objects.filter(pk__in=params['ids']) if 'ids' in params else []
                        label = _('Successfully imported %d ads') % len(info['results'])
            info['headers'] = params['headers']
            info['lines'] = params['lines'][:4]
            info['stage'] = stage
            info['max_stage'] = params['stage']
            info['curr_url'] = curr_url
            context = {'file': imported_file, 'info': info, 'form': form, 'label': label}

        return render(request, 'admin/ads/importfile/import.html', context)


class DistrictAdmin(admin.ModelAdmin):
    list_filter = ('town',)


class SubCategoryAdmin(admin.ModelAdmin):
    list_filter = ('category',)


class TownAdmin(admin.ModelAdmin):
    list_filter = ('region',)


class RegionAdmin(admin.ModelAdmin):
    list_filter = ('country',)


class ImageAttachmentAdmin(admin.ModelAdmin):
    readonly_fields = ('ad',)


class VideoAttachmentAdmin(admin.ModelAdmin):
    readonly_fields = ('ad',)

admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Country)
admin.site.register(Street)
admin.site.register(Metro)
admin.site.register(Region, RegionAdmin)
admin.site.register(Town, TownAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(ImageAttachment, ImageAttachmentAdmin)
admin.site.register(VideoAttachment, VideoAttachmentAdmin)
admin.site.register(PaidOption, PaidOptionAdmin)
admin.site.register(ImportFile, ImportFileAdmin)

admin.site.unregister(TaskState)
admin.site.unregister(WorkerState)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(PeriodicTask)


admin.site.index_template = 'admin/ads/index.html'
