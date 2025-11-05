from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import ForumPost
from users.serializers import UserSerializer


class ForumPostSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='user', read_only=True)
    reply_count = serializers.SerializerMethodField()
    is_reply = serializers.BooleanField(source='is_reply', read_only=True)
    is_top_level = serializers.BooleanField(source='is_top_level', read_only=True)
    net_votes = serializers.IntegerField(source='net_votes', read_only=True)
    vote_ratio = serializers.FloatField(source='vote_ratio', read_only=True)
    thread_posts = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user', 'author_details', 'category', 'title', 'content',
            'parent', 'is_reply', 'is_top_level', 'is_pinned', 'is_locked',
            'upvotes', 'downvotes', 'net_votes', 'vote_ratio', 'view_count',
            'reply_count', 'thread_posts', 'last_activity', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_reply_count(self, obj):
        return obj.reply_count

    def get_thread_posts(self, obj):
        """Get all posts in this thread for top-level posts."""
        if obj.is_top_level:
            return ForumPostListSerializer(obj.get_thread_posts()[1:], many=True).data
        return None


class ForumPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new forum posts."""

    class Meta:
        model = ForumPost
        fields = ['category', 'title', 'content', 'parent']

    def validate_category(self, value):
        """Validate category exists."""
        if value not in dict(ForumPost.CATEGORY_CHOICES):
            raise serializers.ValidationError(f"Invalid category: {value}")
        return value

    def validate_title(self, value):
        """Validate title for top-level posts."""
        if not self.initial_data.get('parent'):  # Top-level post
            if not value or len(value.strip()) < 5:
                raise serializers.ValidationError("Title is required for top-level posts and must be at least 5 characters")
        return value.strip() if value else None

    def validate_content(self, value):
        """Validate content length."""
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters")
        return value.strip()

    def validate_parent(self, value):
        """Validate parent post exists and is not locked."""
        if value:
            if value.is_locked:
                raise serializers.ValidationError("Cannot reply to locked posts")
            if value.parent:  # Prevent replies to replies
                raise serializers.ValidationError("Cannot reply to replies")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        parent = attrs.get('parent')
        title = attrs.get('title')

        # Title is required for top-level posts
        if not parent and not title:
            raise serializers.ValidationError("Title is required for new discussions")

        # Title should not be provided for replies
        if parent and title:
            raise serializers.ValidationError("Replies cannot have titles")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ForumPostListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for forum post listings."""
    author_details = UserSerializer(source='user', read_only=True)
    reply_count = serializers.SerializerMethodField()
    net_votes = serializers.IntegerField(source='net_votes', read_only=True)
    is_recent = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'author_details', 'category', 'title', 'content',
            'reply_count', 'net_votes', 'view_count', 'is_pinned',
            'is_locked', 'is_recent', 'last_activity', 'created_at'
        ]

    def get_reply_count(self, obj):
        return obj.reply_count

    def get_is_recent(self, obj):
        """Check if post is recent (active in last 24 hours)."""
        from django.utils import timezone
        from datetime import timedelta
        return obj.last_activity > (timezone.now() - timedelta(hours=24))


class ForumPostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating forum posts."""

    class Meta:
        model = ForumPost
        fields = ['title', 'content', 'is_locked']

    def validate_title(self, value):
        """Validate title updates."""
        if self.instance.is_reply and value:
            raise serializers.ValidationError("Cannot add title to replies")
        if value and len(value.strip()) < 5:
            raise serializers.ValidationError("Title must be at least 5 characters")
        return value.strip() if value else value

    def validate_content(self, value):
        """Validate content updates."""
        if value and len(value.strip()) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters")
        return value.strip() if value else value

    def validate_is_locked(self, value):
        """Only allow locking/unlocking by post author or admin."""
        request = self.context.get('request')
        if request and value != self.instance.is_locked:
            if request.user != self.instance.user and not request.user.is_admin:
                raise serializers.ValidationError("Only post author or admin can lock/unlock posts")
        return value


class ForumVoteSerializer(serializers.Serializer):
    """Serializer for voting on forum posts."""
    vote_type = serializers.ChoiceField(choices=['upvote', 'downvote'])

    def validate_vote_type(self, value):
        """Validate vote type."""
        if value not in ['upvote', 'downvote']:
            raise serializers.ValidationError("Vote type must be 'upvote' or 'downvote'")
        return value


class ForumSearchSerializer(serializers.Serializer):
    """Serializer for forum search parameters."""
    query = serializers.CharField(max_length=100, required=False)
    category = serializers.ChoiceField(choices=ForumPost.CATEGORY_CHOICES, required=False)
    author = serializers.CharField(max_length=100, required=False)
    sort_by = serializers.ChoiceField(
        choices=['newest', 'oldest', 'most_votes', 'most_replies'],
        default='newest',
        required=False
    )
    time_filter = serializers.ChoiceField(
        choices=['all', 'day', 'week', 'month'],
        default='all',
        required=False
    )


class ForumStatsSerializer(serializers.Serializer):
    """Serializer for forum statistics."""
    total_posts = serializers.IntegerField()
    total_replies = serializers.IntegerField()
    active_users = serializers.IntegerField()
    posts_today = serializers.IntegerField()
    category_stats = serializers.ListField()