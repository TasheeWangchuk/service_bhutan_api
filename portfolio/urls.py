from django.urls import path
from .views import (PortfolioDetailView,PortfolioListCreateView,CertificateDetailView,CertificateListCreateView
                    ,EducationDetailView,EducationListCreateView,ExperienceListCreateView,ExperienceDetailView)

urlpatterns = [
    path('portfolios/', PortfolioListCreateView.as_view(), name='portfolio-list'),
    path('portfolios/<int:pk>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('certificates/', CertificateListCreateView.as_view(), name='certificate-list'),
    path('certificates/<int:pk>/',CertificateDetailView.as_view(), name='certificate-detail'),
    path('education/', EducationListCreateView.as_view(), name='education-list'),
    path('education/<int:pk>/', EducationDetailView.as_view(), name='education-detail'),
    path('experiences/', ExperienceListCreateView.as_view(), name='experience-list'),
    path('experiences/<int:pk>/', ExperienceDetailView.as_view(), name='experience-detail'),
]