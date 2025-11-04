from rest_framework import serializers
from .models import MentorMatch
from users.serializers import UserSerializer


class MentorMatchSerializer(serializers.ModelSerializer):
    learner_details = UserSerializer(source='learner', read_only=True)
    mentor_details = UserSerializer(source='mentor', read_only=True)

    class Meta:
        model = MentorMatch
        fields = [
            'id', 'learner', 'mentor', 'learner_details', 'mentor_details',
            'status', 'session_schedule', 'rating', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_rating(self, value):
        if value is not None and not (1 <= value <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_session_schedule(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Session schedule must be a list")

        for session in value:
            if not isinstance(session, dict):
                raise serializers.ValidationError("Each session must be a dictionary")
            required_keys = ['time', 'topic']
            for key in required_keys:
                if key not in session:
                    raise serializers.ValidationError(f"Session missing required field: {key}")

        return value


class MentorMatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorMatch
        fields = ['mentor']

    def create(self, validated_data):
        validated_data['learner'] = self.context['request'].user
        return super().create(validated_data)


class MentorMatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentorMatch
        fields = ['status', 'session_schedule', 'rating']

    def validate(self, attrs):
        # Only allow rating when status is 'completed'
        if 'rating' in attrs and attrs.get('status') != 'completed':
            raise serializers.ValidationError("Rating can only be set when match is completed")
        return attrs