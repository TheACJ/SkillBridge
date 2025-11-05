from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Roadmap


class ModuleSerializer(serializers.Serializer):
    """Serializer for individual roadmap modules."""
    name = serializers.CharField(max_length=200)
    resources = serializers.ListField()
    estimated_time = serializers.IntegerField(min_value=1, max_value=100)
    completed = serializers.BooleanField(default=False)

    def validate_resources(self, value):
        if not isinstance(value, list) or len(value) == 0:
            raise serializers.ValidationError("At least one resource is required")

        for resource in value:
            if not isinstance(resource, dict):
                raise serializers.ValidationError("Each resource must be a dictionary")
            required_keys = ['title', 'platform', 'url']
            for key in required_keys:
                if key not in resource:
                    raise serializers.ValidationError(f"Resource missing required field: {key}")
                if not isinstance(resource[key], str) or len(resource[key].strip()) == 0:
                    raise serializers.ValidationError(f"Resource {key} must be a non-empty string")

        return value


class RoadmapSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    # user_display_name removed - using email instead
    total_estimated_time = serializers.SerializerMethodField()
    completed_modules_count = serializers.SerializerMethodField()
    remaining_modules = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Roadmap
        fields = [
            'id', 'user', 'user_email', 'domain', 'modules',
            'progress', 'total_estimated_time', 'completed_modules_count',
            'remaining_modules', 'is_completed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_total_estimated_time(self, obj):
        return obj.get_total_estimated_time()

    def get_completed_modules_count(self, obj):
        return obj.get_completed_modules_count()

    def get_remaining_modules(self, obj):
        return obj.get_remaining_modules()

    def get_is_completed(self, obj):
        return obj.is_completed()

    def validate_domain(self, value):
        """Validate domain field."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("Domain must be at least 2 characters long")
        return value.strip()

    def validate_progress(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

    def validate_modules(self, value):
        """Comprehensive modules validation."""
        if not isinstance(value, list):
            raise serializers.ValidationError("Modules must be a list")

        if len(value) == 0:
            raise serializers.ValidationError("At least one module is required")

        if len(value) > 20:
            raise serializers.ValidationError("Maximum 20 modules allowed")

        module_serializer = ModuleSerializer(data=value, many=True)
        if not module_serializer.is_valid():
            raise serializers.ValidationError(module_serializer.errors)

        return value

    def update(self, instance, validated_data):
        """Custom update logic to recalculate progress."""
        modules_data = validated_data.get('modules')
        if modules_data:
            # Recalculate progress based on completed modules
            completed_count = sum(1 for module in modules_data if module.get('completed', False))
            total_count = len(modules_data)
            if total_count > 0:
                validated_data['progress'] = round((completed_count / total_count) * 100, 2)

        return super().update(instance, validated_data)


class RoadmapCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new roadmaps."""
    modules = serializers.ListField(
        child=ModuleSerializer(),
        min_length=1,
        max_length=20,
        help_text="List of learning modules"
    )

    class Meta:
        model = Roadmap
        fields = ['domain', 'modules']

    def validate_domain(self, value):
        """Validate domain uniqueness for user."""
        user = self.context['request'].user
        if Roadmap.objects.filter(user=user, domain__iexact=value.strip()).exists():
            raise serializers.ValidationError("You already have a roadmap for this domain")
        return value.strip()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user

        # Calculate initial progress
        modules_data = validated_data.get('modules', [])
        completed_count = sum(1 for module in modules_data if module.get('completed', False))
        total_count = len(modules_data)
        progress = round((completed_count / total_count) * 100, 2) if total_count > 0 else 0
        validated_data['progress'] = progress

        return super().create(validated_data)


class RoadmapProgressUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating roadmap progress."""
    module_index = serializers.IntegerField(
        min_value=0,
        required=False,
        help_text="Index of module to mark as complete"
    )
    recalculate_progress = serializers.BooleanField(
        default=True,
        help_text="Whether to recalculate progress from modules"
    )

    class Meta:
        model = Roadmap
        fields = ['progress', 'modules', 'module_index', 'recalculate_progress', 'updated_at']
        read_only_fields = ['updated_at']

    def validate_progress(self, value):
        if not (0 <= value <= 100):
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

    def validate(self, attrs):
        """Cross-field validation."""
        if 'module_index' in attrs and 'modules' in attrs:
            raise serializers.ValidationError("Cannot specify both module_index and modules")

        if 'module_index' in attrs:
            module_index = attrs['module_index']
            if module_index >= len(self.instance.modules):
                raise serializers.ValidationError(f"Module index {module_index} is out of range")

        return attrs

    def update(self, instance, validated_data):
        module_index = validated_data.pop('module_index', None)
        recalculate = validated_data.pop('recalculate_progress', True)

        # Handle module completion
        if module_index is not None:
            try:
                new_progress = instance.complete_module(module_index)
                validated_data['progress'] = new_progress
            except ValueError as e:
                raise serializers.ValidationError(str(e))

        # Update other fields
        instance = super().update(instance, validated_data)

        # Recalculate progress if requested and modules were updated
        if recalculate and 'modules' in validated_data:
            instance.progress = instance.calculate_progress()
            instance.save(update_fields=['progress'])

        return instance


class RoadmapListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for roadmap listings."""
    # user_display_name removed - using email instead
    completed_modules_count = serializers.SerializerMethodField()
    total_modules = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Roadmap
        fields = [
            'id', 'domain', 'progress', 'completed_modules_count',
            'total_modules', 'is_completed', 'created_at', 'updated_at'
        ]

    def get_completed_modules_count(self, obj):
        return obj.get_completed_modules_count()

    def get_total_modules(self, obj):
        return len(obj.modules) if obj.modules else 0

    def get_is_completed(self, obj):
        return obj.is_completed()