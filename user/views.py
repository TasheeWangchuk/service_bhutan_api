from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializer import (UserRegistrationSerializer, UserLoginSerializer, 
                        ProfileSerializer, UserProfileSerializer, EmailVerificationSerializer)
from rest_framework import response,status
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.generics import ListAPIView, GenericAPIView
from . import models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from .utils import Util
from django.conf import settings
import jwt




class SignUp(GenericAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        #generate token
        user_email = models.CustomUser.objects.get(email = user.email)
        tokens = RefreshToken.for_user(user_email).access_token
        
        # Generate verification email
        current_site = get_current_site(request).domain
        relative_link = reverse('verify-email')
        verify_url = f'http://{current_site}{relative_link}?token={str(tokens)}'
        
        email_body = f'Hi {user.username},\nUse the link below to verify your email:\n{verify_url}'
        email_data = {
            'email_body': email_body,
            'to_email': user.email,
            'email_subject': 'Verify your email'
        }
        
        Util.send_email(data=email_data)
        
        return Response({
            'user': serializer.data,
            'token': str(tokens)
        }, status=status.HTTP_201_CREATED)

class VerifyEmail(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer
    
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = models.CustomUser.objects.get(user_id=payload['user_id'])
            
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
    permission_classes = [AllowAny]
    
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
            }
        })

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        user = self.request.user
        # Create profile if it doesn't exist
        if not hasattr(user, 'profile'):
            models.Profile.objects.create(user=user)
        return user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        profile_data = request.data.pop('profile', {})
        
        # Update user data
        user_serializer = self.get_serializer(user, data=request.data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        
        # Update or create profile
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)
            
        if profile_data:
            profile_serializer = ProfileSerializer(
                user.profile, 
                data=profile_data, 
                partial=True
            )
            profile_serializer.is_valid(raise_exception=True)
            profile_serializer.save()
        
        return Response(user_serializer.data)