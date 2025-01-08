from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/users", include("user.urls"), name="users"),
    path("api/v1/portfolios", include("portfolio.urls"), name="portfolio"),
]
