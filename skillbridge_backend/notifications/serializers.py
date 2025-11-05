from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Notification
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    icon = serializers.CharField(source='icon', read_only=True)
    color = serializers.CharField(source='color', read_only=True)
    time_since_created = serializers.CharField(source='time_since_created', read_only=True)
    is_recent = serializers.BooleanField(source='is_recent', read_only=True)
    related_object = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_details', 'type', 'content', 'read', 'priority',
            'icon', 'color', 'action_url', 'metadata', 'time_since_created',
            'is_recent', 'related_object', 'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']

    def get_related_object(self, obj):
        """Get related object information."""
        related = obj.get_related_object()
        if related:
            return {
                'type': related.__class__.__name__,
                'id': related.id,
                'summary': str(related)[:100]
            }
        return None


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications (internal use)."""

    class Meta:
        model = Notification
        fields = ['user', 'type', 'content', 'priority', 'action_url', 'metadata']

    def validate_type(self, value):
        """Validate notification type."""
        if value not in dict(Notification.TYPE_CHOICES):
            raise serializers.ValidationError(f"Invalid notification type: {value}")
        return value

    def validate_priority(self, value):
        """Validate priority level."""
        if value not in dict(Notification.PRIORITY_CHOICES):
            raise serializers.ValidationError(f"Invalid priority: {value}")
        return value

    def validate_content(self, value):
        """Validate content length."""
        if not value or len(value.strip()) < 5:
            raise serializers.ValidationError("Notification content must be at least 5 characters")
        return value.strip()


class NotificationMarkReadSerializer(serializers.ModelSerializer):
    """Serializer for marking notifications as read."""

    class Meta:
        model = Notification
        fields = ['read']

    def update(self, instance, validated_data):
        """Mark notification as read with timestamp."""
        instance.mark_as_read()
        return instance


class NotificationBulkActionSerializer(serializers.Serializer):
    """Serializer for bulk notification actions."""
    action = serializers.ChoiceField(choices=['mark_read', 'mark_unread', 'delete'])
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        allow_empty=False,
        help_text="List of notification IDs to perform action on"
    )

    def validate_notification_ids(self, value):
        """Validate that all notification IDs exist and belong to user."""
        request = self.context.get('request')
        if not request or not request.user:
            raise serializers.ValidationError("Authentication required")

        existing_ids = set(
            Notification.objects.filter(
                user=request.user,
                id__in=value
            ).values_list('id', flat=True)
        )

        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid notification IDs: {list(invalid_ids)}")

        return value


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification listings."""
    icon = serializers.CharField(source='icon', read_only=True)
    color = serializers.CharField(source='color', read_only=True)
    time_since_created = serializers.CharField(source='time_since_created', read_only=True)
    is_recent = serializers.BooleanField(source='is_recent', read_only=True)

    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'content', 'read', 'priority', 'icon', 'color',
            'action_url', 'time_since_created', 'is_recent', 'created_at'
        ]


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    recent_count = serializers.IntegerField()  # Last 24 hours
    by_type = serializers.DictField()
    by_priority = serializers.DictField()