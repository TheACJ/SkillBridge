from django.db import models
from django.core.exceptions import ValidationError
from uuid import uuid4
from users.models import User


class Notification(models.Model):
    TYPE_CHOICES = [
        ('match', 'Match'),
        ('progress_update', 'Progress Update'),
        ('session_reminder', 'Session Reminder'),
        ('badge_awarded', 'Badge Awarded'),
        ('system', 'System'),
        ('forum', 'Forum'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    content = models.TextField()
    read = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    action_url = models.URLField(blank=True, null=True, help_text="URL for notification action")
    metadata = models.JSONField(default=dict, help_text="Additional notification data")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['user', 'type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return f"{self.type} for {self.user.display_name}"

    def clean(self):
        """Validate notification data."""
        super().clean()

        # Validate type
        if self.type not in dict(self.TYPE_CHOICES):
            raise ValidationError({'type': f'Invalid notification type: {self.type}'})

        # Validate priority
        if self.priority not in dict(self.PRIORITY_CHOICES):
            raise ValidationError({'priority': f'Invalid priority: {self.priority}'})

        # Validate content
        if not self.content or len(self.content.strip()) < 5:
            raise ValidationError({'content': 'Notification content must be at least 5 characters'})

        # Validate metadata
        if self.metadata and not isinstance(self.metadata, dict):
            raise ValidationError({'metadata': 'Metadata must be a dictionary'})

    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        if not self.read:
            self.read = True
            self.read_at = timezone.now()
            self.save(update_fields=['read', 'read_at'])

    def mark_as_unread(self):
        """Mark notification as unread."""
        if self.read:
            self.read = False
            self.read_at = None
            self.save(update_fields=['read', 'read_at'])

    @property
    def is_recent(self):
        """Check if notification is recent (less than 24 hours old)."""
        from django.utils import timezone
        from datetime import timedelta
        return self.created_at > (timezone.now() - timedelta(hours=24))

    @property
    def time_since_created(self):
        """Get human-readable time since creation."""
        from django.utils import timezone
        from django.utils.timesince import timesince
        return timesince(self.created_at, timezone.now())

    @property
    def icon(self):
        """Get notification icon based on type."""
        icons = {
            'match': '🤝',
            'progress_update': '📈',
            'session_reminder': '⏰',
            'badge_awarded': '🏆',
            'system': 'ℹ️',
            'forum': '💬'
        }
        return icons.get(self.type, '📬')

    @property
    def color(self):
        """Get notification color based on priority."""
        colors = {
            'low': 'gray',
            'normal': 'blue',
            'high': 'orange',
            'urgent': 'red'
        }
        return colors.get(self.priority, 'blue')

    def get_related_object(self):
        """Get related object if available in metadata."""
        if not self.metadata:
            return None

        # Extract related object info from metadata
        if 'match_id' in self.metadata:
            from matches.models import MentorMatch
            try:
                return MentorMatch.objects.get(id=self.metadata['match_id'])
            except MentorMatch.DoesNotExist:
                pass

        elif 'roadmap_id' in self.metadata:
            from roadmaps.models import Roadmap
            try:
                return Roadmap.objects.get(id=self.metadata['roadmap_id'])
            except Roadmap.DoesNotExist:
                pass

        elif 'badge_id' in self.metadata:
            from badges.models import Badge
            try:
                return Badge.objects.get(id=self.metadata['badge_id'])
            except Badge.DoesNotExist:
                pass

        return None

    @classmethod
    def create_notification(cls, user, notification_type, content, priority='normal', **kwargs):
        """Class method to create a notification."""
        return cls.objects.create(
            user=user,
            type=notification_type,
            content=content,
            priority=priority,
            **kwargs
        )

    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user."""
        return cls.objects.filter(user=user, read=False).count()

    @classmethod
    def mark_all_read(cls, user):
        """Mark all notifications as read for a user."""
        from django.utils import timezone
        return cls.objects.filter(user=user, read=False).update(
            read=True,
            read_at=timezone.now()
        )

    @classmethod
    def cleanup_old_notifications(cls, days=30):
        """Clean up old read notifications."""
        from django.utils import timezone
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        # Delete old read notifications
        old_read = cls.objects.filter(read=True, created_at__lt=cutoff_date)
        deleted_count = old_read.delete()[0]

        return deleted_count
