from rest_framework import permissions

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