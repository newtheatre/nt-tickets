# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-06-10 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0008_auto_20190531_0236'),
    ]

    operations = [
        migrations.AddField(
            model_name='show',
            name='allow_reservations',
            field=models.BooleanField(default=True),
        ),
    ]
