# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-13 15:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JSONConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('configuration_text', models.CharField(max_length=10000)),
                ('submit_time', models.DateTimeField(verbose_name='time received')),
                ('user_name', models.CharField(max_length=20)),
            ],
        ),
    ]
