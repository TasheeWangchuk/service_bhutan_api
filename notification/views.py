from rest_framework import generics, permissions
from .models import Notification
from .serializers import NotificationSerializer,NotificationMarkSerializer
from .permissions import IsNotificationOwner

# Add these new views
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationMarkAsRead(generics.UpdateAPIView):
    serializer_class = NotificationMarkSerializer
    permission_classes = [permissions.IsAuthenticated,IsNotificationOwner]
    queryset = Notification.objects.all()
    lookup_field = 'notification_id'
    
    def perform_update(self, serializer):
        serializer.instance.read = True
        serializer.save()