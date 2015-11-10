# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousFeedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100, verbose_name='Type', choices=[(b'bug', b'Bug'), (b'feature_request', b'Feature Request')])),
                ('message', models.TextField(verbose_name='Message')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Time')),
                ('user', models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True, verbose_name='User')),
            ],
            options={
                'ordering': ['-time'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=100, verbose_name='Type', choices=[(b'bug', b'Bug'), (b'feature_request', b'Feature Request')])),
                ('message', models.TextField(verbose_name='Message')),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Time')),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
