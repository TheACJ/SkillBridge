from django.db import models
from django.core.exceptions import ValidationError
from uuid import uuid4
from users.models import User
from roadmaps.models import Roadmap


class ProgressLog(models.Model):
    EVENT_CHOICES = [
        ('commit', 'Commit'),
        ('pull_request', 'Pull Request'),
        ('issue', 'Issue'),
        ('module_complete', 'Module Complete'),
        ('roadmap_created', 'Roadmap Created'),
        ('session_completed', 'Session Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_logs')
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='progress_logs', null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_CHOICES)
    details = models.JSONField(help_text="Event-specific details")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'progress_logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'roadmap']),
            models.Index(fields=['event_type']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'event_type']),
        ]

    def __str__(self):
        roadmap_info = f" on {self.roadmap.domain}" if self.roadmap else ""
        return f"{self.user.email} - {self.event_type}{roadmap_info}"

    def clean(self):
        """Validate progress log data."""
        super().clean()

        # Validate event_type
        if self.event_type not in dict(self.EVENT_CHOICES):
            raise ValidationError({'event_type': f'Invalid event type: {self.event_type}'})

        # Validate details based on event type
        if self.details:
            self._validate_details()

        # Roadmap is required for most events
        if self.event_type in ['commit', 'pull_request', 'module_complete'] and not self.roadmap:
            raise ValidationError({'roadmap': f'Roadmap is required for {self.event_type} events'})

    def _validate_details(self):
        """Validate details JSON based on event type."""
        if not isinstance(self.details, dict):
            raise ValidationError({'details': 'Details must be a dictionary'})

        # Event-specific validation
        if self.event_type == 'commit':
            required_fields = ['repo', 'commit_hash', 'message']
            for field in required_fields:
                if field not in self.details:
                    raise ValidationError({f'details.{field}': f'{field} is required for commit events'})

        elif self.event_type == 'pull_request':
            required_fields = ['pr_number', 'title', 'state']
            for field in required_fields:
                if field not in self.details:
                    raise ValidationError({f'details.{field}': f'{field} is required for pull request events'})

        elif self.event_type == 'issue':
            required_fields = ['issue_number', 'title', 'state']
            for field in required_fields:
                if field not in self.details:
                    raise ValidationError({f'details.{field}': f'{field} is required for issue events'})

        elif self.event_type == 'module_complete':
            required_fields = ['module_index', 'module_name']
            for field in required_fields:
                if field not in self.details:
                    raise ValidationError({f'details.{field}': f'{field} is required for module completion events'})

    @property
    def event_description(self):
        """Get human-readable event description."""
        descriptions = {
            'commit': 'Code commit',
            'pull_request': 'Pull request',
            'issue': 'Issue created/updated',
            'module_complete': 'Module completed',
            'roadmap_created': 'Roadmap created',
            'session_completed': 'Mentorship session completed'
        }
        return descriptions.get(self.event_type, self.event_type)

    @property
    def points_earned(self):
        """Calculate points earned for this event."""
        points_map = {
            'commit': 10,
            'pull_request': 25,
            'issue': 5,
            'module_complete': 50,
            'roadmap_created': 20,
            'session_completed': 30
        }
        return points_map.get(self.event_type, 0)

    def get_related_url(self):
        """Get URL to related resource if available."""
        if self.event_type == 'commit' and 'url' in self.details:
            return self.details['url']
        elif self.event_type == 'pull_request' and 'url' in self.details:
            return self.details['url']
        elif self.event_type == 'issue' and 'url' in self.details:
            return self.details['url']
        return None

    @classmethod
    def log_event(cls, user, event_type, details, roadmap=None):
        """Class method to create a progress log entry."""
        return cls.objects.create(
            user=user,
            roadmap=roadmap,
            event_type=event_type,
            details=details
        )

    @classmethod
    def get_user_stats(cls, user, days=30):
        """Get user progress statistics for the last N days."""
        from django.utils import timezone
        from django.db.models import Count

        since_date = timezone.now() - timezone.timedelta(days=days)

        stats = cls.objects.filter(
            user=user,
            timestamp__gte=since_date
        ).aggregate(
            total_events=Count('id'),
            commits=Count('id', filter=models.Q(event_type='commit')),
            pull_requests=Count('id', filter=models.Q(event_type='pull_request')),
            issues=Count('id', filter=models.Q(event_type='issue')),
            modules_completed=Count('id', filter=models.Q(event_type='module_complete')),
            sessions_completed=Count('id', filter=models.Q(event_type='session_completed'))
        )

        # Calculate total points
        recent_logs = cls.objects.filter(user=user, timestamp__gte=since_date)
        total_points = sum(log.points_earned for log in recent_logs)

        stats['total_points'] = total_points
        stats['period_days'] = days

        return stats

    @classmethod
    def get_recent_activity(cls, user, limit=10):
        """Get recent activity for a user."""
        return cls.objects.filter(user=user).select_related('roadmap')[:limit]
