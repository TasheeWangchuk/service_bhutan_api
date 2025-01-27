from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import  (ProfileView,SignUp,VerifyEmail,
                     LogoutView,LoginView,UserBanView, UserUnbanView,UserListView,UserDetailView,ChangePasswordView
                     ,RequestPasswordReset,ResetPassword,UserPhotoUploadView, UserBannerUploadView,UserBannedListView,AdminUserListView
                     ,AdminUserCreateView, AdminUserActivationView)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from . import views


urlpatterns = [
    path('users/register/', SignUp.as_view(), name='register'),
    path('users/verify-email/', VerifyEmail.as_view(), name='verify-email'),
    path('users/login/', LoginView.as_view(), name='login'),
    path('users/logout/', LogoutView.as_view(), name='logout'),
    path('users/profile/', ProfileView.as_view(), name='profile'),
     path('users/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('users/upload_profile_picture/',UserPhotoUploadView.as_view(), name='upload-profile-picture'),
    path('users/upload_banner/',UserBannerUploadView.as_view(), name='upload-banner-picture'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/<int:user_id>/ban/', UserBanView.as_view(), name='user-ban'),
    path('users/<int:user_id>/unban/', UserUnbanView.as_view(), name='user-unban'),
    path("users/admin/", AdminUserListView.as_view(), name="users"),
    path("users/", UserListView.as_view(), name="users"),
    path("users/banned/", UserBannedListView.as_view(), name="user-banned-list"),
    path("users/<int:user_id>/", UserDetailView.as_view(), name="user-detail"),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path("users/reset-password-request/", RequestPasswordReset.as_view(), name="request_password_reset"),
    path("users/reset-password/", ResetPassword.as_view(), name="password_reset"),
    path('users/create-user/', AdminUserCreateView.as_view(), name='admin-create-user'),
    path('users/activate-account/', AdminUserActivationView.as_view(), name='admin-user-activation'),
]

