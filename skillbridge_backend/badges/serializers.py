from rest_framework import serializers
from .models import Badge
from users.serializers import UserSerializer


class BadgeSerializer(serializers.ModelSerializer):
    mentor_details = UserSerializer(source='mentor', read_only=True)

    class Meta:
        model = Badge
        fields = ['id', 'mentor', 'mentor_details', 'type', 'criteria', 'awarded_at']
        read_only_fields = ['id', 'awarded_at']


class BadgeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['mentor', 'type', 'criteria']

    def validate_criteria(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Criteria must be a JSON object")
        return value