# Generated by Django 5.1.4 on 2025-01-10 08:59

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0002_remove_job_profile_job_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('proposal_id', models.AutoField(primary_key=True, serialize=False)),
                ('cover_letter', models.TextField(blank=True, null=True)),
                ('bid_amount', models.FloatField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('ACCEPTED', 'Accepted'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proposals', to='job.job')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submitted_proposals', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'proposals',
                'managed': True,
                'unique_together': {('job', 'user')},
            },
        ),
    ]
