from django.db import models
from uuid import uuid4
from users.models import User


class ForumPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    category = models.CharField(max_length=100, help_text="e.g., 'Python'")
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'forum_posts'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return f"{self.category}: {self.content[:50]}..."
