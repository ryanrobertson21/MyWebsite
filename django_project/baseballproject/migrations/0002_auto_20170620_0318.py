# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-20 07:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseballproject', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='docfile',
            field=models.FileField(upload_to=b'documents/%H%M%S'),
        ),
    ]