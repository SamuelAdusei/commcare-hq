# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-07-23 15:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tour', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='guidedtour',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='guidedtour',
            name='user',
        ),
        migrations.DeleteModel(
            name='GuidedTour',
        ),
    ]