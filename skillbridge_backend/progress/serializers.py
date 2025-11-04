from rest_framework import serializers
from .models import ProgressLog
from users.serializers import UserSerializer
from roadmaps.serializers import RoadmapSerializer


class ProgressLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    roadmap_details = RoadmapSerializer(source='roadmap', read_only=True)

    class Meta:
        model = ProgressLog
        fields = [
            'id', 'user', 'user_details', 'roadmap', 'roadmap_details',
            'event_type', 'details', 'timestamp'
        ]
        read_only_fields = ['id', 'timestamp']

    def validate_details(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Details must be a JSON object")
        return value


class ProgressLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressLog
        fields = ['roadmap', 'event_type', 'details']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)