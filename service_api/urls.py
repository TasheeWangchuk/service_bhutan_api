from django.contrib import admin
from django.urls import path,include
from django.shortcuts import redirect


def redirect_to_api(request):
    return redirect('api/v1/users/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/users/", include("user.urls"), name="users"),
    path("api/v1/portfolios/", include("portfolio.urls"), name="portfolio"),
    path("", redirect_to_api, name="home"),  # Add this line
]
