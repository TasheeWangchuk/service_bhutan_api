# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthtokenToken(models.Model):
    key = models.CharField(primary_key=True, max_length=40)
    created = models.DateTimeField()
    user = models.OneToOneField('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'authtoken_token'


class Certificates(models.Model):
    certificate_id = models.AutoField(primary_key=True)
    profile_id = models.IntegerField()
    certificate_title = models.CharField(max_length=255, blank=True, null=True)
    certificate_issuer = models.CharField(max_length=255, blank=True, null=True)
    certificate_file = models.CharField(blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'certificates'


class Contracts(models.Model):
    contract_id = models.AutoField(primary_key=True)
    proposal = models.ForeignKey('Proposals', models.DO_NOTHING)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=50)
    payment_amount = models.FloatField()

    class Meta:
        managed = False
        db_table = 'contracts'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Educations(models.Model):
    education_id = models.AutoField(primary_key=True)
    profile_id = models.IntegerField()
    country = models.CharField(max_length=255, blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    start_year = models.DateField(blank=True, null=True)
    end_year = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'educations'


class Experiences(models.Model):
    experience_id = models.AutoField(primary_key=True)
    profile_id = models.IntegerField()
    job_title = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'experiences'


class JobSkills(models.Model):
    job = models.OneToOneField('Jobs', models.DO_NOTHING, primary_key=True)  # The composite primary key (job_id, skill_id) found, that is not supported. The first column is selected.
    skill = models.ForeignKey('Skills', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'job_skills'
        unique_together = (('job', 'skill'),)


class Jobs(models.Model):
    job_id = models.AutoField(primary_key=True)
    client_id = models.IntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=50)
    budget = models.FloatField()
    deadline = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'jobs'


class JobsCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Jobs, models.DO_NOTHING)
    category_name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'jobs_category'


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    content = models.TextField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'notification'


class Portfolios(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    profile_id = models.IntegerField()
    project_title = models.CharField(max_length=255)
    project_role = models.CharField(blank=True, null=True)
    project_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'portfolios'


class Profiles(models.Model):
    profile_id = models.AutoField(primary_key=True)
    profile_picture = models.CharField(max_length=200, blank=True, null=True)
    banner = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField('Users', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'profiles'


class Proposals(models.Model):
    proposal_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Jobs, models.DO_NOTHING)
    freelancer_id = models.IntegerField()
    cover_letter = models.TextField(blank=True, null=True)
    bid_amount = models.FloatField()
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'proposals'


class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    contract = models.ForeignKey(Contracts, models.DO_NOTHING)
    rating = models.FloatField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reviews'


class Skills(models.Model):
    skill_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = False
        db_table = 'skills'


class Users(models.Model):
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(unique=True, max_length=254)
    username = models.CharField(unique=True, max_length=100)
    password = models.CharField(max_length=128)
    confirm_password = models.CharField(max_length=128)
    cid = models.CharField(unique=True, max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    terms_check = models.BooleanField()
    role = models.CharField(max_length=50)
    is_banned = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'


class UsersGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(Users, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_groups'
        unique_together = (('customuser', 'group'),)


class UsersUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    customuser = models.ForeignKey(Users, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_user_permissions'
        unique_together = (('customuser', 'permission'),)
