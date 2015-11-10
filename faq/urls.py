from django.conf.urls import patterns
from django.conf.urls import url
from faq import views as faq_views



urlpatterns = patterns('',
                       url(r'^$', faq_views.home, name='faq'),
                       url(r'^(?P<slug>[\w-]+)/(?P<article_id>\d+)/$', faq_views.detail, name='faq_article'),
                       )