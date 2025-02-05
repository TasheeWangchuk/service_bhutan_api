from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    """Ensure user only accesses their own notifications"""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user