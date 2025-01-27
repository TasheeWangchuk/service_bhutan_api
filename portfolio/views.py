from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Portfolio, Certificate, Education, Experience
from .serializers import (
    PortfolioSerializer, 
    CertificateSerializer,
    EducationSerializer, 
    ExperienceSerializer
)
from django.utils import timezone

class PortfolioListCreateView(generics.ListCreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = PortfolioSerializer
    
    def get_queryset(self):
        return Portfolio.objects.filter(profile=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

class PortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
   
    permission_classes = (IsAuthenticated,)
    serializer_class = PortfolioSerializer
    
    def get_queryset(self):
        return Portfolio.objects.filter(profile=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())
        
class CertificateListCreateView(generics.ListCreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateSerializer
    
    def get_queryset(self):
        return Certificate.objects.filter(profile=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

class CertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = CertificateSerializer
    
    def get_queryset(self):
        return Certificate.objects.filter(profile=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())
        
class EducationListCreateView(generics.ListCreateAPIView):
   
    permission_classes = (IsAuthenticated,)
    serializer_class = EducationSerializer
    
    def get_queryset(self):
        return Education.objects.filter(profile=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = EducationSerializer
    
    def get_queryset(self):
        return Education.objects.filter(profile=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())
        
class ExperienceListCreateView(generics.ListCreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = ExperienceSerializer
    
    def get_queryset(self):
        return Experience.objects.filter(profile=self.request.user.profile)
    
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = ExperienceSerializer
    
    def get_queryset(self):
        return Experience.objects.filter(profile=self.request.user.profile)
    
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())