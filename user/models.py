from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db.models.signals import post_save
from django.db import models
from django.contrib.auth.models import BaseUserManager
from rest_framework_simplejwt.tokens import RefreshToken
from django.dispatch import receiver
from django.db.models.signals import post_save


class UserManager(BaseUserManager):
    def create_user(self, email,password,**extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    user_id = models.AutoField(primary_key=True,unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(unique=True,null=False)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128,null=False)
    confirm_password = models.CharField(max_length=128,null=False)
    cid = models.CharField(max_length=150,unique=True,null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    terms_check = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=[
        ('Client', 'Client'),
        ('Freelancer', 'Freelancer'),
        ('Administrator', 'Administrator')], default='Client')
    is_banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = UserManager()

    class Meta:
        db_table = 'users'
        
    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return({
            'refresh': str(refresh),
            'refresh': str(refresh.access_token),
        })
        
    def __str__(self):
        return str(self.__dict__)
        
class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)  # auto-increment primary key
    user= models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')  # links to the user model
    profile_picture = models.URLField(max_length=200, blank=True, null=True)  # URL to the user's profile picture
    banner = models.URLField(max_length=200, blank=True, null=True)  # URL to the user's banner image
    bio = models.TextField(blank=True, null=True)  # Short biography
    address = models.CharField(max_length=255, blank=True, null=True)  # User's address
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the profile is created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp when the profile is updated

    class Meta:
        db_table = 'profiles'  # The table name in the database

    def __str__(self):
        return f"Profile for {self.user.username}"
    
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    instance.profile.save()
