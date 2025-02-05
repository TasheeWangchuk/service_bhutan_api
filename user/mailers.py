from django.template.loader import render_to_string
from service_api.celery import app
from django.core.mail import send_mail
from django.conf import settings
import logging
from .models import CustomUser
from django.shortcuts import get_object_or_404
import secrets
import os
import string

logger = logging.getLogger(__name__)

@app.task
def request_password_reset(token, user_id):
   try:
        user = get_object_or_404(CustomUser, pk=user_id)
        # url = f"{os.getenv('HOST_URL', '')}/auth/password?reset_password_token={token}"
        url = f"http://127.0.0.1:8000/auth/password?reset_password_token={token}"
        print("usrl", url)
        html_content = render_to_string(
            "mailers/user/request_password_reset.html",
            {"name": user.username, "url": url},
        )
        
        # Plain text message
        plain_message = f"Reset your password by visiting: {url}"
        
        # Send email
        send_mail(
            subject="Reset password instructions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content
        )
        logger.info(f"Password reset email sent to {user.email}")
   except Exception as e:
       logger.error(f"Error in password reset email: {e}")
       raise
        

@app.task
def send_verification_email(user_id,username,email,verification_url):
    try:
        html_content = render_to_string(
            "mailers/user/email_verification.html",
            {"name":username, "url":verification_url}
        )
    
        # Plain text message
        plain_message = f"Verify your email by visiting: {verification_url}"
        
        # Send email
        send_mail(
            subject="Verify Your Email Address",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content
        )
        logger.info(f"Verification email sent to {email}")
    except Exception as e:
        logger.error(f"Error in verification email: {e}")
        raise
    
@app.task
def send_admin_created_email(user_id, email, verification_url):
    try:
        user = CustomUser.objects.get(pk=user_id)
        html_content = render_to_string(
            "mailers/user/admin_created_email.html",
            {"name": user.username, "url": verification_url}
        )
        
        plain_message = f"""Welcome to our platform! An admin created an account for you.
Please set your password to verify your account: {verification_url}"""

        send_mail(
            subject="Complete Your Account Setup",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content
        )
        logger.info(f"Admin-created user email sent to {email}")
    except Exception as e:
        logger.error(f"Error in admin-created user email: {e}")
        raise

@app.task
def send_admin_created_email(user_id, email, activation_url):
    try:
        user = CustomUser.objects.get(user_id=user_id)
        html_content = render_to_string(
            "mailers/user/admin_activation.html",
            {"activation_url": activation_url}
        )
        
        plain_message = f"Activate your account: {activation_url}"
        
        send_mail(
            subject="Complete Your Account Setup",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_content
        )
        logger.info(f"Admin activation email sent to {email}")
    except Exception as e:
        logger.error(f"Error sending admin activation email: {e}")
        raise