from settings import *

SITE_ID = 1


DEBUG = TEMPLATE_DEBUG = False




DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'onchange',
        'USER': 'onchange',
        'PASSWORD': 'dopler',
        'HOST': 'localhost',
    }
}

# MEM CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': 'unix:/tmp/memcached.sock',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'localhost:9200/',
        'INDEX_NAME': 'haystack',
        'TIMEOUT': 60 * 5,
    },
}