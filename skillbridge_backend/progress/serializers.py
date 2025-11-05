from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import ProgressLog
from users.serializers import UserSerializer
from roadmaps.serializers import RoadmapListSerializer


class ProgressLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    roadmap_details = RoadmapListSerializer(source='roadmap', read_only=True)
    event_description = serializers.CharField(source='event_description', read_only=True)
    points_earned = serializers.IntegerField(source='points_earned', read_only=True)
    related_url = serializers.SerializerMethodField()

    class Meta:
        model = ProgressLog
        fields = [
            'id', 'user', 'user_details', 'roadmap', 'roadmap_details',
            'event_type', 'event_description', 'details', 'points_earned',
            'related_url', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

    def get_related_url(self, obj):
        return obj.get_related_url()

    def validate_details(self, value):
        """Comprehensive details validation based on event type."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Details must be a JSON object")

        event_type = self.initial_data.get('event_type')
        if event_type:
            # Event-specific validation
            if event_type == 'commit':
                required_fields = ['repo', 'commit_hash', 'message']
                for field in required_fields:
                    if field not in value:
                        raise serializers.ValidationError(f"Commit events require '{field}' in details")

            elif event_type == 'pull_request':
                required_fields = ['pr_number', 'title', 'state']
                for field in required_fields:
                    if field not in value:
                        raise serializers.ValidationError(f"Pull request events require '{field}' in details")

            elif event_type == 'issue':
                required_fields = ['issue_number', 'title', 'state']
                for field in required_fields:
                    if field not in value:
                        raise serializers.ValidationError(f"Issue events require '{field}' in details")

            elif event_type == 'module_complete':
                required_fields = ['module_index', 'module_name']
                for field in required_fields:
                    if field not in value:
                        raise serializers.ValidationError(f"Module completion events require '{field}' in details")

        return value


class ProgressLogCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating progress log entries."""

    class Meta:
        model = ProgressLog
        fields = ['roadmap', 'event_type', 'details']

    def validate_roadmap(self, value):
        """Validate roadmap access and existence."""
        if not value:
            # Roadmap is optional for some events
            return value

        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only log progress for your own roadmaps")

        return value

    def validate_event_type(self, value):
        """Validate event type."""
        if value not in dict(ProgressLog.EVENT_CHOICES):
            raise serializers.ValidationError(f"Invalid event type: {value}")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        event_type = attrs.get('event_type')
        roadmap = attrs.get('roadmap')

        # Roadmap is required for most events
        if event_type in ['commit', 'pull_request', 'module_complete'] and not roadmap:
            raise serializers.ValidationError(f"Roadmap is required for {event_type} events")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ProgressStatsSerializer(serializers.Serializer):
    """Serializer for user progress statistics."""
    total_events = serializers.IntegerField()
    commits = serializers.IntegerField()
    pull_requests = serializers.IntegerField()
    issues = serializers.IntegerField()
    modules_completed = serializers.IntegerField()
    sessions_completed = serializers.IntegerField()
    total_points = serializers.IntegerField()
    period_days = serializers.IntegerField()


class ProgressLogListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for progress log listings."""
    event_description = serializers.CharField(source='event_description', read_only=True)
    points_earned = serializers.IntegerField(source='points_earned', read_only=True)
    roadmap_domain = serializers.CharField(source='roadmap.domain', read_only=True)

    class Meta:
        model = ProgressLog
        fields = [
            'id', 'event_type', 'event_description', 'points_earned',
            'roadmap_domain', 'timestamp'
        ]


class GitHubWebhookSerializer(serializers.Serializer):
    """Serializer for GitHub webhook payloads."""
    action = serializers.CharField()
    repository = serializers.DictField()
    commits = serializers.ListField(required=False)
    pull_request = serializers.DictField(required=False)
    issue = serializers.DictField(required=False)

    def validate_repository(self, value):
        """Validate repository data."""
        if not isinstance(value, dict) or 'full_name' not in value:
            raise serializers.ValidationError("Repository must include full_name")
        return value