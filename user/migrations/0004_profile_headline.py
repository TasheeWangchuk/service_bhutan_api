# Generated by Django 5.1.4 on 2025-01-16 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_customuser_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='headline',
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
    ]
