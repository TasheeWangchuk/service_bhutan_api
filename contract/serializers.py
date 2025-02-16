from rest_framework import serializers
from .models import Contract,Milestone
from job.models import Proposal
from django.utils import timezone

from rest_framework import serializers
from .models import Contract, Milestone
from django.db import transaction
from user.serializers import UserMinimalSerializer

class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['milestone_id', 'title', 'description', 'amount', 'deadline']
        read_only_fields = ['milestone_id']

class ContractSerializer(serializers.ModelSerializer):
    milestones = MilestoneSerializer(many=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    client_name = serializers.CharField(source='client.get_full_name', read_only=True)
    freelancer_name = serializers.CharField(source='freelancer.get_full_name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'contract_id', 'client_name', 'freelancer_name', 'job_title', 'total_amount','status', 
            'start_date', 'end_date', 'milestones','created_at','updated_at'
        ]
        read_only_fields = ['contract_id', 'client_name', 'freelancer_name', 'job_title','created_at','updated_at']

    def create(self, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        
        contract = Contract.objects.create(**validated_data)
        
        for milestone_data in milestones_data:
            Milestone.objects.create(contract=contract, **milestone_data)
            
        return contract
    

    def update(self, instance, validated_data):
        milestones_data = validated_data.pop('milestones', [])
        
        # Update contract fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        with transaction.atomic():
            # Delete existing milestones that are not in the update data
            instance.milestones.all().delete()
            
            # Create new milestones
            for milestone_data in milestones_data:
                Milestone.objects.create(contract=instance, **milestone_data)

        return instance

    def validate(self, data):
        """
        Custom validation for the contract data
        """
        # Ensure end_date is after start_date if both are provided
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date must be after start date"
            })

        # Validate milestones if provided
        milestones_data = data.get('milestones', [])
        if milestones_data:
            total_amount = sum(milestone['amount'] for milestone in milestones_data)
            if total_amount <= 0:
                raise serializers.ValidationError({
                    "milestones": "Total milestone amount must be greater than 0"
                })

            # Ensure milestone due dates are within contract dates
            if start_date and end_date:
                for milestone in milestones_data:
                    due_date = milestone.get('due_date')
                    if due_date and (due_date < start_date or due_date > end_date):
                        raise serializers.ValidationError({
                            "milestones": "Milestone due dates must be within contract start and end dates"
                        })

        return data

class ProposalAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = ['status']
        extra_kwargs = {'status': {'required': True}}
    
class ContractAcceptanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['status']
        extra_kwargs = {'status': {'required': True}}
        
    def validate_status(self, value):
        """
        Validate that the status is either ACCEPTED or REJECTED
        """
        valid_statuses = [ContractStatus.ACCEPTED, ContractStatus.REJECTED]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                f"Status must be one of {valid_statuses}"
            )
        return value   

class ContractCompletedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['status']
        extra_kwargs = {'status': {'required': True}}

from rest_framework import serializers
from .models import Payment, Review, Contract
from user.serializers import UserMinimalSerializer
from django.core.exceptions import ValidationError
from django.utils import timezone

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_id',
            'transaction_id',
            'contract',
            'status',
            'screenshot',
            'created_at'
        ]
        read_only_fields = ['status','payment_id', 'contract','created_at']

    def validate(self, data):
        # Validate payment amount matches contract amount
        if 'amount' in data and 'contract' in data:
            if data['amount'] != data['contract'].total_amount:
                raise serializers.ValidationError({
                    'amount': 'Payment amount must match the contract total amount'
                })
        return data
        
# review/serializers.py
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from .models import Review
from .enums import ContractStatus

class ReviewSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    freelancer_name = serializers.CharField(source='freelancer.username', read_only=True)
    
    class Meta:
        model = Review
        fields = ['review_id', 'rating', 'contract', 'client_name', 
                 'freelancer_name', 'created_at']
        read_only_fields = ['review_id', 'client_name', 'freelancer_name', 'created_at','contract']

    