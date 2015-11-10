from django.conf.urls import url

from email_templates import views

urlpatterns = [
    url(r'^preview/$', views.preview),
]
