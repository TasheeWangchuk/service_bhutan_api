# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PortfolioViewSet,
    CertificateViewSet,
    EducationViewSet,
    ExperienceViewSet
)

router = DefaultRouter()
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'education', EducationViewSet, basename='education')
router.register(r'experiences', ExperienceViewSet, basename='experience')

urlpatterns = [
    path('', include(router.urls)),
]