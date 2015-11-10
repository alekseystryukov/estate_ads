from djcelery import celery
import sys

import traceback
from time import sleep
from django.core.mail import EmailMessage

from ads.forms import CompareFieldsForm, MatchFieldsForm
from ads.models import Ad, Category, SubCategory, ImportFile, ImageAttachment
from recipes.persistent_dict import PersistentDict
from django.core.mail import send_mail

import dateutil.parser
from datetime import datetime

from recipes.parser import Crawler
from urlparse import urlparse

from django.core.management import call_command
from django.conf import settings



@celery.task
def test(i, j):
    print('HEEELLLLOO')
    email = EmailMessage('Hello', 'World+' + str(i), to=['aleksey.stryukov@gmail.com'])
    email.send()
    return i


@celery.task
def find_similar(ad_id):
    from ads.models import Ad
    ad = Ad.objects.get(pk=ad_id)
    similar = Ad.objects.exclude(pk=ad_id).filter(category=ad.category, sub_category=ad.sub_category,
                                                  district=ad.district)[:3]
    ad.similar.add(*similar)
    ad.save()


@celery.task
def update_index():
    call_command('update_index', interactive=False)
    # chane owner of current media folder
    import os
    now = datetime.now()
    directory = os.path.join(settings.MEDIA_ROOT, 'img', str(now.year), str(now.month), str(now.day))
    os.system("chown -R www-data:www-data " + directory)


@celery.task
def update_index_last_hours(hours):
    call_command('update_index', age=hours, interactive=False)

@celery.task
def parse_ads():
    try:
        call_command('base_parse')
    except:
        send_mail('Parse Ads Error', traceback.format_exc(), settings.DEFAULT_FROM_EMAIL,
                  [admin[1] for admin in settings.ADMINS], fail_silently=False)
        parse_ads.apply_async(countdown=600)



@celery.task
def remove_old_crawled_from_db():
    call_command('manage_ads', delete=True, interactive=False)




@celery.task(name="ads.tasks.prep_compare")
def prep_compare(file_path):
    with PersistentDict(file_path, 'w', format='json') as params:
        comparing = {field: [] for field in params['matching']}
        to_compare = []
        count = (101*len(params['lines']))/100
        i = 0
        for line in params['lines']:
            for field, pos in params['matching'].items():
                if pos:
                    if field in CompareFieldsForm.compared_fields:
                        if type(pos) == list:
                            val = ""
                            for p in pos:
                                try:
                                    p = int(p)
                                except ValueError:
                                    pass
                                else:
                                    if len(line) > p and line[p]:
                                        val += ", " + line[p] if val else line[p]
                            if val:
                                comparing[field].append(val)
                                to_compare.append(field)
                        else:
                            try:
                                pos = int(pos)
                            except ValueError:
                                pass
                            else:
                                if len(line) > pos and line[pos]:
                                    comparing[field].append(line[pos])
                                    to_compare.append(field)
                else:
                    del params['matching'][field]
            i += 1
            celery.current_task.update_state(state='PROGRESS', meta={'current': i, 'total': count})
        #  save unqiue values only
        for field, values in comparing.items():
            comparing[field] = list(set(values))
        to_compare = list(set(to_compare))
        params['to_compare'] = to_compare
        # for field in to_compare:
        #     if field in CompareFieldsForm.compared_fields:
        #         params['to_compare'].append(field)
        params['compared'] = []
        params['comparing'] = comparing
        params['stage'] = 2


@celery.task(name="ads.tasks.import_attachments")
def import_attachments(ad_id):
    try:
        ad = Ad.objects.get(pk=ad_id)
        print(ad)
    except Ad.DoesNotExist:
        return False
    print(ad.url)
    for ur in Crawler.get_attacments_urls(ad.url):
        att = ImageAttachment(ad=ad)
        att.get_remote_image(ur)


@celery.task(name="ads.tasks.import_ads")
def import_ads(file_id):
    imported_file = ImportFile.objects.get(id=file_id)
    clear_prev_ads(imported_file)
    with PersistentDict(imported_file.settings.path, 'w', format='json') as params:
    #with closing(shelve.open(file_path)) as params:
        ids = []
        count = len(params['lines'])
        i = 0
        for line in params['lines']:
            ad = {}
            for field in params['matching']:
                if params['matching'][field] != 'Constant' and 'Constant' not in params['matching'][field]:

                    poss = params['matching'][field] if type(params['matching'][field]) is list else [params['matching'][field]]
                    value = ""
                    for pos in poss:
                        pos = int(pos)
                        if len(line) < pos or not line[pos].strip():
                            continue
                        value += ", " + line[pos] if value else line[pos]

                    if not value:
                        continue
                    if field in CompareFieldsForm.compared_fields:
                        curr_comp_field = CompareFieldsForm.compared_fields[field]
                        compared_obj = curr_comp_field['model'].objects.get(pk=value)
                        if field == 'category':
                            if compared_obj.sub_category is not None:
                                ad['category'] = compared_obj.sub_category.category
                                ad['sub_category'] = compared_obj.sub_category
                            else:
                                ad['category'] = compared_obj.category
                        elif field == 'district':
                            if compared_obj.district:
                                ad['district'] = compared_obj.district
                                ad['town'] = compared_obj.district.town
                            else:
                                ad['town'] = compared_obj.town
                        else:
                            ad[field] = compared_obj.value
                    elif field == 'pub_date':
                        pub_date = dateutil.parser.parse(value)
                        if str(pub_date.time()) == "00:00:00":
                            pub_date = datetime.combine(pub_date.date(), datetime.now().time())
                        ad[field] = ad['order_date'] = pub_date
                    else:
                        ad[field] = Ad.filter_field(value, field)
                elif 'constants' in params and field in params['constants']:  # constant
                    value = Ad.filter_field(str(params['constants'][field]), field)
                    if field in CompareFieldsForm.compared_fields:
                        if field == 'category':
                            cat_values = value.split('-')
                            if len(cat_values) > 1:
                                sub_cat = SubCategory.objects.get(pk=cat_values[1])
                                ad['category'] = sub_cat.category
                                ad['sub_category'] = sub_cat
                            else:
                                cat = Category.objects.get(pk=cat_values[0])
                                ad['category'] = cat
                        elif 'foreign' in CompareFieldsForm.compared_fields[field]:
                            ad[field] = CompareFieldsForm.compared_fields[field]['foreign'].objects.get(pk=value)
                        else:
                            for key, val in CompareFieldsForm.compared_fields[field]['choices']:
                                if str(key) == value:
                                    ad[field] = val
                    else:
                        ad[field] = value
            empty = set(MatchFieldsForm.required) - set(ad.keys())
            if not empty:
                ad_obj = Ad(**ad)
                ad_obj.imported = imported_file
                ad_obj.save()
                find_similar.delay(ad_obj.id)
                if ad_obj.url:
                    parsed_uri = urlparse(ad_obj.url)
                    if parsed_uri.netloc in Crawler.DOMAINS:
                        import_attachments.delay(ad_obj.id)
                ids.append(ad_obj.id)
            i += 1
            celery.current_task.update_state(state='PROGRESS', meta={'current': i, 'total': count})
        params['ids'] = ids
        return ids








def clear_prev_ads(imported_file):
    Ad.objects.filter(imported=imported_file).delete()



