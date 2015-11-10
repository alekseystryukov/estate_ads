# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RudeWord',
            fields=[
                ('id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('word', models.CharField(max_length=50)),
                ('strong', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
