# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FaqArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_ru', models.CharField(max_length=100, null=True)),
                ('title_en', models.CharField(max_length=100, null=True, blank=True)),
                ('title_uk', models.CharField(max_length=100, null=True, blank=True)),
                ('slug', models.CharField(max_length=100, editable=False)),
                ('desc_ru', models.TextField(null=True, verbose_name=b'text')),
                ('desc_en', models.TextField(null=True, verbose_name=b'text', blank=True)),
                ('desc_uk', models.TextField(null=True, verbose_name=b'text', blank=True)),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name=b'date published')),
                ('disabled', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'FAQ article',
                'verbose_name_plural': 'FAQ articles',
            },
            bases=(models.Model,),
        ),
    ]
