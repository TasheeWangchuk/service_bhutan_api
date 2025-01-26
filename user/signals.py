from django.db.models.signals import post_save
from django.dispatch import receiver
from ..models import CustomUser, Profile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a profile for new users."""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Ensure profile is created and saved for existing users."""
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()