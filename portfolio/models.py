from django.db import models
from django.conf import settings
from user.models import Profile
from cloudinary_storage.storage import MediaCloudinaryStorage

    
class Portfolio(models.Model):
    portfolio_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='portfolios')
    project_title = models.CharField(max_length=255)
    project_picture = models.ImageField(upload_to='portfolio/',storage=MediaCloudinaryStorage(),null=True,blank=True)
    project_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'portfolios'

class Certificate(models.Model):
    certificate_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='certificates')
    certificate_title = models.CharField(max_length=255, blank=True, null=True)
    certificate_issuer = models.CharField(max_length=255, blank=True, null=True)
    certificate_picture = models.ImageField(upload_to='certificate_picture/', storage=MediaCloudinaryStorage, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'certificates'

class Education(models.Model):
    education_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    country = models.CharField(max_length=255, blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    degree = models.CharField(max_length=255, blank=True, null=True)
    start_year = models.DateField(blank=True, null=True)
    end_year = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    class Meta:
        managed = True
        db_table = 'educations'

class Experience(models.Model):
    experience_id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    job_title = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    work_description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        db_table = 'experiences'

