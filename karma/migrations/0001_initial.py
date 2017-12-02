# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('screen_name', models.CharField(unique=True, max_length=255, verbose_name=b'Twitter screen name')),
                ('twitter_id', models.CharField(max_length=255, verbose_name=b'Twitter id')),
                ('avatar', models.URLField(verbose_name=b'Twitter avatar URL', blank=True)),
                ('banned', models.BooleanField(default=0, verbose_name=b'Boolean showing if user is banned')),
                ('admin', models.BooleanField(default=0, verbose_name=b'Boolean showing if user is an admin')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.IntegerField(verbose_name=b'Amount of points')),
                ('date', models.DateTimeField()),
                ('twitter_id', models.CharField(max_length=255, verbose_name=b'Twitter id of the tweet')),
                ('text', models.TextField(blank=True)),
                ('receiver', models.ForeignKey(related_name='karma_receives', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('sender', models.ForeignKey(related_name='karma_sends', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
