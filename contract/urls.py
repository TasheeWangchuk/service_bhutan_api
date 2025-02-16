# contracts/urls.py (update existing urls)
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (ContractDetailView, AcceptProposalView,ContractListView,
                    ContractAcceptanceView,ContractStatusCompletedView,
                    ContractPaymentListCreateView,ContractReviewCreateView, FreelancerReviewListView,
                    ContractPaymentDetailView, ContractPaymentVerificationView,
                    ProposalContractCreateView)


urlpatterns = [
    path('proposals/<int:proposal_id>/accept/', AcceptProposalView.as_view(), name='accept-proposal'),
    path('proposals/<int:proposal_id>/contract/',ProposalContractCreateView.as_view(),name='contract-create'),
    path('contract/list/',ContractListView.as_view(),name='contract-list'),
    path('contracts/<int:contract_id>/', ContractDetailView.as_view(), name='contract-detail'),
    path('contracts/<int:contract_id>/respond/', ContractAcceptanceView.as_view(), name='contract-response'),
    path('contracts/<int:contract_id>/complete/', ContractStatusCompletedView.as_view(), name='contract-complete'),
    path('contracts/<int:contract_id>/payments/', ContractPaymentListCreateView.as_view(), name='contract-payments'),
    path('contracts/<int:contract_id>/payments/<int:payment_id>/', ContractPaymentDetailView.as_view(), name='contract-payment-detail'),
    path('contracts/<int:contract_id>/payments/<int:payment_id>/verify/', ContractPaymentVerificationView.as_view(), name='contract-payment-verify'),
    path('contracts/<str:contract_id>/reviews/',ContractReviewCreateView.as_view(),name='contract-review-create' ),
    path('freelancers/<str:freelancer_id>/reviews/',FreelancerReviewListView.as_view(),name='freelancer-reviews-list'),
   
]