from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from uuid import uuid4
from users.models import User


class ForumPost(models.Model):
    CATEGORY_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('web-development', 'Web Development'),
        ('data-science', 'Data Science'),
        ('machine-learning', 'Machine Learning'),
        ('mobile-development', 'Mobile Development'),
        ('devops', 'DevOps'),
        ('databases', 'Databases'),
        ('career-advice', 'Career Advice'),
        ('general', 'General Discussion'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_posts')
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, help_text="Forum category")
    title = models.CharField(max_length=200, validators=[MinLengthValidator(5)], help_text="Post title", default="Untitled Post")
    content = models.TextField(validators=[MinLengthValidator(10)], help_text="Post content")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    is_pinned = models.BooleanField(default=False, help_text="Pin post to top of category")
    is_locked = models.BooleanField(default=False, help_text="Lock post from new replies")
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'forum_posts'
        ordering = ['-is_pinned', '-last_activity']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['parent']),
            models.Index(fields=['user']),
            models.Index(fields=['is_pinned']),
            models.Index(fields=['last_activity']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.category}: {self.title}"

    def clean(self):
        """Validate forum post data."""
        super().clean()

        # Validate category
        if self.category not in dict(self.CATEGORY_CHOICES):
            raise ValidationError({'category': f'Invalid category: {self.category}'})

        # Validate title length
        if self.title and len(self.title.strip()) < 5:
            raise ValidationError({'title': 'Title must be at least 5 characters'})

        # Validate content length
        if self.content and len(self.content.strip()) < 10:
            raise ValidationError({'content': 'Content must be at least 10 characters'})

        # Prevent replies to replies (max depth 1)
        if self.parent and self.parent.parent:
            raise ValidationError({'parent': 'Cannot reply to a reply'})

        # Only allow pinning for top-level posts
        if self.is_pinned and self.parent:
            raise ValidationError({'is_pinned': 'Only top-level posts can be pinned'})

    def save(self, *args, **kwargs):
        """Override save to update last_activity."""
        # Update parent's last_activity if this is a reply
        if self.parent:
            self.parent.last_activity = self.created_at
            self.parent.save(update_fields=['last_activity'])

        super().save(*args, **kwargs)

    @property
    def is_reply(self):
        """Check if this is a reply post."""
        return self.parent is not None

    @property
    def is_top_level(self):
        """Check if this is a top-level post."""
        return self.parent is None

    @property
    def reply_count(self):
        """Get count of replies."""
        return self.replies.count()

    @property
    def net_votes(self):
        """Get net vote score."""
        return self.upvotes - self.downvotes

    @property
    def vote_ratio(self):
        """Get vote ratio (upvotes / total votes)."""
        total_votes = self.upvotes + self.downvotes
        return (self.upvotes / total_votes) if total_votes > 0 else 0

    def get_thread_posts(self):
        """Get all posts in this thread (including replies)."""
        if self.is_top_level:
            return [self] + list(self.replies.all())
        else:
            # If this is a reply, get the thread from the parent
            return self.parent.get_thread_posts()

    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def upvote(self, user):
        """Add upvote from user."""
        # In a real implementation, you'd track individual user votes
        # For now, just increment the counter
        self.upvotes += 1
        self.save(update_fields=['upvotes'])

    def downvote(self, user):
        """Add downvote from user."""
        # In a real implementation, you'd track individual user votes
        self.downvotes += 1
        self.save(update_fields=['downvotes'])

    @classmethod
    def get_popular_posts(cls, category=None, limit=10):
        """Get popular posts by vote score."""
        queryset = cls.objects.filter(parent__isnull=True)  # Only top-level posts

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-upvotes', '-created_at')[:limit]

    @classmethod
    def get_recent_posts(cls, category=None, limit=20):
        """Get recent posts."""
        queryset = cls.objects.filter(parent__isnull=True)  # Only top-level posts

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-created_at')[:limit]

    @classmethod
    def get_category_stats(cls):
        """Get statistics for each category."""
        from django.db.models import Count

        return cls.objects.filter(parent__isnull=True).values('category').annotate(
            post_count=Count('id'),
            total_replies=Count('replies')
        ).order_by('-post_count')

    @classmethod
    def search_posts(cls, query, category=None):
        """Search posts by title and content."""
        queryset = cls.objects.filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        )

        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-created_at')
