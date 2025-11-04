from django.db import models
from uuid import uuid4
from users.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('match', 'Match'),
        ('progress_update', 'Progress Update'),
        ('session_reminder', 'Session Reminder'),
        ('badge_awarded', 'Badge Awarded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
        ]

    def __str__(self):
        return f"{self.type} for {self.user.email}"
