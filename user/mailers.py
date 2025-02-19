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
from smtplib import SMTPException

logger = logging.getLogger(__name__)

@app.task
def request_password_reset(token, user_id):
    try:
        # Use get() instead of get_object_or_404 since this isn't a view
        user = CustomUser.objects.get(pk=user_id)
        
        url = f"{os.getenv('HOST_URL', '')}/auth/password?reset_password_token={token}"
        
        logger.info(f"Attempting to send reset email to {user.email}")
        logger.info(f"Using HOST_URL: {os.getenv('HOST_URL', '')}")
        
        html_content = render_to_string(
            "mailers/user/request_password_reset.html",
            {"name": user.username, "url": url}
        )
        
        plain_message = f"Reset your password by visiting: {url}"
        
        send_mail(
            subject="Reset password instructions",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_content,
            fail_silently=False
        )
        logger.info(f"Password reset email sent successfully to {user.email}")
        
    except CustomUser.DoesNotExist:
        logger.error(f"Failed to send password reset: User with id {user_id} does not exist")
        raise
    except SMTPException as e:
        logger.error(f"SMTP error while sending password reset email: {str(e)}")
        logger.error(f"Email settings: HOST={os.getenv('EMAIL_HOST')}, PORT={os.getenv('EMAIL_PORT')}, FROM={settings.DEFAULT_FROM_EMAIL}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in password reset email: {str(e)}")
        logger.error(f"Email settings: HOST={os.getenv('EMAIL_HOST')}, PORT={os.getenv('EMAIL_PORT')}, FROM={settings.DEFAULT_FROM_EMAIL}")
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