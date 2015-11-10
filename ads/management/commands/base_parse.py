#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError

import urllib
import urllib2
import mechanize
import cookielib


from StringIO import StringIO
import gzip

import json
import sys
import traceback

from django.conf import settings
from ads.models import District, Town, Region, Street, Metro, Ad, Category, SubCategory
from ads.tasks import find_similar, import_attachments
from recipes.parser import Crawler
from recipes.email import send_log
from urlparse import urlparse

import dateutil.parser
from django.utils import timezone
from datetime import datetime, date, timedelta
import time

from ads.templatetags.truncatesmart import truncatesmart
from django.core.management import call_command
from django.core.mail import send_mail

class Command(BaseCommand):
    args = ''
    help = 'Load data to site from "estate-in-kharkov.com"'
    br = None

    def handle(self, *args, **options):
        from django.utils import translation
        translation.activate('en')  # with en-us everything crashes
        self.stdout.write('Load Metro...')
        Command.get_metro()
        self.stdout.write('Load Districts...')
        Command.get_districts()
        self.stdout.write('Load Towns...')
        Command.get_towns()
        self.stdout.write('Load Streets...')
        Command.get_streets()
        self.stdout.write('Load Ads...')
        Command.get_ads()


    @classmethod
    def get(cls, url, data=None):

        if cls.br is None:
            cls.br = cls.login()

        r = cls.br.open(url, data)
        try:
            res = json.loads(r.read())
            if 'message' in res:
                raise ValueError
        except ValueError:
            import cgi
            send_mail('Need to login ', cgi.escape(str(r.read())), settings.DEFAULT_FROM_EMAIL,
                      [admin[1] for admin in settings.ADMINS], fail_silently=False)

            cls.br = cls.login()
            r = cls.br.open(url, data)
            res = json.loads(r.read())

        return res

        # headers = {
        #     'Host': 'estate-in-kharkov.com',
        #     'Connection': 'keep-alive',
        #     'Origin': 'http://estate-in-kharkov.com',
        #     'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36',
        #     'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        #     'Accept': 'application/json, text/javascript, */*; q=0.01',
        #     'Referer': 'http://estate-in-kharkov.com/index.php',
        #     'Accept-Encoding': 'gzip, deflate, sdch',
        #     'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,fr;q=0.2',
        #     #c48b3cc9cbdd45c9404bdccd0ee13a9a
        #     'Cookie': 'autorized=db7cc77b5fcbc094ecfe29822a100172; login=smitholeg; cdecv=c48b3cc9cbdde45c9404bdccd0ee13a9a',
        #     'X-Requested-With': 'XMLHttpRequest'
        # }
        #
        # req = urllib2.Request(url, data, headers)
        # response = urllib2.urlopen(req)
        # response_headers = response.info()
        #
        # if response_headers.get('Content-Encoding') == 'gzip':
        #     buf = StringIO(response.read())
        #     f = gzip.GzipFile(fileobj=buf)
        #     content = f.read()
        #     print('unzipped')
        # else:
        #     content = response.read()
        #
        # # encoding = response_headers['Content-Type'].split('charset=')[-1]
        # # content = unicode(content, encoding)
        # return json.loads(content)


    @classmethod
    def login(cls):
        # Browser
        br = mechanize.Browser()

        # Cookie Jar
        cj = cookielib.LWPCookieJar()
        br.set_cookiejar(cj)

        # Browser options
        br.set_handle_equiv(True)
        br.set_handle_gzip(True)
        br.set_handle_redirect(True)
        br.set_handle_referer(True)
        br.set_handle_robots(False)

        # Follows refresh 0 but not hangs on refresh > 0
        br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

        # Want debugging messages?
        # br.set_debug_http(True)
        # br.set_debug_redirects(True)
        # br.set_debug_responses(True)

        # User-Agent (this is cheating, ok?)
        br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686 (x86_64)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.115 Safari/537.36')]

        br.open('http://estate-in-kharkov.com/index.php?check',
                urllib.urlencode({'login': 'smitholeg', 'password': '1726354kov', 'go': 'Submit'}))

        return br


    @classmethod
    def get_districts(cls):
        town = Town.objects.get(pk=1)
        content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/raj-list.php')
        for key, item in content.items():
            did = key[1:]
            if item[1] and item[0]:
                dist, created = District.objects.get_or_create(pk=did, defaults={'name_en': item[1], 'name_ru': item[1],
                                                                                 'name_uk': item[1], 'town': town})
                if created:
                    print(dist)

    @classmethod
    def get_towns(cls):
        region = Region.objects.get(pk=1)
        content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/nasp-list.php')
        for key, item in content.items():
            did = key[1:]
            if item[1] and item[0]:
                dist, created = Town.objects.get_or_create(pk=did, defaults={'name_en': item[0], 'name_ru': item[0],
                                                                             'name_uk': item[0], 'region': region})
                if created:
                    print(dist)

    @classmethod
    def get_streets(cls):
        content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/ulica-list.php')
        for key, item in content.items():
            did = key[1:]
            if item[1] and item[0]:
                dist, created = Street.objects.get_or_create(pk=did, defaults={'name': item[0]})
                if created:
                    print(dist)

    @classmethod
    def get_metro(cls):
        content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/metro-list.php')

        for key, item in content.items():
            did = key[1:]
            if item[1] and item[0]:
                dist, created = Metro.objects.get_or_create(pk=did, defaults={'name': item[0]})
                if created:
                    print(dist)

    @classmethod
    def parse_categories(cls, ad, item, table):
        # print(table)
        # print(item['textob'])
        # del item['textob']
        # print(item)
        category = sub_category = None
        if table == 'kvart':
            category = Category.objects.get(pk=8)  # selling apartments
        elif table == 'arenda':
            tip = int(item['tip'])
            if tip in [5, 20, 21, 22, 23, 24, 25]:  # apartments rent
                category = Category.objects.get(pk=1)
                if int(item['srok']) == 2:  # посуточно
                    # srok-list
                    # n1: ["", ""]
                    # n2: ["Посуточно", "посут."]
                    # n3: ["Долгосрочно", "долг."]
                    sub_category = SubCategory.objects.get(pk=1)
                else:
                    sub_category = SubCategory.objects.get(pk=3)
                if tip != 25:
                    ad['rooms_count'] = tip - 19
            elif int(item['tip']) in [6, 7, 8, 9, 10, 26]:  # houses rent
                category = Category.objects.get(pk=3)
                if int(item['srok']) == 2:
                    sub_category = SubCategory.objects.get(pk=8)
                else:
                    sub_category = SubCategory.objects.get(pk=7)

            elif int(item['tip']) in [2, 3, 4]:   # комната , комуналка , подселение, гостинка
                category = Category.objects.get(pk=2)  # аренда комнат
                if int(item['srok']) == 2:
                    sub_category = SubCategory.objects.get(pk=5)
                else:
                    sub_category = SubCategory.objects.get(pk=6)

            elif int(item['tip']) in [18, 54]:  # участок, дача -> аренда земли
                category = Category.objects.get(pk=4)
            elif int(item['tip']) in [19, 53]:  # гараж , стоянка
                category = Category.objects.get(pk=5)
            else:
                category = Category.objects.get(pk=6)  # аренда помещений

        elif table == 'komn':
            category = Category.objects.get(pk=9)  # продажа комнат
            if item['tip'] == '3':
                sub_category = SubCategory.objects.get(pk=16)
            elif item['tip'] == '4':
                sub_category = SubCategory.objects.get(pk=17)
            elif item['tip'] == '5':
                sub_category = SubCategory.objects.get(pk=15)
            else:
                sub_category = SubCategory.objects.get(pk=14)

        elif table == 'domm':
            # n2: ["Дом", "дом"]
            # n3: ["Часть дома", "часть. д"]
            # n4: ["Дача", "дача"]
            # n5: ["Участок", "участок"]
            # n6: ["флигель", "флигель"]
            # n7: ["1/2 дома", "1/2 д"]
            # n8: ["1/3 дома", "1/3 д"]
            # n9: ["Коттедж", "котедж"]
            # n10: ["Усадьба", "усадьба"]
            # n11: ["Особняк", "особняк"]
            # n12: ["Недострой", "недострой"]
            # n13: ["Погреб", "Погреб"]
            # n14: ["2/3 дома", "2/3 дома"]
            # n15: ["Гараж", "Гараж"]
            if item['tip'] in ['4', '5']:
                category = Category.objects.get(pk=11)  # продажа земли
            elif item['tip'] == '15':
                category = Category.objects.get(pk=12)  # продажа гаражей, стоянок
            elif item['tip'] == '13':
                category = Category.objects.get(pk=13)  # продажа помещений
            else:
                category = Category.objects.get(pk=10)  # продажа домов

        elif table == 'negil':
            # n2: ["Магазин", "Магаз"]
            # n3: ["Торговый зал", "Торг.зал"]
            # n4: ["Киоск", "Киоск"]
            # n5: ["Павильон", "Павильон"]
            # n6: ["Супермаркет", "Суперм"]
            # n7: ["Помещение", "Помещ"]
            # n8: ["Здание", "Здание"]
            # n9: ["Парикмахерская", "Парикм"]
            # n10: ["Фотосалон", "Фотосал"]
            # n11: ["Ателье", "Ателье"]
            # n12: ["Завод", "Завод"]
            # n13: ["Фабрика", "Фабрика"]
            # n14: ["Склад", "Склад"]
            # n15: ["Цех", "Цех"]
            # n16: ["Офис", "Офис"]
            # n17: ["Участок", "Участок"]
            # n18: ["Производство", "Произв."]
            # n19: ["СТО", "СТО"]
            # n20: ["АЗС", "АЗС"]
            # n21: ["Компьютерный зал", "комп зал"]
            # n22: ["Кафе", "кафе"]
            # n23: ["Контейнер", "контейнер"]
            # n24: ["Бизнес", "бизнес"]
            # n25: ["Свиноферма", "свиноверма"]
            # n26: ["Маслобойный цех", "маслобойный цех"]
            # n27: ["Баня", "баня"]
            # n28: ["Комплекс", "Комплекс"]
            # n29: ["Птицеферма", "птицеферма"]
            # n30: ["Подвал", "подвал"]
            # n31: ["Мастерская", "мастерская"]
            # n32: ["Мельница", "мельница"]
            # n33: ["Ресторан", "ресторан"]
            # n34: ["Автостоянка", "автостоянка"]
            # n35: ["Цоколь", "цоколь"]
            # n36: ["Предприятие", "предприятие"]
            # n37: ["Площадка", "площадка"]
            # n38: ["База", "база"]
            # n39: ["Лагерь", "лагерь"]
            # n40: ["Ангар", "Ангар"]
            # n41: ["Квартира", "квартира"]
            # n42: ["Вулканизация", "вулканизация"]
            # n43: ["Фирма", "фирма"]
            # n44: ["Ферма", "ферма"]
            # n45: ["Клуб", "клуб"]
            # n46: ["Аптека", "аптека"]
            # n47: ["Автомойка", "автомойка"]
            # n48: ["Место", "Место"]
            # n49: ["Овощехранилище", "Овощехр."]
            # n50: ["АТП", "АТП"]
            # n51: ["Гараж", "Гараж"]
            # n52: ["Вагончик", "Вагончик"]
            # n53: ["Коровник", "Коровник"]
            if item['tip'] == '17':
                category = Category.objects.get(pk=11)  # продажа земли
            elif item['tip'] == '51':
                category = Category.objects.get(pk=12)  # продажа гаражей, стоянок
            else:
                category = Category.objects.get(pk=13)  # продажа помещений

        elif table == 'client':
            # n2: ["Комната", "комната"]
            # n3: ["Коммуналка", "коммун."]
            # n4: ["Подселение", "подселен."]
            # n5: ["Гостинка", "гостин."]
            # n6: ["Флигель", "флигель"]
            # n7: ["1/2 дома", "1/2 дома"]
            # n8: ["1/3 дома", "1/3 дома"]
            # n9: ["Коттедж", "котедж"]
            # n10: ["Усадьба", "усадьба"]
            # n11: ["Фотосалон", "Фотосалон"]
            # n12: ["Ателье", "Ателье"]
            # n13: ["Завод", "Завод"]
            # n14: ["Фабрика", "Фабрика"]
            # n15: ["Склад", "Склад"]
            # n16: ["Цех", "Цех"]
            # n17: ["Офис", "Офис"]
            # n18: ["Участок", "Участок"]
            # n19: ["Гараж", "Гараж"]
            # n20: ["1-комн. квартира", "1к из.кв"]
            # n21: ["2-комн. квартира", "2к из.кв"]
            # n22: ["3-комн. квартира", "3к из.кв"]
            # n23: ["4-комн. квартира", "4к из.кв"]
            # n24: ["5-комн. квартира", "5к из.кв"]
            # n25: ["Квартира", "квартира"]
            # n26: ["Дом", "дом"]
            # n27: ["Магазин", "магазин"]
            # n28: ["Место", "место"]
            # n29: ["Контейнер", "контейнер"]
            # n30: ["Кафе", "кафе"]
            # n31: ["Киоск", "киоск"]
            # n32: ["Помещение", "помещение"]
            # n33: ["АЗС", "АЗС"]
            # n34: ["Ангар", "ангар"]
            # n35: ["СТО", "СТО"]
            # n36: ["Свинарник", "свинарник"]
            # n37: ["Павильон", "павильон"]
            # n38: ["База", "база"]
            # n39: ["Комплекс", "комплекс"]
            # n40: ["Здание", "здание"]
            # n41: ["Мастерская", "мастерская"]
            # n42: ["Вулканизация", "вулканизац"]
            # n43: ["Аптека", "аптека"]
            # n44: ["Бизнес", "бизнес"]
            # n45: ["Площадь", "площадь"]
            # n46: ["Дача", "дача"]
            # n47: ["Парикмахерская", "парикмахерская"]
            # n48: ["Бокс", "бокс"]
            # n49: ["Палатка", "палатка"]
            # n50: ["Фирма", "фирма"]
            # n51: ["Отдел в магазине", "отдел в магаз."]
            # n52: ["Баня", "баня"]
            # n53: ["Жилье", "Жилье"]
            # n54: ["Автомойка", "Автомойка"]
            # vid == 2 сниму, vid == 4 меняю , vid == 3 куплю
            if item['vid'] == 4:
                category = Category.objects.get(pk=15)
            elif item['vid'] == 2:
                if item['tip'] in ['5', '20', '21', '22', '23', '24', '25']:
                    category = Category.objects.get(pk=1)  # аренда квартир
                    if item['tip'] != '25':
                        ad['rooms_count'] = int(item['tip']) - 19
                elif item['tip'] in ['2', '3', '4']:
                    category = Category.objects.get(pk=2)  # аренда комнат
                elif item['tip'] in ['6', '7', '8', '9', '10', '26']:
                    category = Category.objects.get(pk=3)  # аренда домов
                elif item['tip'] in ['18', '46']:
                    category = Category.objects.get(pk=4)  # аренда земли
                elif item['tip'] == '19':
                    category = Category.objects.get(pk=5)  # аренда гаражей
                else:
                    category = Category.objects.get(pk=6)  # помещений
            else:
                if item['tip'] in ['20', '21', '22', '23', '24', '25']:
                    category = Category.objects.get(pk=8)  # продажа квартир
                    if item['tip'] != '25':
                        ad['rooms_count'] = int(item['tip']) - 19
                elif item['tip'] in ['2', '3', '4', '5']:
                    category = Category.objects.get(pk=9)  # продажа комнат
                elif item['tip'] in ['6', '7', '8', '9', '10', '26']:
                    category = Category.objects.get(pk=10)  # продажа домов
                elif item['tip'] in ['18', '46']:
                    category = Category.objects.get(pk=11)  # продажа земли
                elif item['tip'] == '19':
                    category = Category.objects.get(pk=12)  # продажа гаражей
                else:
                    category = Category.objects.get(pk=13)  # помещений

        ad['category'] = category
        # print(category)
        if sub_category:
            ad['sub_category'] = sub_category
        #     print(sub_category)
        # raw_input('Next')
        # print('---------------------------------------------------')
        return ad

    @classmethod
    def get_ads(cls):
        errors = 5
        match = {'cena': 'price', 'datap': 'pub_date', 'dom_etag': 'floor_max', 'etag': 'floor',
                 'kol_komn': 'rooms_count', 'pl1': 'area_living', 'plk': 'area_kitchen', 'plosh': 'area',
                 'pl_land': 'area_land', 'textob': 'desc'}

        now = datetime.now().strftime("%Y-%m-%d")
        yesterday = (date.today() - timedelta(1)).strftime("%Y-%m-%d")

        data = {
            're_base_name': 'kvart',
            're_base_section': 'green',
            'rem': 0,
            'subq_start': 0,
            'subq_lines': 200,
            'order_by[data]': 'desc',
            'order_by[datap]': 'desc',
            'data_start': yesterday,
            'data_end': now,
        }
        statistic = {}
        log = ""
        try:
            for table in ['arenda', 'kvart', 'komn', 'domm', 'negil', 'client']:  #  all tales
                data['re_base_name'] = table
                print('Load from ' + table)
                statistic[table] = {}
                for private_type in ['green']:  #['green', 'red']:  # all bases
                    statistic[table][private_type] = 0
                    print('table type ' + private_type)
                    data['re_base_section'] = private_type
                    current = 0
                    total = 200
                    while current < total:   # all pages
                        print('select 200 starts from ' + str(current) + ', total is ' + str(total))
                        data['subq_start'] = current
                        str_data = urllib.urlencode(data)
                        content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/real-estate-database.php', str_data)
                        current += 200
                        if 're_base_query_count' in content:
                            total = int(content['re_base_query_count'])

                        if 'items' not in content and errors:
                            print("hasn't content , errors left %d" % errors)
                            errors -= 1
                            print(content)
                            time.sleep((6-errors)*10)
                            current -= 200
                            continue
                        assert 'items' in content, 'unexpected content: ' + str(content)

                        if content['items'] is False:
                            break
                        for item in content['items'].values():
                            aid = item['kod']
                            try:
                                existed = Ad.objects.get(gkey=aid)
                                print(str(existed) + ' already imported!')
                                continue
                            except Ad.DoesNotExist:
                                pass

                            ad_item = {'gkey': aid}
                            for field in item:
                                if item[field] and field in match:
                                    ad_item[match[field]] = item[field]

                            ad = cls.parse_categories(ad_item, item, table)
                            # continue
                            if 'sub_category' in ad:
                                print(ad['sub_category'])
                            if 'rooms_count' in ad:
                                print('rooms: ' + str(ad['rooms_count']))

                            if item['textob']:
                                ad['title'] = truncatesmart(item['textob'], 45)
                                if not ad['title']:
                                    ad['title'] = item['textob'][:45]

                            ad['offering'] = table != 'client'
                            ad['private'] = private_type == 'green'
                            ad['phone'] = ""
                            for i in range(1, 5):
                                name = 'tel'+str(i)
                                if name in item and item[name].strip():
                                    if i > 1:
                                        ad['phone'] += ', '
                                    ad['phone'] += item[name].strip()

                            if item['metro']:
                                try:
                                    metro = Metro.objects.get(pk=item['metro'])
                                    ad['desc'] += ' ' + metro.name
                                except Metro.DoesNotExist:
                                    pass

                            if item['ulica']:
                                try:
                                    ad['address'] = Street.objects.get(pk=item['ulica'])
                                except Street.DoesNotExist:
                                    pass

                            if item['raj']:
                                try:
                                    ad['district'] = District.objects.get(pk=item['raj'])
                                except District.DoesNotExist:
                                    pass

                            if item['nasp']:
                                item['nasp'] = 1 if item['nasp'] == '293' else item['nasp']
                                try:
                                    ad['town'] = Town.objects.get(pk=item['nasp'])
                                except Town.DoesNotExist:
                                    continue

                            if ad['pub_date']:
                                pub_date = dateutil.parser.parse(ad['pub_date'])
                                if str(pub_date.time()) == "00:00:00":
                                    pub_date = datetime.combine(pub_date.date(), datetime.now().time())

                                pub_date_utc = pub_date.replace(tzinfo=timezone.get_current_timezone())
                                ad['pub_date'] = ad['order_date'] = pub_date_utc

                            if item['fotosite'] and item['fotosite'].find('&have_images'):
                                ad['url'] = item['fotosite'].replace('&have_images', '')

                            ad_obj = Ad(**ad)
                            ad_obj.save()
                            statistic[table][private_type] += 1

                            find_similar.delay(ad_obj.id)
                            if ad_obj.url:
                                parsed_uri = urlparse(ad_obj.url)
                                if parsed_uri.netloc in Crawler.DOMAINS:
                                    import_attachments.delay(ad_obj.id)

                            print(ad_obj)
                            time.sleep(1)
        except:
            log += "Error: " + traceback.format_exc() + "\n"
            raise
        finally:
            for name, stats in statistic.items():
                log += name + ': '
                if 'green' in stats:
                    log += str(stats['green'])
                log += " / "
                if 'red' in stats:
                    log += str(stats['red'])
                log += "\n"
            send_log(log)
