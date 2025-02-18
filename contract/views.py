from rest_framework import generics, permissions, status
from .permissions import *
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import Contract, Milestone
from job.models import Proposal
from .serializers import (
    ContractSerializer,
    ProposalAcceptanceSerializer,
    MilestoneSerializer,
    ContractAcceptanceSerializer,
    ContractCompletedSerializer,
)
from .enums import ContractStatus
from job.enums import ProposalStatusEnum, JobStatusEnum
import logging
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.db import transaction
from .models import Contract
from job.models import Proposal
from .serializers import ContractAcceptanceSerializer
from .enums import ContractStatus
from job.enums import ProposalStatusEnum, JobStatusEnum
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import Payment, Contract
from .serializers import PaymentSerializer,ReviewSerializer
from .permissions import (CanCreateContract, ContractAccessPermission,
                          IsAssignedFreelancer,CanManageContractPayment,
                          CanVerifyPayment,CanCreateContractReview)
from .services import ProposalService,ContractService,PaymentService, ReviewService
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from django.http import Http404
from django.db.models import Q




logger = logging.getLogger(__name__)


class AcceptProposalView(generics.UpdateAPIView):
    queryset = Proposal.objects.all()
    serializer_class = ProposalAcceptanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsJobOwner]
    lookup_field = 'proposal_id'
     
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        proposal = self.get_object()
        serializer = self.get_serializer(proposal, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            updated_proposal = ProposalService.accept_proposal(proposal)
            return Response(self.get_serializer(updated_proposal).data)
        
        except ValidationError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        except Exception as e:
            logger.error(f"Error accepting proposal: {str(e)}")
            return Response(
                {"detail": "An error occurred while processing your request"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProposalContractCreateView(generics.CreateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated,CanCreateContract]

    def perform_create(self, serializer):
        try:
            proposal_id = self.kwargs.get('proposal_id')
            
            #validate proposal
            proposal = ContractService.validate_proposal(proposal_id)
            
            #Extract milestone data
            milestones_data = serializer.validated_data.pop('milestones',[])
            
            #create contract with milestone
            contract =ContractService.create_contract(
                proposal=proposal,
                client=self.request.user,
                milestones_data=milestones_data,
                **serializer.validated_data
            )
            serializer.instance = contract
            

        except ValidationError as e:
            raise ValidationError({"detail": str(e)})
        except Exception as e:
            logger.error(f"Error creating contract: {str(e)}")
            raise ValidationError(
                {"detail": "An error occurred while creating the contract"}
            )

class ContractListView(generics.ListAPIView):
    serializer_class = ContractSerializer
    permission_classes = [ContractAccessPermission]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {
        'status',
    }
    ordering_fields = ['created_at', 'total_amount']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return ContractService.get_user_contracts(self.request.user)
        
class ContractDetailView(generics.RetrieveUpdateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanUpdateContract
    ]
    lookup_field = 'contract_id'

    def get_queryset(self):
        """Filter contracts accessible to the current user"""
        return Contract.objects.filter(
            Q(client=self.request.user) | Q(freelancer=self.request.user)
        ).prefetch_related('milestones')

    def perform_update(self, serializer):
        contract = self.get_object()
        
        # Use service to handle the update
        ContractService.update_contract_with_milestones(
            contract=contract,
            validated_data=serializer.validated_data
        )

class ContractAcceptanceView(generics.UpdateAPIView):
    queryset = Contract.objects.all()
    serializer_class = ContractAcceptanceSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedFreelancer]
    lookup_field = 'contract_id'

    def get_queryset(self):
        """Filter contracts where the current user is the freelancer"""
        return Contract.objects.filter(
            freelancer=self.request.user,
            status=ContractStatus.PENDING
        )

    def update(self, request, *args,**kwargs):
        contract = self.get_object()
        serializer = self.get_serializer(contract, data = request.data,partial = True )
        serializer.is_valid(raise_exception = True)
        
        new_status = serializer.validated_data['status']
        
        if new_status ==ContractStatus.ACCEPTED:
            ContractService.handle_contract_acceptance(contract)
            return Response({
                "detail":"Contract accepted successfully",
                "contract_id":contract.contract_id
            })
        
        elif new_status == ContractStatus.REJECTED:
            ContractService.handle_contact_rejection(contract)
            return Response({
                "detail": "Contract rejected. Proposal resubmitted."
            })
        
        return Response(
            {"detail":"Invalid status choice"},
            status = status.HTTP_400_BAD_REQUEST
        )

class ContractStatusCompletedView(generics.UpdateAPIView):

    serializer_class = ContractCompletedSerializer
    permission_classes = [permissions.IsAuthenticated,IsContractClient]
    lookup_field = 'contract_id'
    
    def get_queryset(self):
        """Filter contracts where the current user is the client"""
        return Contract.objects.filter(
            client=self.request.user,
            status=ContractStatus.ACCEPTED
        )
    
    def update(self, request, *args, **kwargs):
        contract = self.get_object()
         
        # Use the service to handle completion
        updated_contract = ContractService.completed_contract(contract)
        
        # Serialize and return the updated contract
        response_serializer = self.get_serializer(updated_contract)
        print(response_serializer.data)
        return Response(response_serializer.data)
     
class ContractPaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated,CanManageContractPayment]
    
    def get_queryset(self):
        return PaymentService.get_contract_payments(
            contract_id=self.kwargs.get('contract_id')
        )

    def perform_create(self, serializer):
        contract_id = self.kwargs.get('contract_id')
        contract = get_object_or_404(Contract, pk=contract_id)
        
        # Validate payment creation
        PaymentService.validate_payment_creation(contract, self.request.user)
        
        # Create the payment
        serializer.save(contract=contract)

class ContractPaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated,PaymentDetailPermission]
    lookup_field = 'payment_id'
    
    def get_queryset(self):
        contract_id = self.kwargs.get('contract_id')
        return Payment.objects.filter(contract_id=contract_id)
    
    def retrieve(self, request, *args, **kwargs):
        payment = self.get_object()
        serializer = self.get_serializer(payment)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        payment = self.get_object()
        serializer = self.get_serializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        updated_payment = PaymentService.update_payment(
            payment=payment,
            data=serializer.validated_data
        )
        
        return Response(self.get_serializer(updated_payment).data)
    
    def destroy(self, request, *args, **kwargs):
        payment = self.get_object()
        PaymentService.delete_payment(payment)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ContractPaymentVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated,CanVerifyPayment]
    
    def get_payment(self):
        """
        Helper method to get payment object.
        Used by permission class and view.
        """
        return PaymentService.get_contract_payment(
            contract_id=self.kwargs['contract_id'],
            payment_id=self.kwargs['payment_id']
        )
    
    def post(self, request, contract_id, payment_id):
        payment = self.get_payment()
        
        try:
            # Validate if payment can be verified
            PaymentService.validate_verification(payment)
            
            # Verify the payment
            verified_payment = PaymentService.verify_payment(payment)
            
            return Response({
                "message": "Payment verified successfully",
                "payment_id": verified_payment.payment_id,
                "status": verified_payment.status,
                "verified_at": verified_payment.verified_at
            }, status=status.HTTP_200_OK)
            
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class ContractReviewCreateView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated, CanCreateContractReview]
    
    def perform_create(self, serializer):
        contract_id = self.kwargs.get('contract_id')
        try:
            contract = Contract.objects.get(pk=contract_id)
        except Contract.DoesNotExist:
            raise Http404('Contract not found')
        rating = serializer.validated_data['rating']
        
        review = ReviewService.create_review(
            contract=contract,
            user=self.request.user,
            rating=rating
        )
        
        return review
    
class FreelancerReviewListView(generics.ListAPIView):
    """
    View to list all reviews received by a freelancer
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        freelancer_id = self.kwargs.get('freelancer_id')
        return ReviewService.get_freelancer_reviews(freelancer_id)
    

