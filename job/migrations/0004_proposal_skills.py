# Generated by Django 5.1.4 on 2025-01-16 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0003_proposal'),
    ]

    operations = [
        migrations.AddField(
            model_name='proposal',
            name='skills',
            field=models.ManyToManyField(related_name='proposals', to='job.skill'),
        ),
    ]
