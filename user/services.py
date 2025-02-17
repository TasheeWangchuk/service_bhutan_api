# services.py
from django.db import transaction
from .models import Profile
from .serializers import BasicProfileSerializer,PrivateUserProfileSerializer

class ProfileService:
    """
    Service layer for profile management operations
    """
    @staticmethod
    def get_or_create_profile(user):
        """Get user profile, creating it if it doesn't exist"""
        if not hasattr(user, 'profile'):
            profile = Profile.objects.create(user=user)
            return profile
        return user.profile
    
    @staticmethod
    @transaction.atomic
    def update_user_and_profile(user, user_serializer, profile_data=None):
        """Update both user and profile information atomically"""
        # Save user data
        user = user_serializer.save()
        
        # Get or create profile
        profile = ProfileService.get_or_create_profile(user)
        
        # Update profile data if provided
        if profile_data:
            profile_serializer = BasicProfileSerializer(
                profile, 
                data=profile_data, 
                partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        
        # Return updated data
        return PrivateUserProfileSerializer(user).data