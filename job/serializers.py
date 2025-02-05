from rest_framework import serializers
from .models import Job, JobCategory, Skill, Proposal
from user.serializers import UserMinimalSerializer
from django.utils import timezone


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = ('category_id', 'category_name')

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ('skill_id', 'name')

class JobSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), write_only=True)
    skills_details = SkillSerializer(source='skills', many=True, read_only=True)
    job_category = serializers.PrimaryKeyRelatedField(queryset=JobCategory.objects.all(),write_only=True)
    job_category_details = JobCategorySerializer(source='job_category', read_only=True)
    user = UserMinimalSerializer(read_only=True)
    time_preference = serializers.CharField(read_only=True)
    proposals_count = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Job
        fields = [
            'job_id',
            'user',
            'title',
            'description',
            'budget',
            'deadline',
            'job_category',
            'job_category_details',
            'payment_type',
            'time_preferences_type',
            'time_preference',
            'custom_time_preference',
            'experience_level',
            'location',
            'status',
            'created_at',
            'updated_at',
            'skills',
            'skills_details',
            'proposals_count'
        ]
        read_only_fields = ['job_id', 'user', 'status', 'created_at', 'updated_at']

    def get_proposals_count(self, obj):
        return obj.proposals.count()

    def validate_deadline(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past")
        return value

    def validate_budget(self, value):
        if value <= 0:
            raise serializers.ValidationError("Budget must be greater than zero")
        return value

    def validate(self, data):
        # Validate custom time preference
        if data.get('time_preferences_type') == 'CUSTOM' and not data.get('custom_time_preference'):
            raise serializers.ValidationError({
                "custom_time_preference": "Custom time preference is required when time preference type is CUSTOM"
            })
        
        return data
    
class JobListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    job_category_name = serializers.CharField(source='job_category.category_name')
    proposals_count = serializers.SerializerMethodField()
    skills = SkillSerializer(many=True)
    address = serializers.CharField(source='user.address',read_only=True)


    class Meta:
        model = Job
        fields = [
            'job_id',
            'title',
            'payment_type',
            'budget',
            'experience_level',
            'time_preference',
            'description',
            'job_category_name',
            'location',
            'status',
            'created_at',
            'skills',
            'proposals_count',
            'address'
        ]
        read_only_fields = fields

    def get_user_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username

    def get_proposals_count(self, obj):
        return obj.proposals.count()

class ProposalSerializer(serializers.ModelSerializer):
    skills = serializers.PrimaryKeyRelatedField(many=True, queryset=Skill.objects.all(), write_only=True)
    skills_details = SkillSerializer(source='skills', many=True, read_only=True)
    job_title = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")
    
    class Meta:
        model = Proposal
        fields = [
            'proposal_id',
            'job',
            'job_title',
            'user',
            'cover_letter',
            'bid_amount',
            'status',
            'created_at',
            'skills',
            'skills_details'
        ]
        read_only_fields = ['proposal_id', 'status', 'created_at', 'job', 'user']
         
    def get_job_title(self, obj):
        return obj.job.title if hasattr(obj.job, 'title') else None
    
    def validate_bid_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Bid amount must be greater than zero")
        return value
    
class ProposalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    user = UserMinimalSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    
    class Meta:
        model = Proposal
        fields = [
            'proposal_id',
            'user',
            'bid_amount',
            'status',
            'created_at',
            'skills'
        ]
        read_only_fields = fields
        