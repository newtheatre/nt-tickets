# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2019-06-13 19:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pricing', '0003_auto_20190526_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='stuffpasspricing',
            name='performer_pass',
            field=models.DecimalField(decimal_places=2, default=10.0, max_digits=6),
        ),
    ]