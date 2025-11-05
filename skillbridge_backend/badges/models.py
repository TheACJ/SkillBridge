from django.db import models
from django.core.exceptions import ValidationError
from uuid import uuid4
from users.models import User


class Badge(models.Model):
    BADGE_TYPES = [
        ('First Steps', 'First Steps'),
        ('Mentor', 'Mentor'),
        ('Dedicated Learner', 'Dedicated Learner'),
        ('Code Contributor', 'Code Contributor'),
        ('Community Builder', 'Community Builder'),
        ('Mentor Extraordinaire', 'Mentor Extraordinaire'),
        ('Knowledge Sharer', 'Knowledge Sharer'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    type = models.CharField(max_length=100, choices=BADGE_TYPES, help_text="Badge type")
    criteria = models.JSONField(help_text="Criteria met for earning the badge")
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'badges'
        ordering = ['-awarded_at']
        unique_together = ['mentor', 'type']  # One badge per type per mentor
        indexes = [
            models.Index(fields=['mentor']),
            models.Index(fields=['type']),
            models.Index(fields=['awarded_at']),
        ]

    def __str__(self):
        return f"{self.type} - {self.mentor.display_name}"

    def clean(self):
        """Validate badge data."""
        super().clean()

        # Validate badge type
        if self.type and self.type not in dict(self.BADGE_TYPES):
            raise ValidationError({'type': f'Invalid badge type: {self.type}'})

        # Validate criteria
        if self.criteria:
            self._validate_criteria()

        # Ensure mentor has correct role
        if self.mentor and self.mentor.role != 'mentor':
            raise ValidationError({'mentor': 'Only mentors can receive badges'})

    def _validate_criteria(self):
        """Validate criteria JSON structure."""
        if not isinstance(self.criteria, dict):
            raise ValidationError({'criteria': 'Criteria must be a dictionary'})

        # Type-specific validation
        if self.type == 'First Steps':
            if 'first_module_completed' not in self.criteria:
                raise ValidationError({'criteria': 'First Steps badge requires first_module_completed'})

        elif self.type == 'Mentor':
            if 'sessions_completed' not in self.criteria or not isinstance(self.criteria['sessions_completed'], int):
                raise ValidationError({'criteria': 'Mentor badge requires valid sessions_completed count'})

        elif self.type == 'Dedicated Learner':
            if 'active_days_in_30' not in self.criteria or not isinstance(self.criteria['active_days_in_30'], int):
                raise ValidationError({'criteria': 'Dedicated Learner badge requires valid active_days_in_30'})

        elif self.type == 'Code Contributor':
            if 'total_commits' not in self.criteria or not isinstance(self.criteria['total_commits'], int):
                raise ValidationError({'criteria': 'Code Contributor badge requires valid total_commits'})

        elif self.type == 'Community Builder':
            if 'forum_posts' not in self.criteria or not isinstance(self.criteria['forum_posts'], int):
                raise ValidationError({'criteria': 'Community Builder badge requires valid forum_posts count'})

    @property
    def description(self):
        """Get badge description."""
        descriptions = {
            'First Steps': 'Completed your first learning module',
            'Mentor': 'Completed your first mentorship session',
            'Dedicated Learner': '20+ days of consistent learning activity',
            'Code Contributor': '100+ code commits',
            'Community Builder': 'Active forum contributor',
            'Mentor Extraordinaire': '10+ highly-rated mentorship sessions',
            'Knowledge Sharer': 'Helped 5+ learners complete roadmaps'
        }
        return descriptions.get(self.type, self.type)

    @property
    def icon(self):
        """Get badge icon identifier."""
        icons = {
            'First Steps': '🌟',
            'Mentor': '🏆',
            'Dedicated Learner': '📚',
            'Code Contributor': '💻',
            'Community Builder': '🤝',
            'Mentor Extraordinaire': '⭐',
            'Knowledge Sharer': '🎓'
        }
        return icons.get(self.type, '🏅')

    @property
    def rarity(self):
        """Get badge rarity level."""
        rarities = {
            'First Steps': 'common',
            'Mentor': 'common',
            'Dedicated Learner': 'uncommon',
            'Code Contributor': 'uncommon',
            'Community Builder': 'uncommon',
            'Mentor Extraordinaire': 'rare',
            'Knowledge Sharer': 'rare'
        }
        return rarities.get(self.type, 'common')

    def meets_criteria(self, user_criteria):
        """Check if provided criteria meets badge requirements."""
        if not self.criteria:
            return False

        # Compare criteria values
        for key, required_value in self.criteria.items():
            if key not in user_criteria:
                return False
            if isinstance(required_value, (int, float)):
                if user_criteria[key] < required_value:
                    return False
            elif user_criteria[key] != required_value:
                return False

        return True

    @classmethod
    def get_available_badges(cls):
        """Get all available badge types."""
        return [badge[0] for badge in cls.BADGE_TYPES]

    @classmethod
    def get_user_badges(cls, user):
        """Get all badges for a user."""
        return cls.objects.filter(mentor=user).order_by('-awarded_at')

    @classmethod
    def has_badge(cls, user, badge_type):
        """Check if user has a specific badge."""
        return cls.objects.filter(mentor=user, type=badge_type).exists()

    @classmethod
    def award_badge(cls, mentor, badge_type, criteria):
        """Award a badge to a mentor if they don't already have it."""
        if cls.has_badge(mentor, badge_type):
            return None

        badge = cls.objects.create(
            mentor=mentor,
            type=badge_type,
            criteria=criteria
        )

        return badge
