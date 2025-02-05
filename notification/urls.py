from django.urls import path
from .views import (

    NotificationListView,
    NotificationMarkAsRead
)

urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='user-notifications'),
    path('notifications/<int:notification_id>/mark-as-read/', 
         NotificationMarkAsRead.as_view(), 
         name='mark-notification-read'),
]