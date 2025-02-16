from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobCategoryViewSet,
    SkillViewSet,
    ProposalListCreateView,
    ProposalDetailView,
    JobListCreateView,
    JobDetailView,
    UserProposalListView
)

router = DefaultRouter()
router.register(r'job-categories', JobCategoryViewSet, basename='job-category')
router.register(r'skills', SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
    path('jobs/', JobListCreateView.as_view(), name='job-list-create'),
    path('jobs/<int:job_id>/', JobDetailView.as_view(), name='job-detail'),
    path('jobs/<int:job_id>/proposals/', ProposalListCreateView.as_view(), name='job-proposals-list-create'),
    path('proposals/<int:proposal_id>/', ProposalDetailView.as_view(), name='job-proposal-detail'),
    path('proposals/my-proposals/', UserProposalListView.as_view(), name='user-proposals-list'),
    path('proposals/my-proposals/<int:proposal_id>/', ProposalDetailView.as_view(), name='user-proposals-list'),

]