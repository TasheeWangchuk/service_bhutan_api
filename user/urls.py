from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import  ProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


# urlpatterns = [
#     path('auth/register/', UserRegistrationView.as_view(), name='register'),
#     path('auth/login/', UserLoginView.as_view(), name='login'),
#     path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('profile/', ProfileView.as_view(), name='profile'),
    
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]


# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.SignUp.as_view() , name='signup' ),
#     path('email-verify/', views.VerifyEmail.as_view(), name="email-verify"),  
# ]
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.SignUp.as_view(), name='register'),
    path('verify-email/', views.VerifyEmail.as_view(), name='verify-email'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
