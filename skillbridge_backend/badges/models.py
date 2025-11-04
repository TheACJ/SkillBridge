from django.db import models
from uuid import uuid4
from users.models import User


class Badge(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    type = models.CharField(max_length=100, help_text="e.g., 'Bronze Mentor'")
    criteria = models.JSONField(help_text="e.g., {sessions_completed: Integer}")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'badges'
        ordering = ['-awarded_at']

    def __str__(self):
        return f"{self.type} - {self.mentor.email}"
