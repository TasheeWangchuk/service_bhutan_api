from rest_framework import serializers
from .models import Portfolio,Certificate,Education,Experience
from django.utils import timezone


class PortfolioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = [
            'portfolio_id',
            'profile',
            'project_title',
            'project_role',
            'project_description',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['portfolio_id','created_at', 'updated_at']
        
        def validate_project_title(self, value):
            if len(value.strip()) == 0:
                raise serializers.ValidationError("Project title cannot be empty")
            return value

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            'certificate_id',
            'profile',
            'certificate_title',
            'certificate_issuer',
            'certificate_file',
            'issue_date',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['certificate_id', 'created_at', 'updated_at']      
    def validate_issue_date(self, value):
        if value and value > timezone.now().date():
            raise serializers.ValidationError("Issue date cannot be in the future")
        return value
        
class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'education_id',
            'profile',
            'country',
            'university',
            'degree',
            'start_year',
            'end_year'
        ]
        read_only_fields = ['education_id']

    def validate(self, data):
        if data.get('start_year') and data.get('end_year'):
            if data['start_year'] > data['end_year']:
                raise serializers.ValidationError({
                    "end_year": "End year must be after start year"
                })
        return data

class ExperienceSerializer(serializers.ModelSerializer):
    """
    Serializer for Experience model with comprehensive validation.
    """
    duration = serializers.SerializerMethodField

    class Meta:
        model = Experience
        fields = [
            'experience_id',
            'profile',
            'job_title',
            'company_name',
            'country',
            'city',
            'start_date',
            'end_date',
            'work_description',
            'duration'
        ]
        read_only_fields = ['experience_id']

    def get_duration(self, obj):
        """Calculate the duration of experience"""
        if obj.start_date and obj.end_date:
            return (obj.end_date - obj.start_date).days
        return None

    def validate(self, data):
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError({
                    "end_date": "End date must be after start date"
                })
            if data['end_date'] > timezone.now().date():
                raise serializers.ValidationError({
                    "end_date": "End date cannot be in the future"
                })
        return data
