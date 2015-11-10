"""
Django settings for estate_ads project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.utils.translation import ugettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=daik3b82e)^ngx+%#iv!3^+nv5j1+b+hy&rp*j9k!+2he_21t'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = TEMPLATE_DEBUG = True


ALLOWED_HOSTS = ['localhost', '159.224.7.74', '31.131.19.157', 'onchange.com.ua', 'www.onchange.com.ua']
ADMINS = MANAGERS = [("Alex", "aleksey.stryukov@gmail.com")]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'haystack',
    'registration',
    'postman',
    'captcha',
    'easy_thumbnails',
    'django_bootstrap_breadcrumbs',  # http://django-bootstrap-breadcrumbs.readthedocs.org/en/latest/

    'robots',
    'debug_toolbar',
    'memcache_status',

    'tinymce',
    'filebrowser',

    'kombu.transport.django',
    'djcelery',

    'custom_user',
    'custom_custom_user',

    'feedback',
    'email_templates',
    'rudeword',
    'register',
    'ads',
    'faq',

    "compressor",
)

MIDDLEWARE_CLASSES = (
   # 'ads.middleware.StatsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    #'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'ads.middleware.ActiveUserMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # 'django.middleware.cache.UpdateCacheMiddleware', # per site cache
    # 'django.middleware.common.CommonMiddleware',
    # 'django.middleware.cache.FetchFromCacheMiddleware',

)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "ads.processor.settings_processor",
    "ads.processor.site_processor",
    "feedback.context_processors.feedback_form",
    "django.core.context_processors.request",
    "postman.context_processors.inbox",
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # other finders..
    'compressor.finders.CompressorFinder',
)

#STATICFILES_DIRS = (os.path.join(os.path.join(BASE_DIR, "ads"), "static"), )


ROOT_URLCONF = 'estate_ads.urls'

WSGI_APPLICATION = 'estate_ads.wsgi.application'

AUTH_USER_MODEL = 'custom_custom_user.MyCustomEmailUser'
AUTHENTICATION_BACKENDS = ('django.contrib.auth.backends.ModelBackend',
                           'custom_auth.backends.AuthenticationBackendAnonymous')

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'estate_ads',
        'USER': 'estate_ads',
        'PASSWORD': 'dopler',
        #'HOST': '192.168.0.100',
        'HOST': '159.224.7.74',
    }
}



# MEM CACHE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        # 'LOCATION': 'unix:/tmp/memcached.sock',
        'LOCATION': '159.224.7.74:11211',
        'TIMEOUT': 60,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

#Search engine
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        #'URL': '192.168.0.100:9200/',
        'URL': '159.224.7.74:9200/',
        'INDEX_NAME': 'haystack',
        'TIMEOUT': 60 * 5,
    },
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'ru'

ugettext = lambda s: s

LANGUAGES = (('uk', ugettext('Ukrainian')), ('ru', ugettext('Russian')), ('en', ugettext('English')), )

TIME_ZONE = 'Europe/Kiev'

DATE_INPUT_FORMATS = ['%Y-%m-%d', '%d/%m/%Y', '%d/%m/%y']

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 2

PROTOCOL = 'http://'




# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.join(BASE_DIR, 'ads'), 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
LOCALE_PATHS = (os.path.join(BASE_DIR, 'locale'), os.path.join(os.path.join(BASE_DIR, 'ads'), 'locale'),)

IMAGE_UPLOAD_PATH = 'img'
VIDEO_UPLOAD_PATH = 'video'
THUMBNAIL_UPLOAD_PATH = 'thumb'
IMPORT_UPLOAD_PATH = 'import'
IMPORT_SETTINGS_PATH = os.path.join(IMPORT_UPLOAD_PATH, 'settings')


UPLOAD_IMG_TYPES = ['image/png', 'image/gif', 'image/jpeg', 'image/jpg']
UPLOAD_IMG_MAX_SIZE = 5242880
UPLOAD_IMG_MAX_SIZE_MB = UPLOAD_IMG_MAX_SIZE/1024
UPLOAD_IMAGES_LIMIT = 12
UPLOAD_VIDEO_TYPES = ['video/mp4', 'video/ogg', 'video/webm', 'video/x-flv']
UPLOAD_VIDEO_EXT = ['mp4', 'flv', 'webm', 'ogv', 'x-flv']
UPLOAD_VIDEO_MAX_SIZE = 429916160
UPLOAD_VIDEO_MAX_SIZE_MB = UPLOAD_VIDEO_MAX_SIZE/1024
UPLOAD_VIDEO_LIMIT = 5
IMPORT_TYPES = ['text/csv']  # text/xml
IMPORT_MAX_SIZE = 104857600  # 100MB

THUMBNAIL_ALIASES = {
    '': {
        'photo': {'size': (102, 102), 'crop': True},
        'gallery_thumb': {'size': (75, 75), 'crop': True},
    },
}

TEMPLATE_DIRS = [os.path.join(BASE_DIR, 'templates')]

ACCOUNT_ACTIVATION_DAYS = 30
REGISTRATION_AUTO_LOGIN = True
#LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 25
DEFAULT_FROM_EMAIL = 'noreply@onchange.com.ua'

EMAIL_HOST = 'smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@onchange.com.ua'
EMAIL_HOST_PASSWORD = 'onchange2015test'

# RECAPTCHA_PUBLIC_KEY = '6Lf1Tf4SAAAAAAxHYOjEEDHVHSpfmsIGVlMfjP79'
# RECAPTCHA_PRIVATE_KEY = '6Lf1Tf4SAAAAAO2BEF1dEYvwdPdy3b1_E9ACIS_9'
CAPTCHA_OUTPUT_FORMAT = '%(image)s %(ref_button)s %(hidden_field)s %(text_field)s'

PROJECT_DIR = os.path.dirname(__file__)

FEEDBACK_CHOICES = (('bug', _('Bug')), ('feature_request', _('Feature Request')),
                    ('complaint', _('Complaint')))
ALLOW_ANONYMOUS_FEEDBACK = True

# Celery

import djcelery
djcelery.setup_loader()


CELERY_IMPORTS = ("ads.tasks",)

#BROKER_URL = 'amqp://estate_ads:dopler@159.224.7.74:5672//'
#CELERY_RESULT_BACKEND = "amqp"
BROKER_URL = 'redis://localhost:6379/0'
# redis://:password@hostname:port/db_number
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_IGNORE_RESULT = False

from datetime import timedelta
from celery.schedules import crontab

CELERYBEAT_SCHEDULE = {
    'update_haystack_every_hour': {
        'task': 'ads.tasks.update_index_last_hours',
        'schedule': timedelta(seconds=3500),   # slightly less than one hour
        'args': (1,)
    },
    # 'parse_ads': {
    #     'task': 'ads.tasks.parse_ads',
    #     'schedule': crontab(hour=10, minute=50),
    #     'args': tuple(),
    # },
    # 'remove_old_crawled_from_db': {
    #     'task': 'ads.tasks.remove_old_crawled_from_db',
    #     'schedule': crontab(hour=6, minute=30),
    #     'args': tuple(),
    # },
}
# from celery.schedules import crontab
#
# CELERYBEAT_SCHEDULE = {
#     # Executes every Monday morning at 7:30 A.M
#     'add-every-monday-morning': {
#         'task': 'tasks.add',
#         'schedule': crontab(hour=7, minute=30, day_of_week=1),
#         'args': (16, 16),
#     },
# }

# celery flower --broker=amqp://estate_ads:dopler@159.224.7.74:5672//
# http://192.168.0.100:5555/

TINYMCE_DEFAULT_CONFIG = {
    'plugins': "table,spellchecker,paste,searchreplace,preview",

    'theme': "advanced",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,

    'theme_advanced_buttons3_add': "preview",
    'plugin_preview_width': "800",
    'plugin_preview_height': "900",
    'plugin_preview_pageurl': '/email_template/preview/',

    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "bottom",
    'theme_advanced_resizing': 'true',
}
TINYMCE_SPELLCHECKER = True
TINYMCE_COMPRESSOR = True

# django-filebrowser
# FILEBROWSER_DIRECTORY = os.path.join(MEDIA_ROOT, 'uploads')
VERSIONS_BASEDIR = os.path.join(MEDIA_ROOT, '_versions')


POSTMAN_DISALLOW_ANONYMOUS = True
POSTMAN_DISALLOW_MULTIRECIPIENTS = True
POSTMAN_DISALLOW_COPIES_ON_REPLY = True
POSTMAN_DISABLE_USER_EMAILING = False
POSTMAN_AUTO_MODERATE_AS = True  # True, False, None
POSTMAN_MAILER_APP = "email_templates"

#ROBOTS_CACHE_TIMEOUT = 60*60*24
