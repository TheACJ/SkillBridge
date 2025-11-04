from django.db import models
from uuid import uuid4
from users.models import User


class Roadmap(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    domain = models.CharField(max_length=100, help_text="e.g., 'Python', 'Blockchain'")
    modules = models.JSONField(default=list, help_text="Array of {name: String, resources: Array<URL>, estimated_time: Integer, completed: Boolean}")
    progress = models.FloatField(default=0.0, help_text="Progress percentage (0-100)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'roadmaps'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email}'s {self.domain} Roadmap"
