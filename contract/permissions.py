# permissions.py
from rest_framework import permissions
from job.models import Proposal
from .models import Contract,Review
from .enums import PaymentStatus,ContractStatus
     
class IsJobOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.job.user == request.user

class CanCreateContract(permissions.BasePermission):
    def has_permission(self,request,view):
        proposal_id = view.kwargs.get('proposal_id')
        try:
            proposal = Proposal.objects.get(pk = proposal_id)
            return proposal.job.user == request.user
        except Proposal.DoesNotExist:
            return False

class ContractAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view,obj):
        return request.user in [obj.client,obj.freelancer]
    
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