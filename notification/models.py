# jobs/models.py
from django.db import models
from user.models import CustomUser

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('proposal', 'Proposal'),
        ('job', 'Job'),
        ('system', 'System'),
    )

    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.message[:50]}"