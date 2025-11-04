from django.db import models
from uuid import uuid4
from users.models import User
from roadmaps.models import Roadmap


class ProgressLog(models.Model):
    EVENT_CHOICES = [
        ('commit', 'Commit'),
        ('pull_request', 'Pull Request'),
        ('issue', 'Issue'),
        ('module_complete', 'Module Complete'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_logs')
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='progress_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    details = models.JSONField(help_text="e.g., {repo: String, commit_hash: String}")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'progress_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'roadmap']),
            models.Index(fields=['event_type']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.event_type} on {self.roadmap.domain}"
