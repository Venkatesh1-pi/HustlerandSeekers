# Generated by Django 5.1.7 on 2025-05-09 07:46

import hustler_role_category.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_id', models.CharField(blank=True, max_length=100, null=True)),
                ('category_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sender_id', models.CharField(blank=True, max_length=100, null=True)),
                ('receiver_id', models.CharField(blank=True, max_length=100, null=True)),
                ('message', models.CharField(blank=True, max_length=500, null=True)),
                ('status', models.CharField(blank=True, max_length=500, null=True)),
                ('attachment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsersCategory',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('role_category_name', models.CharField(blank=True, max_length=100, null=True)),
                ('summary', models.CharField(blank=True, max_length=500, null=True)),
                ('about_yourself', models.CharField(blank=True, max_length=500, null=True)),
                ('price', models.CharField(blank=True, max_length=255, null=True)),
                ('location', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.CharField(blank=True, max_length=255, null=True)),
                ('longitude', models.CharField(blank=True, max_length=255, null=True)),
                ('image1', hustler_role_category.models.Base64ImageField(blank=True, null=True)),
                ('image2', hustler_role_category.models.Base64ImageField(blank=True, null=True)),
                ('image3', hustler_role_category.models.Base64ImageField(blank=True, null=True)),
                ('video', hustler_role_category.models.Base64VideoField(blank=True, null=True)),
                ('twitter_link', models.CharField(blank=True, max_length=255, null=True)),
                ('isnta_link', models.CharField(blank=True, max_length=255, null=True)),
                ('fb_link', models.CharField(blank=True, max_length=255, null=True)),
                ('linkedin_link', models.CharField(blank=True, max_length=255, null=True)),
                ('yt_link', models.CharField(blank=True, max_length=255, null=True)),
                ('other_link', models.CharField(blank=True, max_length=255, null=True)),
                ('is_primary', models.IntegerField(choices=[(0, 'No'), (1, 'Yes')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UsersPosts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(blank=True, max_length=100, null=True)),
                ('summary', models.CharField(blank=True, max_length=500, null=True)),
                ('video', models.FileField(blank=True, null=True, upload_to='users/posts/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
