# jobs/serializers.py
from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['user','notification_id','message','notification_type','read','link']
        read_only_fields = ('user', 'created_at', 'notification_id')

class NotificationMarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['read','created_at']
        read_only_fields = ('read','created_at')