from rest_framework import generics, filters, status,viewsets
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import Job, JobCategory, Skill, Proposal
from .serializers import (
    JobSerializer,
    JobCategorySerializer,
    SkillSerializer,
    ProposalSerializer,
    ProposalListSerializer,
    JobListSerializer
)
from .permissions import *
from .helper.notify import (
    notify_new_proposal,
    notify_proposal_status_change,
    notify_job_status_change,
    notify_job_deletion
)

class JobListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):  
        if self.request.method == 'POST':
            return [IsClient()]
        return [IsAuthenticated()]  
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return JobSerializer
        return JobListSerializer
    
    def get_queryset(self):
        user = self.request.user
        queryset = Job.objects.select_related('job_category', 'user').prefetch_related('skills')
       
        # If user is a client, only show their own jobs
        if user.role == 'Client':  
            return queryset.filter(user=user)
            
        # If user is freelancer or admin, show all jobs
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class JobRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = JobSerializer
    lookup_field = 'job_id'
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        job = serializer.save()
        notify_job_status_change(job, old_status)
     
    def perform_destroy(self, instance):
        notify_job_deletion(instance)  # Helper call
        super().perform_destroy(instance)
         
    def get_queryset(self):
        return Job.objects.select_related('job_category','user').prefetch_related('skills')
    
class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsAuthenticated]

class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=False, methods=['get'])
    def popular(self, request):
        # Get top 10 most used skills
        popular_skills = Skill.objects.annotate(
            job_count=models.Count('job')
        ).order_by('-job_count')[:10]
        
        serializer = self.get_serializer(popular_skills, many=True)
        return Response(serializer.data)

class ProposalListCreateView(generics.ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProposalSerializer
        return ProposalListSerializer 
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsFreelancer()]
        return [IsAuthenticated()]  # Base permission, we'll filter in get_queryset
    
    
    def get_queryset(self):
        job_id = self.kwargs.get('job_id')
        try:
            # First try to get the job
            job = Job.objects.get(job_id=job_id)
            print(f"Found job: {job}")
            
            user = self.request.user
            if user == job.user:
                return Proposal.objects.filter(job_id=job_id)
            
            return Proposal.objects.filter(
                job_id=job_id,
                user=self.request.user
            )
            
        except Job.DoesNotExist:
            # Log the error and return empty queryset
            print(f"No job found with ID: {job_id}")
            return Proposal.objects.none()
        
    
    def perform_create(self, serializer):
        job_id = self.kwargs.get('job_id')
        job = get_object_or_404(Job, job_id=job_id)
        
        existing_proposal = Proposal.objects.filter(
            job=job,
            user=self.request.user
        ).exists()
        
        if existing_proposal:
            raise ValidationError("You have already submitted a proposal for this job")
        
        proposal = serializer.save(job=job,user=self.request.user)
        notify_new_proposal(proposal)
        
class ProposalDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'proposal_id'
    
    def get_object(self):
        obj = super().get_object()
        # Only allow access to own proposals or job owner
        if obj.user != self.request.user and obj.job.user != self.request.user:
            raise permissions.PermissionDenied(
                "You don't have permission to access this proposal"
            )
        return obj
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        proposal = serializer.save()
        notify_proposal_status_change(proposal, old_status)
        
    def perform_destroy(self, instance):
        # Only allow deletion if proposal is pending
        if instance.status != 'PENDING':
            raise ValidationError(
                "Cannot delete proposal that is not in pending status"
            )
        if instance.user != self.request.user:
            raise permissions.PermissionDenied(
                "Only proposal owner can delete the proposal"
            )
        instance.delete()
        
class UserProposalListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsFreelancer]
    serializer_class = ProposalListSerializer
    
    def get_queryset(self):
        return Proposal.objects.filter(
            user=self.request.user
        ).select_related(
            'job', 'user'
        ).prefetch_related(
            'skills'
        ).order_by('-created_at')