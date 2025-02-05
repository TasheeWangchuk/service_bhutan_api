from django.db import models
from user.models import CustomUser
from .enums import PaymentTypeEnum, TimePreferenceEnum, ExperienceLevelEnum, LocationEnum, StatusEnum, ProposalStatusEnum


class JobCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = 'jobs_category'

class Skill(models.Model): 
    skill_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = True
        db_table = 'skills'

class Job(models.Model):
    job_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    budget = models.FloatField()
    deadline = models.DateField(blank=True, null=True)
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='jobs')
    payment_type = models.CharField(max_length=20,choices=PaymentTypeEnum.choices(),)
    time_preferences_type = models.CharField(max_length=20,choices=TimePreferenceEnum.choices(),)
    custom_time_preference = models.CharField(max_length=255,null=True,blank=True,help_text="Custom time preference if not selecting from predefined options" )
    experience_level = models.CharField(max_length=20,choices=ExperienceLevelEnum.choices(),)
    location = models.CharField(max_length=20,choices=LocationEnum.choices(),)
    status = models.CharField(max_length=20,choices=StatusEnum.choices(),default=StatusEnum.OPEN.name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    skills = models.ManyToManyField('Skill')  
    
    class Meta:
        managed = True
        db_table = 'jobs'
        
    @property
    def time_preference(self):
        if self.time_preferences_type == TimePreferenceEnum.CUSTOM.name:
            return self.custom_time_preference
        return dict(TimePreferenceEnum.choices())[self.time_preferences_type]

class Proposal(models.Model): 
    proposal_id = models.AutoField(primary_key=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='proposals')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submitted_proposals')
    cover_letter = models.TextField(blank=True, null=True)
    bid_amount = models.FloatField()
    status = models.CharField(max_length=20,choices=ProposalStatusEnum.choices(), default=ProposalStatusEnum.PENDING.name)
    created_at = models.DateTimeField(auto_now_add=True)
    skills = models.ManyToManyField('Skill', related_name='proposals')

    class Meta:
        managed = True
        db_table = 'proposals'
        unique_together = ['job', 'user']