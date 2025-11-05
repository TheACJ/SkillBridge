from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from datetime import datetime
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
    rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating 1-5 after completion"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mentor_matches'
        ordering = ['-created_at']
        unique_together = ['learner', 'mentor']  # Prevent duplicate matches
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['learner', 'status']),
            models.Index(fields=['mentor', 'status']),
        ]

    def __str__(self):
        return f"Match: {self.learner.email} ↔ {self.mentor.email}"

    def clean(self):
        """Validate match data."""
        super().clean()

        # Prevent self-matching
        if self.learner == self.mentor:
            raise ValidationError("Learner and mentor cannot be the same user")

        # Validate roles
        if self.learner.role != 'learner':
            raise ValidationError({'learner': 'Learner must have learner role'})
        if self.mentor.role != 'mentor':
            raise ValidationError({'mentor': 'Mentor must have mentor role'})

        # Validate session schedule
        if self.session_schedule:
            self._validate_session_schedule()

        # Rating can only be set for completed matches
        if self.rating is not None and self.status != 'completed':
            raise ValidationError({'rating': 'Rating can only be set for completed matches'})

    def _validate_session_schedule(self):
        """Validate session schedule JSON structure."""
        if not isinstance(self.session_schedule, list):
            raise ValidationError({'session_schedule': 'Session schedule must be a list'})

        if len(self.session_schedule) > 50:
            raise ValidationError({'session_schedule': 'Maximum 50 sessions allowed'})

        for i, session in enumerate(self.session_schedule):
            if not isinstance(session, dict):
                raise ValidationError({f'session_schedule[{i}]': 'Each session must be a dictionary'})

            # Check required fields
            if 'time' not in session:
                raise ValidationError({f'session_schedule[{i}].time': 'Session time is required'})

            if 'topic' not in session:
                raise ValidationError({f'session_schedule[{i}].topic': 'Session topic is required'})

            # Validate time format (should be ISO string)
            try:
                if isinstance(session['time'], str):
                    datetime.fromisoformat(session['time'].replace('Z', '+00:00'))
            except ValueError:
                raise ValidationError({f'session_schedule[{i}].time': 'Invalid time format'})

    def accept_match(self):
        """Accept a pending match."""
        if self.status != 'pending':
            raise ValueError("Only pending matches can be accepted")

        self.status = 'active'
        self.save()

        # Trigger notifications
        from notifications.tasks import send_notification
        send_notification.delay(
            user_id=self.learner.id,
            notification_type='match',
            content=f"Your mentorship request has been accepted by {self.mentor.display_name}!"
        )
        send_notification.delay(
            user_id=self.mentor.id,
            notification_type='match',
            content=f"You've accepted {self.learner.display_name}'s mentorship request!"
        )

        return self

    def reject_match(self):
        """Reject a pending match."""
        if self.status != 'pending':
            raise ValueError("Only pending matches can be rejected")

        self.status = 'rejected'
        self.save()

        # Notify learner
        from notifications.tasks import send_notification
        send_notification.delay(
            user_id=self.learner.id,
            notification_type='match',
            content=f"Your mentorship request to {self.mentor.display_name} has been declined."
        )

        return self

    def complete_match(self, rating=None):
        """Complete an active match."""
        if self.status != 'active':
            raise ValueError("Only active matches can be completed")

        self.status = 'completed'
        if rating is not None:
            self.rating = rating
        self.save()

        # Update mentor's rating
        self.mentor.update_profile_rating()

        # Trigger completion notifications and badges
        from notifications.tasks import send_notification
        from badges.tasks import check_and_award_badge

        send_notification.delay(
            user_id=self.learner.id,
            notification_type='match',
            content=f"Your mentorship with {self.mentor.display_name} has been completed!"
        )
        send_notification.delay(
            user_id=self.mentor.id,
            notification_type='match',
            content=f"Your mentorship with {self.learner.display_name} has been completed!"
        )

        # Check for badges
        check_and_award_badge.delay(self.mentor.id, 'Mentor', {'sessions_completed': 1})

        return self

    def add_session(self, session_time, topic):
        """Add a new session to the schedule."""
        if not isinstance(self.session_schedule, list):
            self.session_schedule = []

        session = {
            'time': session_time.isoformat() if hasattr(session_time, 'isoformat') else str(session_time),
            'topic': str(topic)
        }

        self.session_schedule.append(session)
        self.save()

        return session

    def get_upcoming_sessions(self):
        """Get list of upcoming sessions."""
        from datetime import datetime
        now = datetime.now()

        upcoming = []
        for session in self.session_schedule:
            try:
                session_time = datetime.fromisoformat(session['time'].replace('Z', '+00:00'))
                if session_time > now:
                    upcoming.append(session)
            except (ValueError, KeyError):
                continue

        return sorted(upcoming, key=lambda x: x['time'])

    def get_completed_sessions_count(self):
        """Get count of completed sessions (placeholder for future implementation)."""
        # This would be implemented when we add session completion tracking
        return 0

    def can_rate(self):
        """Check if this match can be rated."""
        return self.status == 'completed' and self.rating is None

    def get_match_duration_days(self):
        """Get match duration in days."""
        from datetime import datetime
        duration = datetime.now() - self.created_at.replace(tzinfo=None)
        return duration.days

    @property
    def is_active(self):
        """Check if match is currently active."""
        return self.status == 'active'

    @property
    def is_pending(self):
        """Check if match is pending."""
        return self.status == 'pending'

    @property
    def is_completed(self):
        """Check if match is completed."""
        return self.status == 'completed'
