from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
import re


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

    def available_mentors(self, learner_skills=None, location=None, min_rating=0):
        """
        Get available mentors filtered by skills, location, and rating.
        """
        mentors = self.get_queryset().filter(role='mentor', is_active=True)

        if learner_skills:
            # Filter mentors who have matching skills
            skill_filters = models.Q()
            for skill in learner_skills:
                skill_filters |= models.Q(profile__skills__icontains=skill.lower())
            mentors = mentors.filter(skill_filters)

        if location:
            mentors = mentors.filter(profile__location__icontains=location)

        # Order by rating (assuming rating is stored in profile)
        mentors = mentors.order_by('-profile__rating')

        return mentors

    def get_mentors_by_expertise(self, domain):
        """
        Get mentors specialized in a specific domain.
        """
        return self.get_queryset().filter(
            role='mentor',
            is_active=True,
            profile__expertise__icontains=domain.lower()
        )


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('learner', 'Learner'),
        ('mentor', 'Mentor'),
        ('admin', 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='learner')
    profile = models.JSONField(default=dict, help_text="JSON field for skills, location, availability, github_username, etc.")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'users'

    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_groups',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_permissions',
        related_query_name='custom_user',
    )

    def __str__(self):
        return self.email

    def clean(self):
        """Validate user data."""
        super().clean()

        # Validate email format
        if self.email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValidationError({'email': 'Enter a valid email address.'})

        # Validate profile structure
        if self.profile:
            self._validate_profile()

    def _validate_profile(self):
        """Validate profile JSON structure."""
        required_fields = ['skills', 'location']
        for field in required_fields:
            if field not in self.profile:
                raise ValidationError({f'profile.{field}': f'{field} is required in profile'})

        # Validate skills
        if 'skills' in self.profile:
            skills = self.profile['skills']
            if not isinstance(skills, list):
                raise ValidationError({'profile.skills': 'Skills must be a list'})
            if len(skills) > 20:
                raise ValidationError({'profile.skills': 'Maximum 20 skills allowed'})

        # Validate availability for mentors
        if self.role == 'mentor' and 'availability' in self.profile:
            availability = self.profile['availability']
            if not isinstance(availability, (int, float)) or not (0 <= availability <= 168):
                raise ValidationError({'profile.availability': 'Availability must be between 0-168 hours/week'})

        # Validate rating if present
        if 'rating' in self.profile:
            rating = self.profile['rating']
            if not isinstance(rating, (int, float)) or not (0 <= rating <= 5):
                raise ValidationError({'profile.rating': 'Rating must be between 0-5'})

    def has_skill(self, skill):
        """Check if user has a specific skill."""
        if not self.profile or 'skills' not in self.profile:
            return False
        return skill.lower() in [s.lower() for s in self.profile['skills']]

    def get_mentor_rating(self):
        """Get mentor's average rating from completed matches."""
        if self.role != 'mentor':
            return None

        from matches.models import MentorMatch
        completed_matches = MentorMatch.objects.filter(
            mentor=self,
            status='completed',
            rating__isnull=False
        )

        if not completed_matches.exists():
            return 0.0

        return completed_matches.aggregate(avg_rating=models.Avg('rating'))['avg_rating']

    def get_completion_rate(self):
        """Calculate user's roadmap completion rate."""
        roadmaps = self.roadmaps.all()
        if not roadmaps.exists():
            return 0.0

        completed_roadmaps = roadmaps.filter(progress=100.0).count()
        return (completed_roadmaps / roadmaps.count()) * 100

    def update_profile_rating(self):
        """Update the rating in profile based on actual match ratings."""
        actual_rating = self.get_mentor_rating()
        if actual_rating is not None:
            if not self.profile:
                self.profile = {}
            self.profile['rating'] = round(actual_rating, 2)
            self.save(update_fields=['profile'])

    @property
    def is_mentor(self):
        return self.role == 'mentor'

    @property
    def is_learner(self):
        return self.role == 'learner'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def display_name(self):
        """Get a display name for the user."""
        if self.profile and 'display_name' in self.profile:
            return self.profile['display_name']
        return self.email.split('@')[0]

    @property
    def skills_list(self):
        """Get user's skills as a list."""
        if not self.profile or 'skills' not in self.profile:
            return []
        return self.profile['skills']

    @property
    def location(self):
        """Get user's location."""
        if not self.profile or 'location' not in self.profile:
            return None
        return self.profile['location']

    @property
    def availability_hours(self):
        """Get user's availability in hours per week."""
        if not self.profile or 'availability' not in self.profile:
            return 0
        return self.profile['availability']
