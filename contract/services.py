from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Proposal,Milestone,Contract,Payment
from job.enums import JobStatusEnum,ProposalStatusEnum
from .enums import ContractStatus
from django.shortcuts import get_object_or_404
from django.db.models import Q
import logging
from .enums import PaymentStatus




logger = logging.getLogger(__name__)

class ProposalService:
    @staticmethod
    @transaction.atomic
    def accept_proposal(proposal):
        if proposal.job.status == JobStatusEnum.CLOSED.name :
            raise ValidationError("Job is already closed")
        
        # Update the proposal status
        proposal.status = ProposalStatusEnum.ACCEPTED.name
        proposal.save()
        
        # Update the job status
        proposal.job.status = JobStatusEnum.CLOSED.name
        proposal.job.save()
        
        # Reject other proposals
        Proposal.objects.filter(job=proposal.job).exclude(pk=proposal.pk).update(
            status=ProposalStatusEnum.REJECTED.name
        )
        
        return proposal
 

class ContractService:
    @staticmethod
    def validate_proposal(proposal_id):
        try:
            proposal = Proposal.objects.get(pk=proposal_id)
            if proposal.status != ProposalStatusEnum.ACCEPTED.name:
                raise ValidationError("Can only create contracts for accepted proposals")
            return proposal
        except Proposal.DoesNotExist:
            raise ValidationError("Proposal not found")
    
    @staticmethod
    @transaction.atomic
    def create_contract(proposal, client,milestones_data, **contract_data):
        contract = Contract.objects.create(
            client=client,
            freelancer=proposal.user,
            job=proposal.job,
            status=ContractStatus.PENDING,
            **contract_data
        )
        
        milestones = [
                Milestone(contract=contract, **milestone_data)
                for milestone_data in milestones_data
            ]
        Milestone.objects.bulk_create(milestones)

        return contract
    
    def get_user_contracts(user):
        return Contract.objects.filter(
            Q(client = user) | Q(freelancer = user)
        ).select_related('job','client','freelancer').prefetch_related('milestones')
     
    @staticmethod
    def validate_contract_status(contract):
        if contract.status != 'PENDING':
            raise ValidationError("Contract can only be updated when in PENDING status.")
        
    @staticmethod
    def update_contract_with_milestones(contract, validated_data):
        # Validate contract status before proceeding
        ContractService.validate_contract_status(contract)

        with transaction.atomic():
            # Extract milestones data before updating contract
            milestones_data = validated_data.pop('milestones', [])
            
            # Update contract details
            for attr, value in validated_data.items():
                setattr(contract, attr, value)
            contract.save()
            
            # Handle milestone updates if provided
            if milestones_data:
                # Clear existing milestones
                contract.milestones.all().delete()
                
                # Create new milestones
                Milestone.objects.bulk_create([
                    Milestone(contract=contract, **milestone_data)
                    for milestone_data in milestones_data
                ])
            
            return contract
        
    @staticmethod
    @transaction.atomic
    def handle_contact_rejection(contract):
        """
        Handle the contract rejection process
        """
        #Reset job status to open
        contract.job.status = JobStatusEnum.OPEN.name
        contract.job.save()
        
        #get the current proposals associated with this contract
        current_proposal = Proposal.objects.get(
            job = contract.job,
            user = contract.freelancer
        )
        
        # Update all other proposals for this job back to pending
        Proposal.objects.filter(
            job=contract.job
        ).exclude(
            proposal_id=current_proposal.proposal_id
        ).update(status=ProposalStatusEnum.PENDING.name)
        
        # Set the current proposal to rejected
        current_proposal.status = ProposalStatusEnum.REJECTED.name
        current_proposal.save()
    
        # Update contract status
        contract.status = ContractStatus.REJECTED.name
        contract.save()
    @staticmethod
    @transaction.atomic
    def handle_contract_acceptance(contract):
        """
        Handle the contract acceptance process
        """
        contract.status = ContractStatus.ACCEPTED
        contract.save()
    
    @staticmethod
    @transaction.atomic
    def completed_contract(contract):
        contract.status = ContractStatus.COMPLETED
        contract.save()
        return contract
    

