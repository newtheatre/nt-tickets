# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-05-11 13:44
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0010_warnings_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warnings',
            name='order',
        ),
    ]
