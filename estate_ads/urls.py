from django.conf.urls import include, url
from django.contrib import admin
from ads import views


from register.views import ExtendedRegistrationView
from custom_auth.forms import MyPasswordResetForm, MySetPasswordForm

from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.shortcuts import render
import settings
from filebrowser.sites import site
from django.views.generic import TemplateView
from custom_postman.views import MyWriteView as WriteView
from custom_postman.forms import ContactForm, AnonymousContactForm
from custom_auth.forms import MyAuthenticationForm
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse_lazy
from django.contrib.sitemaps.views import sitemap
from ads.models import AdSitemap, CategorySitemap, StaticViewSitemap

from faq import views as faq_views

urlpatterns = [

    url(r'^$', views.home, name='home'),

    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^email_template/', include('email_templates.urls')),

    url(r'^admin/', include(admin.site.urls)),

    url(r'^cat/(?P<slug>[^/]+)/(?P<page>\d*)/?$', views.category, name='category'),
    url(r'^ajax_get_filters/(?P<cat_id>\d+)/(?P<sub_cat_id>\d+)/$', views.ajax_get_filters, name='get_filters'),
    url(r'^ajax_get_dist_opts/(?P<town_id>\d+)/$', views.get_district_opts, name='get_district_opts'),

    url(r'^detail/(?P<slug>[^/]+)/(?P<ad_id>\d+)/$', views.detail, name='detail'),
    url(r'^send_to_friend/$', views.ajax_send_to_friend, name='send_to_friend'),

    url(r'^post_ad/$', views.post_ad, name='post_ad'),
    url(r'^post_ad/(?P<ad_id>\d+)/$', views.edit_ad, name='edit_ad'),
    url(r'^ajax_get_fields/(?P<cat_id>\d+)/(?P<sub_cat_id>\d+)/$', views.ajax_get_fields, name='get_fields'),
    url(r'^file_upload/(?P<ftype>\w+)/$', views.file_upload, name='file_upload'),
    url(r'^paid_option/(?P<option_id>\w+)/(?P<ad_id>\w+)/$', views.paid_option, name='paid_option'),

    url(r'^activate_ad/(?P<ad_id>\d+)/(?P<activation_key>\w*)/$', views.activate_ad_key, name='activate_ad_key'),
    url(r'^activate_ad/(?P<ad_id>\d+)/$', views.activate_ad, name='activate_ad'),


    url(r'^search/autocomplete/$',  views.autocomplete, name='search_autocomplete'),
    url(r'^search/(?P<page>\d+)/',  views.search, name='search'),
    url(r'^search/',  views.search, name='search'),

    url(r'^i18n/', include('django.conf.urls.i18n')),

    url(r'^feedback/', include('feedback.urls'), name='feedback'),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^faq/', include('faq.urls')),
    url(r'^terms/$', faq_views.terms, name='terms'),

    url(r'^messages/contact/(?:(?P<recipients>[^/#]+)/)?$',
        WriteView.as_view(form_classes=(ContactForm, AnonymousContactForm)), name='postman_contact'),
    url(r'^messages/write/', RedirectView.as_view(url=reverse_lazy('postman_inbox'))),
    url(r'messages/', include('postman.urls')),


    url(r'^accounts/login/?$', 'django.contrib.auth.views.login',
        {'template_name': 'registration/login.html', 'authentication_form': MyAuthenticationForm}),
    url(r'^accounts/register/$', ExtendedRegistrationView.as_view()),
    url(r'^accounts/password/change/$', auth_views.password_change, name='password_change'),
    url(r'^accounts/password/reset/complete/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^accounts/password/reset/$', auth_views.password_reset,  kwargs={'password_reset_form': MyPasswordResetForm},
        name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.password_reset_confirm,
        kwargs={'set_password_form': MySetPasswordForm}, name='password_reset_confirm'),
    url(r'^accounts/password/change/done/$', auth_views.password_change_done, name='password_change_done'),  # auth_password_change_done
    url(r'^accounts/password/reset/done/$', auth_views.password_reset_done, name='password_reset_done'),  # bug auth_password_reset_done
    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^profile/', views.profile, name='profile'),
    url(r'^profile_ads/(?P<page>\d+)/$', views.profile_ads, name='profile_ads'),
    url(r'^visits/(?P<page>\d+)/$', views.profile_visits, name='profile_visits'),

    url(r'^ajax_task_state/$', views.ajax_task_state, name='ajax_task_state'),

    url(r'^sitemap\.xml$', sitemap, {'sitemaps': {'categories': CategorySitemap, 'ads': AdSitemap,
                                                  'static': StaticViewSitemap}},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt$', include('robots.urls')),

    url(r'^404$', lambda r: render(r, 'errors/404.html', {'body_cls': 'errorPage'}), name='error404'),
    url(r'^500$', lambda r: render(r, 'errors/500.html', {'body_cls': 'errorPage'}), name='error500'),

    url(r'^locale/$', 'ads.views.view_locale'),


]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'ads.views.error404'
handler500 = 'ads.views.error500'
