from rest_framework import serializers
from .models import Roadmap


class RoadmapSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = Roadmap
        fields = ['id', 'user', 'user_email', 'domain', 'modules', 'progress', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_progress(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

    def validate_modules(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Modules must be a list")

        for module in value:
            if not isinstance(module, dict):
                raise serializers.ValidationError("Each module must be a dictionary")
            required_keys = ['name', 'resources', 'estimated_time', 'completed']
            for key in required_keys:
                if key not in module:
                    raise serializers.ValidationError(f"Module missing required field: {key}")

        return value


class RoadmapCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadmap
        fields = ['domain', 'modules']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RoadmapProgressUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Roadmap
        fields = ['progress', 'modules', 'updated_at']
        read_only_fields = ['updated_at']

    def validate_progress(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value