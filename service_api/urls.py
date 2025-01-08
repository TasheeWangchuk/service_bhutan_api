from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include("user.urls"), name="users"),
    path("api/v1/", include("portfolio.urls"), name="portfolio"),
]
