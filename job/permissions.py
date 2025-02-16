from rest_framework import permissions
from rest_framework.exceptions import ValidationError

class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Client'

class IsFreelancer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Freelancer'

class IsAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'Administrator'
    
class IsNotificationOwner(permissions.BasePermission):
    """Ensure user only accesses their own notifications"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

        

class IsJobOwnerOrAdmin(permissions.BasePermission):
    """Allow only job owners or admins to modify/delete"""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'Client':
            return True
        return obj.user == request.user
    

class IsJobOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Assuming Job model has an owner field
        return obj.owner == request.user


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