from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Badge
from users.serializers import UserSerializer


class BadgeSerializer(serializers.ModelSerializer):
    mentor_details = UserSerializer(source='mentor', read_only=True)
    description = serializers.CharField(source='description', read_only=True)
    icon = serializers.CharField(source='icon', read_only=True)
    rarity = serializers.CharField(source='rarity', read_only=True)

    class Meta:
        model = Badge
        fields = [
            'id', 'mentor', 'mentor_details', 'type', 'description',
            'icon', 'rarity', 'criteria', 'awarded_at'
        ]
        read_only_fields = ['id', 'awarded_at']


class BadgeCreateSerializer(serializers.ModelSerializer):
    """Serializer for awarding badges (admin only)."""

    class Meta:
        model = Badge
        fields = ['mentor', 'type', 'criteria']

    def validate_mentor(self, value):
        """Validate mentor exists and has correct role."""
        if value.role != 'mentor':
            raise serializers.ValidationError("Only mentors can receive badges")
        return value

    def validate_type(self, value):
        """Validate badge type exists."""
        if value not in Badge.get_available_badges():
            raise serializers.ValidationError(f"Invalid badge type: {value}")
        return value

    def validate_criteria(self, value):
        """Validate criteria structure and content."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Criteria must be a JSON object")

        badge_type = self.initial_data.get('type')
        if badge_type:
            # Type-specific validation
            if badge_type == 'First Steps':
                if 'first_module_completed' not in value:
                    raise serializers.ValidationError("First Steps badge requires first_module_completed")

            elif badge_type == 'Mentor':
                if 'sessions_completed' not in value or not isinstance(value['sessions_completed'], int):
                    raise serializers.ValidationError("Mentor badge requires valid sessions_completed count")

            elif badge_type == 'Dedicated Learner':
                if 'active_days_in_30' not in value or not isinstance(value['active_days_in_30'], int):
                    raise serializers.ValidationError("Dedicated Learner badge requires valid active_days_in_30")

            elif badge_type == 'Code Contributor':
                if 'total_commits' not in value or not isinstance(value['total_commits'], int):
                    raise serializers.ValidationError("Code Contributor badge requires valid total_commits")

            elif badge_type == 'Community Builder':
                if 'forum_posts' not in value or not isinstance(value['forum_posts'], int):
                    raise serializers.ValidationError("Community Builder badge requires valid forum_posts count")

        return value

    def validate(self, attrs):
        """Cross-field validation."""
        mentor = attrs.get('mentor')
        badge_type = attrs.get('type')

        if mentor and badge_type:
            # Check if mentor already has this badge
            if Badge.has_badge(mentor, badge_type):
                raise serializers.ValidationError(f"Mentor already has the {badge_type} badge")

        return attrs


class BadgeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for badge listings."""
    mentor_display_name = serializers.CharField(source='mentor.display_name', read_only=True)
    description = serializers.CharField(source='description', read_only=True)
    icon = serializers.CharField(source='icon', read_only=True)
    rarity = serializers.CharField(source='rarity', read_only=True)

    class Meta:
        model = Badge
        fields = [
            'id', 'mentor_display_name', 'type', 'description',
            'icon', 'rarity', 'awarded_at'
        ]


class BadgeAwardSerializer(serializers.Serializer):
    """Serializer for checking and awarding badges automatically."""
    mentor_id = serializers.UUIDField()
    badge_type = serializers.ChoiceField(choices=Badge.BADGE_TYPES)
    criteria = serializers.DictField()

    def validate_mentor_id(self, value):
        """Validate mentor exists."""
        from users.models import User
        try:
            mentor = User.objects.get(id=value, role='mentor', is_active=True)
            return mentor
        except User.DoesNotExist:
            raise serializers.ValidationError("Mentor not found")

    def validate_badge_type(self, value):
        """Validate badge type."""
        badge_type, _ = value  # Unpack tuple
        return badge_type

    def create(self, validated_data):
        """Award badge if criteria are met."""
        mentor = validated_data['mentor_id']
        badge_type = validated_data['badge_type']
        criteria = validated_data['criteria']

        # Check if badge already exists
        if Badge.has_badge(mentor, badge_type):
            return None

        # Create and return the badge
        return Badge.award_badge(mentor, badge_type, criteria)