#!/usr/bin/env python
# -*- coding: utf-8 -*-

import httplib
import urllib 
import urllib2

from StringIO import StringIO
import gzip

from bs4 import BeautifulSoup
import json


from ads.models import District, Town


class Crawler():
    headers = {
        'Host': 'estate-in-kharkov.com',
        'Connection': 'keep-alive',
        'Origin': 'http://estate-in-kharkov.com',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1',
        'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-encoding': 'gzip',
        'Referer': 'http://estate-in-kharkov.com/index.php',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,fr;q=0.2',
        'Cookie': 'autorized=db7cc77b5fcbc094ecfe29822a100172; login=smitholeg'
    }

    def __init__(self):
        pass

    @classmethod
    def get(cls, url):
        req = urllib2.Request(url, None, Crawler.headers)
        response = urllib2.urlopen(req)

        response_headers = response.info()

        if response_headers.get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
            print('unzipped')
        else:
            content = response.read()

        # encoding = response_headers['Content-Type'].split('charset=')[-1]
        # content = unicode(content, encoding)

        return json.loads(content)

    @classmethod
    def get_districts(cls):
        town = Town.objects.get(pk=1)
        from django.conf import settings
        print(settings.LANGUAGES)
        #content = cls.get('http://estate-in-kharkov.com/ps/re_base/ajax/raj-list.php')
        # for key, item in content.items():
        #     did = key[1:]
        #     dist, created = District.objects.get_or_create(pk=did, defaults={'name_en': item[1], 'name_ru': item[1],
        #                                                                      'name_uk': item[1], 'long_name_en': item[0],
        #                                                                      'long_name_ru': item[0], 'long_name_uk': item[0],
        #                                                                     'town': town})
           # print(dist)


    @staticmethod
    def test():
        data = {
            're_base_name': 'kvart',
            're_base_section': 'green',
            'rem': 0,
            'subq_start': 0,
            'subq_lines': 200,
            'order_by[data]': 'desc',
            'order_by[datap]': 'desc'
        }
        data = urllib.urlencode(data)
        print data
        req = urllib2.Request('http://estate-in-kharkov.com/ps/re_base/ajax/real-estate-database.php', data, Crawler.headers)
        #req = urllib2.Request('http://estate-in-kharkov.com/ps/re_base/ajax/an-list.php', None, headers)

        #encoding = req.headers['content-type'].split('charset=')[-1]
        #print(encoding)
        response = urllib2.urlopen(req)

        response_headers = response.info()
        encoding = response_headers['Content-Type'].split('charset=')[-1]

        if response_headers.get('Content-Encoding') == 'gzip':
            buf = StringIO(response.read())
            f = gzip.GzipFile(fileobj=buf)
            content = f.read()
            print('unzipped')
        else:
            content = response.read()

        #print(content)

        #print(encoding)
        #encoding = 'latin-1'
        #ucontent = unicode(content, encoding)
        print(content)

        soup = BeautifulSoup(content)
        print(soup.contents[0])

        # with open("Failed.py", "w") as text_file:
        #     text_file.write(soup.contents[0])

