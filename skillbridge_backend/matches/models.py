from django.db import models
from uuid import uuid4
from users.models import User


class MentorMatch(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    learner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learner_matches')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentor_matches')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    session_schedule = models.JSONField(default=list, help_text="Array of {time: Timestamp, topic: String}")
    rating = models.IntegerField(null=True, blank=True, help_text="Rating 1-5 after completion")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mentor_matches'
        ordering = ['-created_at']
        unique_together = ['learner', 'mentor']  # Prevent duplicate matches

    def __str__(self):
        return f"Match: {self.learner.email} ↔ {self.mentor.email}"
