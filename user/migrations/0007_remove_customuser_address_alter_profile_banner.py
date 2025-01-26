# Generated by Django 5.1.4 on 2025-01-25 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0006_alter_profile_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='address',
        ),
        migrations.AlterField(
            model_name='profile',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to='banner/'),
        ),
    ]
