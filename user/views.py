from rest_framework import (
    status, 
    generics, 
    viewsets, 
    exceptions, 
    permissions,
    filters
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView, GenericAPIView

from rest_framework_simplejwt.tokens import RefreshToken

import jwt
from django.contrib.auth import authenticate
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator, PasswordResetTokenGenerator

from django_filters.rest_framework import DjangoFilterBackend
import django_filters
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter

from .serializers import *
from service_api.helper.permissions import *
from .models import CustomUser, PasswordReset
from .mailers import send_verification_email, request_password_reset, send_admin_created_email


class SignUp(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate token
        tokens = RefreshToken.for_user(user)
        access_token = str(tokens.access_token)
        
        # Generate verification URL
        current_site = get_current_site(request).domain
        relative_link = reverse('verify-email')
        verify_url = f'http://{current_site}{relative_link}?token={access_token}'
        
        # Send verification email using Celery
        send_verification_email.delay(
            user_id=user.user_id,
            username=user.username,
            email=user.email,
            verification_url=verify_url
        )
        
        return Response({
            'user': serializer.data,
            'token': access_token,
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)
        
class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(user_id=payload['user_id'])
            
            if not user.is_verified:
                user.is_verified = True
                user.save()
                
            return Response(
                {'email': 'Successfully verified'}, 
                status=status.HTTP_200_OK
            )
            
        except jwt.ExpiredSignatureError:
            return Response(
                {'error': 'Verification link expired'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {'error': 'Invalid token'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class LoginView(APIView):
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            },
            'user': {
                'email': user.email,
                'role': user.role,
                'username': user.username
            }
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import generics, status
from rest_framework.response import Response
from service_api.helper.permissions import IsProfileOwner
from .serializers import ListProfileSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsProfileOwner]
    serializer_class = ListProfileSerializer
    
    def get_object(self):
        user = self.request.user
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['is_owner'] = True  # Since this view is for the user's own profile
        return context
    
    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        
        # Update profile directly
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
class UserPhotoUploadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        photo = request.data.get("profile_picture")
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.profile_picture = photo
        profile.save()
        
        serializer = ProfilePictureSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserBannerUploadView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        user = request.user
        photo = request.data.get("banner")
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.banner = photo
        profile.save()
        
        serializer = BannerSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK) 

class AdminUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()  # This is fine
    serializer_class = ListProfileSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdministrator]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter]
    filterset_fields = ['role']
    search_fields = ['username']

    def get_queryset(self):
        # Filter users who are verified and not banned, and not deleted
        return CustomUser.objects.filter(
            is_verified=True,
            is_banned=False,
            deleted_at__isnull=True
        )

class UserBannedListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()  # This is fine
    serializer_class = ListProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['role', 'is_verified', 'is_banned']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username']
    ordering = ['-created_at']

    def get_queryset(self):
        # Filter users who are verified and not banned, and not deleted
        return CustomUser.objects.filter(
            is_verified=True,
            is_banned=True,
            deleted_at__isnull=True
        )

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class UserListView(generics.ListAPIView):
    # Ensure this matches what get_queryset returns
    serializer_class = ListProfileSerializer
    
    # Permissions and filters setup
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # These fields should match fields available in Profile model if applicable
    filterset_fields = ['user__role', 'user__is_banned']  # Adjust based on actual model fields
    
    search_fields = ['user__username']  # Assuming username is part of CustomUser model
    
    ordering_fields = ['created_at', 'user__username']  # Adjust field names as needed
    
    ordering = ['-created_at']

    def get_queryset(self):
        return Profile.objects.filter(
            user__is_verified=True,
            user__is_banned=False,
            user__deleted_at__isnull=True,
            user__role__in=['Freelancer', 'Client']
        ).exclude(user=self.request.user)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RetrieveProfileSerializer
    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return get_object_or_404(Profile, user_id=user_id)

class UserBanView(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdministrator]
    
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, user_id=user_id)
        
        # Prevent self-banning
        if request.user.user_id == user.user_id:
            return Response(
                {"error": "You cannot ban your own account"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.is_banned = True
        user.save()
        
        return Response(
            {"message": f"User {user.email} has been banned successfully"},
            status=status.HTTP_200_OK
        )

class UserUnbanView(APIView):
    permission_classes = [permissions.IsAuthenticated,IsAdministrator]
    
    def post(self, request, user_id):
        user = get_object_or_404(CustomUser, user_id=user_id)
        
        user.is_banned = False
        user.save()
        
        return Response(
            {"message": f"User {user.email} has been unbanned successfully"},
            status=status.HTTP_200_OK
        )

class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        serializer_class = ChangePasswordSerializer(data = request.data, context = {"request": request})
        if serializer_class.is_valid():
            serializer_class.save()
            return Response({"detail": "Password successfully updated."}, status=status.HTTP_200_OK)
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RequestPasswordReset(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            raise exceptions.ValidationError(serializer.errors)
            
        email = request.data["email"]
        user = CustomUser.objects.filter(email__iexact=email).first()
        
        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            reset = PasswordReset(email=email, token=token)
            reset.save()
            # Change user.user_id to user.id or user.pk
            request_password_reset.delay(token, user.user_id)  # or user.pk
            return Response(
                {"success": "We have sent you a link to reset your password."}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"error": "User with the given email is not found."}, 
            status=status.HTTP_404_NOT_FOUND
        )

class ResetPassword(generics.GenericAPIView):
    serializer_class = PasswordResetSerializer
    
    def post(self,request):
        serializer =self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        password = data["password"]
        confirm_password = data["confirm_password"]
        token = request.data["token"]
        
        if password != confirm_password:
            return Response({"error": "Passwords do not match"}, status=400)
        reset_obj = PasswordReset.objects.filter(token=token).first()
        
        if not reset_obj:
            return Response({"error": "Invalid token"}, status=400)

        user = CustomUser.objects.filter(email=reset_obj.email).first()
        
        if user:
            user.set_password(password)
            user.save()
            reset_obj.delete()
            return Response({"success": "Password updated"})
        else:
            return Response({"error": "No user found"}, status=404)
 
class AdminUserCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]
    serializer_class = AdminUserCreateSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_verified=False)
        
        # Generate activation token
        token = default_token_generator.make_token(user)
        current_site = get_current_site(self.request).domain
        activation_url = (
            f"http://{current_site}/auth/activate-account/"
            f"?user_id={user.user_id}&token={token}"
        )
        
        send_admin_created_email.delay(
            user_id=user.user_id,
            email=user.email,
            activation_url=activation_url
        )

class AdminUserActivationView(generics.GenericAPIView):
    serializer_class = AdminUserActivationSerializer
    

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        password = serializer.validated_data['password']
        
        # Activate user and set password
        user.is_verified = True
        user.set_password(password)
        user.save()
        
        return Response(
            {"message": "Account activated successfully"},
            status=status.HTTP_200_OK
        )      