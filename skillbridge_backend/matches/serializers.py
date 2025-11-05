from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime
from .models import MentorMatch
from users.serializers import UserSerializer


class SessionSerializer(serializers.Serializer):
    """Serializer for individual mentoring sessions."""
    time = serializers.DateTimeField()
    topic = serializers.CharField(max_length=200)
    duration_minutes = serializers.IntegerField(min_value=15, max_value=240, default=60)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_time(self, value):
        """Validate session time is in the future."""
        if value <= datetime.now(value.tzinfo):
            raise serializers.ValidationError("Session time must be in the future")
        return value


class MentorMatchSerializer(serializers.ModelSerializer):
    learner_details = UserSerializer(source='learner', read_only=True)
    mentor_details = UserSerializer(source='mentor', read_only=True)
    upcoming_sessions = serializers.SerializerMethodField()
    match_duration_days = serializers.SerializerMethodField()
    can_rate = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    is_pending = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = MentorMatch
        fields = [
            'id', 'learner', 'mentor', 'learner_details', 'mentor_details',
            'status', 'session_schedule', 'rating', 'upcoming_sessions',
            'match_duration_days', 'can_rate', 'is_active', 'is_pending',
            'is_completed', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_upcoming_sessions(self, obj):
        return obj.get_upcoming_sessions()

    def get_match_duration_days(self, obj):
        return obj.get_match_duration_days()

    def get_can_rate(self, obj):
        return obj.can_rate()

    def get_is_active(self, obj):
        return obj.is_active

    def get_is_pending(self, obj):
        return obj.is_pending

    def get_is_completed(self, obj):
        return obj.is_completed

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_session_schedule(self, value):
        """Comprehensive session schedule validation."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Session schedule must be a list")

        if len(value) > 50:
            raise serializers.ValidationError("Maximum 50 sessions allowed")

        session_serializer = SessionSerializer(data=value, many=True)
        if not session_serializer.is_valid():
            raise serializers.ValidationError(session_serializer.errors)

        return value


class MentorMatchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new mentor matches."""
    mentor_id = serializers.UUIDField(write_only=True, help_text="ID of the mentor to match with")

    class Meta:
        model = MentorMatch
        fields = ['mentor_id']

    def validate_mentor_id(self, value):
        """Validate mentor exists and is available."""
        from users.models import User
        try:
            mentor = User.objects.get(id=value, role='mentor', is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Mentor not found or not available")

        # Check if user already has a pending/active match with this mentor
        request = self.context.get('request')
        if request and request.user:
            existing_match = MentorMatch.objects.filter(
                learner=request.user,
                mentor=mentor,
                status__in=['pending', 'active']
            ).exists()
            if existing_match:
                raise serializers.ValidationError("You already have a pending or active match with this mentor")

        return value

    def create(self, validated_data):
        mentor_id = validated_data.pop('mentor_id')
        from users.models import User
        mentor = User.objects.get(id=mentor_id)

        validated_data.update({
            'learner': self.context['request'].user,
            'mentor': mentor
        })

        return super().create(validated_data)


class MentorMatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating mentor matches."""
    action = serializers.ChoiceField(
        choices=['accept', 'reject', 'complete', 'add_session'],
        required=False,
        help_text="Action to perform on the match"
    )
    session_time = serializers.DateTimeField(required=False)
    session_topic = serializers.CharField(max_length=200, required=False)

    class Meta:
        model = MentorMatch
        fields = ['status', 'session_schedule', 'rating', 'action', 'session_time', 'session_topic']

    def validate(self, attrs):
        """Cross-field validation based on action."""
        action = attrs.get('action')
        user = self.context['request'].user

        if action == 'accept':
            if self.instance.status != 'pending':
                raise serializers.ValidationError("Only pending matches can be accepted")
            if user != self.instance.mentor:
                raise serializers.ValidationError("Only the mentor can accept matches")

        elif action == 'reject':
            if self.instance.status != 'pending':
                raise serializers.ValidationError("Only pending matches can be rejected")
            if user != self.instance.mentor:
                raise serializers.ValidationError("Only the mentor can reject matches")

        elif action == 'complete':
            if self.instance.status != 'active':
                raise serializers.ValidationError("Only active matches can be completed")
            if user not in [self.instance.learner, self.instance.mentor]:
                raise serializers.ValidationError("Only match participants can complete matches")

        elif action == 'add_session':
            if self.instance.status != 'active':
                raise serializers.ValidationError("Can only add sessions to active matches")
            if not attrs.get('session_time') or not attrs.get('session_topic'):
                raise serializers.ValidationError("session_time and session_topic are required for add_session action")

        # Rating validation
        if 'rating' in attrs:
            if self.instance.status != 'completed':
                raise serializers.ValidationError("Rating can only be set for completed matches")
            if user != self.instance.learner:
                raise serializers.ValidationError("Only learners can rate matches")

        return attrs

    def update(self, instance, validated_data):
        action = validated_data.pop('action', None)

        if action == 'accept':
            instance.accept_match()
        elif action == 'reject':
            instance.reject_match()
        elif action == 'complete':
            rating = validated_data.get('rating')
            instance.complete_match(rating=rating)
            if 'rating' in validated_data:
                validated_data.pop('rating')  # Already handled
        elif action == 'add_session':
            session_time = validated_data.pop('session_time')
            session_topic = validated_data.pop('session_topic')
            instance.add_session(session_time, session_topic)

        # Update other fields normally
        return super().update(instance, validated_data)


class MentorMatchListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for match listings."""
    learner_details = UserSerializer(source='learner', read_only=True)
    mentor_details = UserSerializer(source='mentor', read_only=True)
    upcoming_sessions_count = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()

    class Meta:
        model = MentorMatch
        fields = [
            'id', 'learner_details', 'mentor_details', 'status',
            'upcoming_sessions_count', 'rating', 'is_active', 'created_at'
        ]

    def get_upcoming_sessions_count(self, obj):
        return len(obj.get_upcoming_sessions())

    def get_is_active(self, obj):
        return obj.is_active