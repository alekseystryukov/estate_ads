# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import ads.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('rudeword', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offering', models.BooleanField(default=True, db_index=True)),
                ('disabled', models.BooleanField(default=False, db_index=True)),
                ('private', models.BooleanField(default=False, db_index=True)),
                ('blocked', models.NullBooleanField(default=False, db_index=True)),
                ('viewed', models.IntegerField(default=0)),
                ('activation_key', models.CharField(default=None, max_length=40, null=True, verbose_name='activation key', blank=True)),
                ('title', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=50)),
                ('desc', models.TextField()),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date published', blank=True)),
                ('mod_date', models.DateTimeField(null=True, verbose_name=b'date modified', blank=True)),
                ('order_date', models.DateTimeField(default=django.utils.timezone.now, db_index=True, verbose_name=b'for order', blank=True)),
                ('address', models.CharField(max_length=100, null=True, blank=True)),
                ('lat', models.DecimalField(null=True, max_digits=20, decimal_places=16, blank=True)),
                ('lon', models.DecimalField(null=True, max_digits=20, decimal_places=16, blank=True)),
                ('phone', models.CharField(max_length=50, null=True, blank=True)),
                ('price', models.IntegerField(null=True, blank=True)),
                ('price_negotiated', models.BooleanField(default=False)),
                ('gkey', models.CharField(db_index=True, max_length=20, null=True, blank=True)),
                ('url', models.CharField(max_length=200, null=True, blank=True)),
                ('premium_to', models.DateTimeField(null=True, blank=True)),
                ('rooms_count', models.IntegerField(max_length=2, null=True, blank=True)),
                ('area_living', models.IntegerField(null=True, blank=True)),
                ('area_kitchen', models.IntegerField(null=True, blank=True)),
                ('area', models.IntegerField(null=True, blank=True)),
                ('floor', models.IntegerField(max_length=2, null=True, blank=True)),
                ('floor_max', models.IntegerField(max_length=2, null=True, blank=True)),
                ('free_from', models.DateField(null=True, blank=True)),
                ('distance', models.IntegerField(max_length=4, null=True, blank=True)),
                ('area_land', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'ordering': ['-order_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
                ('slug', models.CharField(unique=True, max_length=50, db_index=True)),
                ('form_add', models.CharField(blank=True, max_length=25, null=True, choices=[(b'AdFormApartment', b'Apartment Form'), (b'AdFormRoom', b'Room Form'), (b'AdFormHouse', b'House Form'), (b'AdFormLand', b'Land Form'), (b'AdFormPrice', b'Form with price'), (b'AdFormPremises', b'Premises Form')])),
                ('form_filter', models.CharField(blank=True, max_length=25, null=True, choices=[(b'PriceSearchForm', b'Price Search Form'), (b'RoomSearchForm', b'Room Search Form'), (b'FilterSearchForm', b'Base Empty Form'), (b'HouseSearchForm', b'House Search Form'), (b'ApartmentSearchForm', b'Apartment Search Form')])),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComparedCategory',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('category', models.ForeignKey(to='ads.Category', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComparedDistrict',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComparedOffering',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('value', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComparedPriceNeg',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('value', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ComparedPrivate',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('value', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='District',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
            ],
            options={
                'ordering': ['name_ru'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', ads.db_fields.ContentTypeRestrictedFileField(upload_to=b'img')),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date upload', blank=True)),
                ('order', models.IntegerField(null=True)),
                ('ad', models.ForeignKey(to='ads.Ad', null=True)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', ads.db_fields.ContentTypeRestrictedFileField(upload_to=b'import')),
                ('settings', models.FileField(null=True, upload_to=b'import/settings', blank=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date upload')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Metro',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PaidOption',
            fields=[
                ('uid', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
                ('desc', models.TextField()),
                ('cost', models.IntegerField()),
                ('duration', models.IntegerField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
                ('country', models.ForeignKey(to='ads.Country')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Street',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
                ('form_add', models.CharField(blank=True, max_length=25, null=True, choices=[(b'AdFormApartment', b'Apartment Form'), (b'AdFormRoom', b'Room Form'), (b'AdFormHouse', b'House Form'), (b'AdFormLand', b'Land Form'), (b'AdFormPrice', b'Form with price'), (b'AdFormPremises', b'Premises Form')])),
                ('form_filter', models.CharField(blank=True, max_length=25, null=True, choices=[(b'PriceSearchForm', b'Price Search Form'), (b'RoomSearchForm', b'Room Search Form'), (b'FilterSearchForm', b'Base Empty Form'), (b'HouseSearchForm', b'House Search Form'), (b'ApartmentSearchForm', b'Apartment Search Form')])),
                ('category', models.ForeignKey(to='ads.Category')),
            ],
            options={
                'verbose_name_plural': 'SubCategories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Town',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_ru', models.CharField(max_length=50, null=True)),
                ('name_en', models.CharField(max_length=50, null=True, blank=True)),
                ('name_uk', models.CharField(max_length=50, null=True, blank=True)),
                ('region', models.ForeignKey(to='ads.Region')),
            ],
            options={
                'ordering': ['name_ru'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VideoAttachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', ads.db_fields.ContentTypeRestrictedFileField(upload_to=b'video')),
                ('type', models.CharField(max_length=15, null=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date upload', blank=True)),
                ('ad', models.ForeignKey(to='ads.Ad', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='VisitHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'date visited')),
                ('ad', models.ForeignKey(to='ads.Ad')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='visithistory',
            unique_together=set([('user', 'ad')]),
        ),
        migrations.AddField(
            model_name='district',
            name='town',
            field=models.ForeignKey(to='ads.Town', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compareddistrict',
            name='district',
            field=models.ForeignKey(to='ads.District', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='compareddistrict',
            name='town',
            field=models.ForeignKey(to='ads.Town', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comparedcategory',
            name='sub_category',
            field=models.ForeignKey(to='ads.SubCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='category',
            field=models.ForeignKey(to='ads.Category'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='district',
            field=models.ForeignKey(blank=True, to='ads.District', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='imported',
            field=models.ForeignKey(blank=True, to='ads.ImportFile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='rude_words',
            field=models.ManyToManyField(to='rudeword.RudeWord', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='similar',
            field=models.ManyToManyField(to='ads.Ad', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='sub_category',
            field=models.ForeignKey(blank=True, to='ads.SubCategory', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='town',
            field=models.ForeignKey(to='ads.Town'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ad',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]
