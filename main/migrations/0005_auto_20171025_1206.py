# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-25 12:06
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_image_primary_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='is_placeholder',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='image',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.Product'),
        ),
        migrations.AlterField(
            model_name='image',
            name='title',
            field=models.CharField(blank=True, help_text='(Optional) Image title to show.', max_length=80, null=True, unique=True),
        ),
    ]
