# permissions.py
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from job.models import Proposal
from contract.models import Contract, Review
from contract.enums import PaymentStatus, ContractStatus

# User Role Permissions
class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Client'

class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Freelancer'

class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Administrator'

# General Ownership Permissions
class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.profile == request.user.profile

class IsProfileOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class IsNotificationOwner(permissions.BasePermission):
    """Ensure user only accesses their own notifications"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

# Job-related Permissions
class IsJobOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # For jobs that have a 'user' attribute
        if hasattr(obj, 'job'):
            return obj.job.user == request.user
        # For direct job objects
        return obj.user == request.user

class IsJobOwnerOrAdmin(permissions.BasePermission):
    """Allow only job owners or admins to modify/delete"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Client':
            return True
        return obj.user == request.user

# Proposal-related Permissions
class IsProposalAccessible(permissions.BasePermission):
    """
    Custom permission to check if user can access the proposal:
    - Proposal owners have full access (GET, PUT, PATCH, DELETE)
    - Job owners can only view proposals (GET)
    """
    def has_object_permission(self, request, view, obj):
        # Proposal owner has full access
        if obj.user == request.user:
            return True
            
        # Job owner can only view
        if obj.job.user == request.user:
            return request.method in permissions.SAFE_METHODS
            
        return False

class CanDeleteProposal(permissions.BasePermission):
    """
    Custom permission to check if user can delete the proposal.
    Only allows deletion if:
    1. User is the proposal owner
    2. Proposal is in PENDING status
    """
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
            
        if obj.status != 'PENDING':
            raise ValidationError("Cannot delete proposal that is not in pending status")
            
        return obj.user == request.user

# Contract-related Permissions
class CanCreateContract(permissions.BasePermission):
    def has_permission(self, request, view):
        proposal_id = view.kwargs.get('proposal_id')
        try:
            proposal = Proposal.objects.get(pk=proposal_id)
            return proposal.job.user == request.user
        except Proposal.DoesNotExist:
            return False

class ContractAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        return request.user in [obj.client, obj.freelancer]
    
class CanUpdateContract(permissions.BasePermission):
    message = "Only clients can update contracts they are involved with."

    def has_object_permission(self, request, view, obj):
        # Allow GET requests for both client and freelancer
        if request.method in permissions.SAFE_METHODS:
            return request.user in [obj.client, obj.freelancer]
        
        # For PUT/PATCH, allow only if user is the client
        return request.user == obj.client

class IsAssignedFreelancer(permissions.BasePermission):
    """Custom permission to only allow the assigned freelancer to accept/reject a contract."""
    def has_object_permission(self, request, view, obj):
        return obj.freelancer == request.user

class IsContractClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.client == request.user

# Payment-related Permissions
class CanManageContractPayment(permissions.BasePermission):
    """
    Permission class for contract payments:
    - List: Both client and freelancer can view
    - Create: Only client can create
    """
    def has_permission(self, request, view):
        contract_id = view.kwargs.get('contract_id')
        try:
            contract = Contract.objects.get(pk=contract_id)
            if request.method == 'POST':
                return request.user == contract.client
            return request.user in [contract.client, contract.freelancer]
        except Contract.DoesNotExist:
            return False

class PaymentDetailPermission(permissions.BasePermission):
    """
    Permission class for payment detail operations:
    - GET: Both client and freelancer can view
    - PUT/PATCH: Only client can update
    - DELETE: Only client can delete, and only if payment is in PENDING status
    """
    def has_object_permission(self, request, view, obj):
        contract = obj.contract
        
        # For viewing, both client and freelancer can access
        if request.method in permissions.SAFE_METHODS:
            return request.user in [contract.client, contract.freelancer]
        
        # For updates and deletes, only client can perform
        if request.user != contract.client:
            return False
        
         # For deletion, check if payment is in PENDING status
        if request.method == 'DELETE':
            return obj.status == PaymentStatus.PENDING
            
        return True

class CanVerifyPayment(permissions.BasePermission):
    """
    Permission to verify payments:
    - Only the freelancer of the contract can verify payments
    """
    def has_permission(self, request, view):
        payment = view.get_payment()
        return request.user == payment.contract.freelancer

# Review-related Permissions
class CanCreateContractReview(permissions.BasePermission):
    """
    Permission to create contract reviews:
    - Only contract client can create review
    - Contract must be completed
    - Only one review per contract
    """
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True
            
        # Get contract_id from URL parameters instead of request.data
        contract_id = view.kwargs.get('contract_id')
        
        try:
            contract = Contract.objects.get(pk=contract_id)
            return (
                request.user == contract.client and
                contract.status == ContractStatus.COMPLETED and
                not Review.objects.filter(contract=contract).exists()
            )
        except Contract.DoesNotExist:
            return False

class ReviewPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create']:
            return request.user.is_authenticated
        return True

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve']:
            return (
                request.user == obj.client or 
                request.user == obj.freelancer
            )
        return False