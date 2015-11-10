# coding=utf-8
import os
from django.db import models
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.forms import HiddenInput
from datetime import datetime, timedelta
from django.utils import timezone
from easymode.i18n.decorators import I18n
from django.utils.translation import ugettext_lazy as _
from estate_ads import settings

from ads.db_fields import ContentTypeRestrictedFileField

import hashlib
import random
import time
from slugify import slugify

from email_templates.models import EmailTemplate
from rudeword.models import RudeWord

import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from haystack.query import SearchQuerySet
from django.contrib.auth import get_user_model



FORMS = (('AdFormApartment', 'Apartment Form'), ('AdFormRoom', 'Room Form'), ('AdFormHouse', 'House Form'),
         ('AdFormLand', 'Land Form'), ('AdFormPrice', 'Form with price'), ('AdFormPremises', 'Premises Form'), )
FILTERS = (('PriceSearchForm', 'Price Search Form'), ('RoomSearchForm', 'Room Search Form'),
           ('FilterSearchForm', 'Base Empty Form'),
           ('HouseSearchForm', 'House Search Form'), ('ApartmentSearchForm', 'Apartment Search Form'),)


@I18n('name')
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.CharField(max_length=50, unique=True, db_index=True)  # ,,
    form_add = models.CharField(max_length=25, choices=FORMS, null=True, blank=True)
    form_filter = models.CharField(max_length=25, choices=FILTERS, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ads.views.category', args=[self.slug, 1])

    def save(self, **kwargs):
        self.slug = slugify(self.name_uk)
        if not Category.objects.filter(slug=self.slug).exclude(pk=self.id).exists():
            super(Category, self).save(**kwargs)

    @property
    def search_form(self):
        from ads import forms
        form_class = self.form_filter if self.form_filter else 'FilterSearchForm'
        try:
            return getattr(forms, form_class)
        except AttributeError:
            return forms.FilterSearchForm




@I18n('name')
class SubCategory(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category)
    form_add = models.CharField(max_length=25, choices=FORMS, null=True, blank=True)
    form_filter = models.CharField(max_length=25, choices=FILTERS, null=True, blank=True)

    class Meta:
        verbose_name_plural = "SubCategories"

    def __unicode__(self):
        return self.name


@I18n('name')
class Country(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


@I18n('name')
class Region(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country)

    def __unicode__(self):
        return self.name


@I18n('name')
class Town(models.Model):
    name = models.CharField(max_length=50)
    region = models.ForeignKey(Region)

    class Meta:
        ordering = ['name_ru']

    def __unicode__(self):
        return self.name


@I18n('name')
class District(models.Model):
    town = models.ForeignKey(Town, null=True)
    name = models.CharField(max_length=50)

    class Meta:
        ordering = ['name_ru']

    def __unicode__(self):
        return self.name


class Street(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class Metro(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name



def get_upload_path(filename, path_prefix):
    import os.path
    now = datetime.now()
    return os.path.join(path_prefix, str(now.year), str(now.month), str(now.day), filename)


class ImportFile(models.Model):
    file = ContentTypeRestrictedFileField(upload_to=settings.IMPORT_UPLOAD_PATH,
                                          #upload_to=lambda instance, filename: get_upload_path(filename, settings.IMPORT_UPLOAD_PATH),
                                          content_types=settings.IMPORT_TYPES,
                                          max_upload_size=settings.IMPORT_MAX_SIZE)
    settings = models.FileField(null=True, blank=True, upload_to=settings.IMPORT_SETTINGS_PATH)
    date = models.DateTimeField('date upload', default=timezone.now)

    def __unicode__(self):
        return self.file.name


class Ad(models.Model):

    offering = models.BooleanField(default=True, db_index=True)  # there is two types of ads: people may looking or suggest estate
    disabled = models.BooleanField(default=False, db_index=True)
    private = models.BooleanField(default=False, db_index=True)
    blocked = models.NullBooleanField(default=False, db_index=True)
    rude_words = models.ManyToManyField(RudeWord, null=True, blank=True)
    viewed = models.IntegerField(default=0)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    activation_key = models.CharField(_('activation key'), max_length=40, null=True, blank=True, default=None)

    title = models.CharField(max_length=50)
    slug = models.CharField(max_length=50)
    desc = models.TextField()
    pub_date = models.DateTimeField('date published', default=timezone.now, blank=True)
    mod_date = models.DateTimeField('date modified', null=True, blank=True)
    order_date = models.DateTimeField('for order', default=timezone.now, blank=True, db_index=True)
    town = models.ForeignKey(Town)
    district = models.ForeignKey(District, null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=100)
    lat = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)
    lon = models.DecimalField(max_digits=20, decimal_places=16, null=True, blank=True)
    category = models.ForeignKey(Category)
    sub_category = models.ForeignKey(SubCategory, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    price_negotiated = models.BooleanField(default=False)

    imported = models.ForeignKey(ImportFile, null=True, blank=True)
    gkey = models.CharField(max_length=20, null=True, db_index=True, blank=True)
    url = models.CharField(max_length=200, null=True, blank=True)

    premium_to = models.DateTimeField(null=True, blank=True)
    similar = models.ManyToManyField('self', symmetrical=False, blank=True)
    # appartments fields
    rooms_count = models.IntegerField(max_length=2, null=True, blank=True)
    area_living = models.IntegerField(null=True, blank=True)
    area_kitchen = models.IntegerField(null=True, blank=True)
    area = models.IntegerField(null=True, blank=True)
    floor = models.IntegerField(max_length=2, null=True, blank=True)
    floor_max = models.IntegerField(max_length=2, null=True, blank=True)
    free_from = models.DateField(null=True, blank=True)
    distance = models.IntegerField(max_length=4, null=True, blank=True)
    area_land = models.IntegerField(null=True, blank=True)

    fields_for_analyse = ['title', 'desc', 'address']  # looking for rude words

    def save(self, **kwargs):
        self.mod_date = timezone.now()
        self.slug = slugify(self.title)
        if self.district_id and self.town_id is None:  # hasattr(self, 'district') and
            self.town = self.district.town
        super(Ad, self).save(**kwargs)

        # cache invalidation
        if 'update_fields' in kwargs and set(kwargs['update_fields']) - {'viewed'}:
            cache.delete('detail_%s' % self.id)

    @staticmethod
    def filter_field(value, field):
        field = Ad._meta.get_field(field)
        if field.max_length:
            value = value[:field.max_length]
        return value

    def set_premium(self, duration):
        self.premium_to = timezone.now()+timedelta(days=duration)

    def set_vip(self, duration):
        self.order_date = timezone.now()+timedelta(days=duration)

    class Meta:
        ordering = ['-order_date']
        #  index_together = [["title"], ]

    def __unicode__(self):
        return self.title

    @staticmethod
    def get_form_class(category=None, sub_category=None, offering=None):
        from ads import forms
        if offering:
            form_class = 'AdForm'
            if sub_category:
                cat = sub_category if isinstance(sub_category, SubCategory) else SubCategory.objects.get(pk=sub_category)
                if cat.form_add:
                    form_class = cat.form_add
                elif cat.category.form_add:
                    form_class = cat.category.form_add
            elif category:
                cat = category if isinstance(category, Category) else Category.objects.get(pk=category)
                if cat.form_add:
                    form_class = cat.form_add
        else:
            form_class = 'AdLookingFormMore' if category or sub_category else 'AdLookingForm'
        try:
            form = getattr(forms, form_class)
        except AttributeError:
            form = forms.AdForm
        return form

    @staticmethod
    def get_search_form(request, category=None):
        from ads import forms
        if request.GET.get('offering'):
            return forms.FilterSearchForm

        form_class = category.form_filter if category and category.form_filter else 'FilterSearchForm'
        try:
            return getattr(forms, form_class)
        except AttributeError:
            return forms.FilterSearchForm

    @staticmethod
    def save_files(post, obj):
        if 'images[]' in post:
            ids = post.getlist('images[]')
            ImageAttachment.objects.filter(ad=obj).exclude(pk__in=ids).delete()

            order = 0
            for img_id in ids:
                img = ImageAttachment.objects.get(pk=img_id)
                img.ad = obj
                img.order = order
                img.save()
                order += 1
        if 'video[]' in post:
            ids = post.getlist('video[]')
            VideoAttachment.objects.filter(ad=obj).exclude(pk__in=ids).delete()
            for vid_id in ids:
                img = VideoAttachment.objects.get(pk=vid_id)
                img.ad = obj
                img.save()

    def save_as_disabled(self, email):
        self.disabled = True
        salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
        if isinstance(self.title, unicode):
            key = self.title.encode('utf-8')
            self.activation_key = hashlib.sha1(salt+key).hexdigest()
        self.save()
        mail = EmailTemplate.objects.get(pk='post_ad_activation_email')
        mail.send(email, None, **self.__dict__)

    def get_absolute_url(self):
        return reverse('ads.views.detail', args=[self.slug, self.id])

    @classmethod
    def haystack_search(cls, data, autocomplete=False):
        sqs = SearchQuerySet().all()
        if data.get('q'):
            if autocomplete:
                sqs = sqs.filter(content_auto=data.get('q'))
            else:
                sqs = sqs.filter(content=data.get('q'))

        sqs = sqs.filter(town=data.get('town', 1)).filter(offering=int(not data.get('offering', False)))

        category = data.get('category')
        if category:
            sqs = sqs.filter(category=category)

        sub_category = data.get('sub_category')
        if sub_category:
            sqs = sqs.filter(sub_category=sub_category)

        district = data.get('district', '')
        if district:
            sqs = sqs.filter(district=district)

        range_fields = ['area', 'price', 'rooms_count', 'area_living', 'floor']
        field_filter = {}
        for field in range_fields:
            field_from, field_to = field+'_from', field+'_to'
            if field_from in data and data[field_from] and field_to in data and data[field_to]:
                if data[field_from] > data[field_to]:
                    field_filter[field+'__gte'] = data[field_to]
                    field_filter[field+'__lte'] = data[field_from]
                else:
                    field_filter[field+'__gte'] = data[field_from]
                    field_filter[field+'__lte'] = data[field_to]
            elif field_from in data and data[field_from]:
                field_filter[field+'__gte'] = data[field_from]
            elif field_to in data and data[field_to]:
                field_filter[field+'__lte'] = data[field_to]
        if field_filter:
            sqs = sqs.filter(**field_filter)
        return sqs

    @classmethod
    def database_search(cls, data):
        f = {}
        for k, v in data.items():
            if k != 'offering':
                f[k + '_id'] = v
        f['offering'] = not data.get('offering', False)
        return Ad.objects.filter(**f)

    @classmethod
    def search(cls, data, autocomplete=False):
        clear_data = {}
        for k, v in data.items():
            if v is not None and v != "":
                clear_data[k] = v
        if set(clear_data.keys()) - {'town', 'district', 'category', 'sub_category', 'offering'}:
            return cls.haystack_search(clear_data, autocomplete)
        else:
            return cls.database_search(clear_data)

    def add_to_visited(self, request):
        self.viewed += 1
        self.save(update_fields=["viewed"])
        if request.user.is_authenticated():
            visit, created = VisitHistory.objects.get_or_create(user=request.user, ad=self)
            visit.date = timezone.now()
            visit.save()
        else:
            request.session.setdefault('history', []).append(int(self.id))
            request.session['history'] = list(set(request.session['history']))
            request.session.modified = True


class VisitHistory(models.Model):
    ad = models.ForeignKey(Ad)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField('date visited', default=timezone.now)

    class Meta:
        unique_together = (("user", "ad"),)
        ordering = ['-date']



class ImageAttachment(models.Model):
    file = ContentTypeRestrictedFileField(#upload_to=settings.IMAGE_UPLOAD_PATH,
                                          upload_to=lambda instance, filename: get_upload_path(filename, settings.IMAGE_UPLOAD_PATH),
                                          content_types=settings.UPLOAD_IMG_TYPES,
                                          max_upload_size=settings.UPLOAD_IMG_MAX_SIZE)
    #thumbnail = models.ImageField(upload_to=settings.THUMBNAIL_UPLOAD_PATH)
    ad = models.ForeignKey(Ad, null=True)
    date = models.DateTimeField('date upload', default=timezone.now, blank=True)
    order = models.IntegerField(null=True)

    def __unicode__(self):
        return self.file.name

    class Meta:
        ordering = ['order']

    def get_remote_image(self, image_url):
        img_temp = NamedTemporaryFile(delete=True)
        try:
            img_temp.write(urllib2.urlopen(image_url.replace(" ", "%20")).read())
            print(img_temp.name)
        except urllib2.HTTPError, error:
            print(error.read())
        else:
            img_temp.flush()
            self.file.save(os.path.basename(img_temp.name) + str(int(time.time())) + '.jpg', File(img_temp))
            self.save()
            print(self.file.name)


class VideoAttachment(models.Model):
    file = ContentTypeRestrictedFileField(#upload_to=settings.VIDEO_UPLOAD_PATH,
                                          upload_to=lambda instance, filename: get_upload_path(filename, settings.VIDEO_UPLOAD_PATH),
                                          content_types=settings.UPLOAD_VIDEO_TYPES,
                                          max_upload_size=settings.UPLOAD_VIDEO_MAX_SIZE)
    #type = models.CharField(max_length=15, null=True)
    #thumbnail = models.ImageField(upload_to=settings.THUMBNAIL_UPLOAD_PATH)
    ad = models.ForeignKey(Ad, null=True)
    date = models.DateTimeField('date upload', default=timezone.now, blank=True)

    def __unicode__(self):
        return self.file.name


@I18n('name')
class PaidOption(models.Model):
    uid = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=50)
    desc = models.TextField()
    cost = models.IntegerField()
    duration = models.IntegerField(null=True, blank=True)  # days..

    def is_available(self, amount):
        return amount >= self.cost

    def __unicode__(self):
        return self.name_en


class ComparedDistrict(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    district = models.ForeignKey(District, null=True)
    town = models.ForeignKey(Town, null=True)


class ComparedCategory(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    category = models.ForeignKey(Category, null=True)
    sub_category = models.ForeignKey(SubCategory, null=True)


class ComparedPrivate(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    value = models.BooleanField(default=False)


class ComparedOffering(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    value = models.BooleanField(default=False)


class ComparedPriceNeg(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    value = models.BooleanField(default=False)


# SITEMAP MODELS

from django.contrib.sitemaps import Sitemap


class AdSitemap(Sitemap):
    changefreq = "monthly"
    priority = 1.0

    def items(self):
        return Ad.objects.filter(disabled=False, blocked=False)

    def lastmod(self, obj):
        return obj.mod_date or obj.pub_date


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['home', 'faq']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Category.objects.filter(ad__isnull=False).distinct()

    def lastmod(self, obj):
        return Ad.objects.filter(category=obj)[0].pub_date