class PaymentService:
    @staticmethod
    def get_contract_payments(contract_id):
        return Payment.objects.filter(contract_id=contract_id)
    
    @staticmethod
    def validate_payment_creation(contract,user):
        if user != contract.client:
            raise ValidationError("Only clients can create payments")
        
        if contract.status != ContractStatus.COMPLETED:
            raise ValidationError("Payments can only be made for completed contracts")
    
    @staticmethod
    def create_payment(contract, payment_data):
       
        return Payment.objects.create(
            contract=contract,
            **payment_data
        )
    
    @staticmethod
    def get_contract_payment(contract_id, payment_id):
        """
        Get a specific payment for a contract
        """
        return get_object_or_404(
            Payment.objects.filter(contract_id=contract_id),
            payment_id=payment_id
        )
        
    @staticmethod
    def update_payment(payment, data):
        """
        Update payment details
        """
        # Add any validation logic here
        if payment.status != PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be updated")
            
        for key, value in data.items():
            setattr(payment, key, value)
        payment.save()
        return payment
    
    @staticmethod
    def delete_payment(payment):
        """
        Delete a payment
        """
        if payment.status != PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be deleted")
            
        payment.delete()
        
    @staticmethod
    def get_contract_payment(contract_id, payment_id):
        """
        Get payment and verify it belongs to the contract
        """
        return get_object_or_404(
            Payment,
            payment_id=payment_id,
            contract_id=contract_id
        )

    @staticmethod
    def validate_verification(payment):
        """
        Validate if payment can be verified
        """
        if payment.status == PaymentStatus.VERIFIED:
            raise ValidationError("Payment is already verified")

        if payment.status != PaymentStatus.PENDING:
            raise ValidationError("Only pending payments can be verified")

    @staticmethod
    def verify_payment(payment):
        """
        Mark payment as verified and handle related operations
        """
        payment.status = PaymentStatus.VERIFIED
        payment.save()

        # You could add additional operations here:
        # - Update contract balance
        # - Send notifications
        # - Create payment receipt
        # - Update payment history
        
        return payment
        
    

# services.py
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import Review
from django.db.models import Avg
from decimal import Decimal
from user.models import Profile



class ReviewService:
    @staticmethod
    def validate_review_creation(contract, user):
        """
        Validate if a review can be created
        """
        if contract.status != ContractStatus.COMPLETED:
            raise ValidationError(_('Reviews can only be created for completed contracts'))

        if user != contract.client:
            raise ValidationError(_('Only the contract client can create reviews'))

        if Review.objects.filter(contract=contract).exists():
            raise ValidationError(_('A review already exists for this contract'))

    @staticmethod
    @transaction.atomic
    def create_review(contract, user, rating):
        """
        Create a new review for a contract
        """
        # Validate review creation
        ReviewService.validate_review_creation(contract, user)
        
        # Create the review
        review = Review.objects.create(
            client=user,
            freelancer=contract.freelancer,
            contract=contract,
            rating=rating
        )
        
        # Update freelancer's average rating (optional)
        ReviewService.update_freelancer_rating(contract.freelancer)
        
        return review

    @staticmethod
    def update_freelancer_rating(freelancer):
        """
        Update freelancer's average rating and 
        """
        review_stats = Review.objects.filter(
            freelancer=freelancer
        ).aggregate(
            avg_rating=Avg('rating'),
        )
        
        # Get or create profile
        profile, _ = Profile.objects.get_or_create(user=freelancer)
        
        # Update profile with new stats
        # Convert to Decimal safely, defaulting to 0 if None
        avg_rating = review_stats['avg_rating'] or 0
        profile.average_rating = Decimal(str(avg_rating)).quantize(Decimal('0.01'))
        profile.save()
        
        return profile

    @staticmethod
    def get_freelancer_reviews(freelancer_id):
        """
        Get all reviews for a freelancer
        """
        return Review.objects.filter(
            freelancer_id=freelancer_id
        ).select_related('client', 'contract')   
   

        
   
        
        