# Generated by Django 5.1.4 on 2025-01-07 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Certificate',
            fields=[
                ('certificate_id', models.AutoField(primary_key=True, serialize=False)),
                ('certificate_title', models.CharField(blank=True, max_length=255, null=True)),
                ('certificate_issuer', models.CharField(blank=True, max_length=255, null=True)),
                ('certificate_file', models.CharField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('issue_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'certificates',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('education_id', models.AutoField(primary_key=True, serialize=False)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('university', models.CharField(blank=True, max_length=255, null=True)),
                ('degree', models.CharField(blank=True, max_length=255, null=True)),
                ('start_year', models.DateField(blank=True, null=True)),
                ('end_year', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'educations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('experience_id', models.AutoField(primary_key=True, serialize=False)),
                ('job_title', models.CharField(blank=True, max_length=255, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('work_description', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'experiences',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Portfolio',
            fields=[
                ('portfolio_id', models.AutoField(primary_key=True, serialize=False)),
                ('project_title', models.CharField(max_length=255)),
                ('project_role', models.CharField(blank=True, null=True)),
                ('project_description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'portfolios',
                'managed': False,
            },
        ),
    ]