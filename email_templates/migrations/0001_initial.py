# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('uid', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('desc', models.CharField(max_length=200)),
                ('subject', models.CharField(max_length=200)),
                ('html', models.TextField()),
                ('text', models.TextField()),
            ],
            options={
                'verbose_name': 'Mail template',
                'verbose_name_plural': 'Mail templates',
            },
            bases=(models.Model,),
        ),
    ]
