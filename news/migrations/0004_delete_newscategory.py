# Generated by Django 4.2.8 on 2025-04-13 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_initial'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NewsCategory',
        ),
    ]
