from django.contrib import admin
from django.urls import path,include
from django.shortcuts import redirect


def redirect_to_api(request):
    return redirect('api/v1/users/')

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include("user.urls"), name="users"),
    path("api/v1/portfolios/", include("portfolio.urls"), name="portfolios"),
    path("api/v1/", include("job.urls"), name="jobs"),
    # path("api/v1/", include("contract.urls"), name="jobs"),
    path("api/v1/", include("notification.urls"), name="notifications"),
    path("", redirect_to_api, name="home"),  # Add this line
]
