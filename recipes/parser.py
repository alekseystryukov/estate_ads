import urllib2
from urllib2 import Request
from bs4 import BeautifulSoup
from urlparse import urlparse, urlunparse
import re


# elements = select(soup, 'td.offer')
# result = []
# for elem in elements:
#     result.append({
#         'title': select(elem, '.detailsLink span')[0].string,
#         'price': select(elem, '.price strong')[0].string.strip()
#     })

class Crawler():

    DOMAINS = ['www.kharkovforum.com', 'fn.ua', 'premier.ua']

    def __init__(self):
        pass

    @classmethod
    def soup_from_url(cls, url):
        req = Request(url)
        try:
            html = urllib2.urlopen(req)
        except urllib2.HTTPError, error:
            print(error.read())
            return None
        return BeautifulSoup(html.read())

    @classmethod
    def url_encode_non_ascii(cls, b):
        return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

    @classmethod
    def iri_to_uri(cls, iri):
        parts = urlparse(iri)
        return urlunparse(
            part.encode('idna') if parti == 1 else cls.url_encode_non_ascii(part.encode('utf-8'))
            for parti, part in enumerate(parts)
        )

    @classmethod
    def get_from_khforum(cls, url):    # 'http://www.kharkovforum.com/showthread.php?t=4134890'
        soup = cls.soup_from_url(url)
        res = []
        if soup:
            content = soup.select('a .thumbnail')
            for node in content:
                links = node.findParents('a')
                if links:
                    href = links[0].get('href')
                    if href:
                        res.append(cls.iri_to_uri('http://www.kharkovforum.com/' + href))

        return res

    @classmethod
    def get_from_fnua(cls, url):  # http://fn.ua/view.php?ad_id=6421062
        soup = cls.soup_from_url(url)
        res = []
        if soup:
            content = soup.select('#ad-thumbs li a')
            for node in content:
                href = node.get('href')
                if href:
                    res.append(cls.iri_to_uri('http://fn.ua' + href[1:]))
        return res

    @classmethod
    def get_from_premier(cls, url):  # http://premier.ua/adv-9094511.aspx
        soup = cls.soup_from_url(url)
        res = []
        if soup:
            content = soup.select('.adv-imgs a')
            for node in content:
                href = node.get('href')
                if href:
                    res.append(cls.iri_to_uri('http://premier.ua' + href))

        return res

    @classmethod
    def get_attacments_urls(cls, url):
        parsed_uri = urlparse(url)
        if parsed_uri.netloc == 'www.kharkovforum.com':
            return cls.get_from_khforum(url)
        elif parsed_uri.netloc == 'fn.ua':
            return cls.get_from_fnua(url)
        elif parsed_uri.netloc == 'premier.ua':
            return cls.get_from_premier(url)
        return []