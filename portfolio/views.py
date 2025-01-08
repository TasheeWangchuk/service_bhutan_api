from rest_framework import viewsets, status
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

class BaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    
    def perform_create(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
    
    def perform_update(self, serializer):
        serializer.save(
            updated_at=timezone.now(),
        )
    
    def get_queryset(self):
          return self.queryset.filter(profile=self.request.user.profile)
class PortfolioViewSet(BaseViewSet):
    """
    ViewSet for managing portfolio entries.
    Supports: list, create, retrieve, update, delete
    """
    queryset = Portfolio.objects.all()
    serializer_class = PortfolioSerializer

class CertificateViewSet(BaseViewSet):
    """
    ViewSet for managing certificates.
    Supports: list, create, retrieve, update, delete
    """
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

class EducationViewSet(BaseViewSet):
    """
    ViewSet for managing education records.
    Supports: list, create, retrieve, update, delete
    """
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class ExperienceViewSet(BaseViewSet):
    """
    ViewSet for managing work experiences.
    Supports: list, create, retrieve, update, delete
    """
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
