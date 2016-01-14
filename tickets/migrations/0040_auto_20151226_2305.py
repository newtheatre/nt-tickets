# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-26 23:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0039_auto_20151226_2118'),
    ]

    operations = [
        migrations.AddField(
            model_name='externalpricing',
            name='season_ticket_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='show',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tickets.Category'),
        ),
    ]