from rest_framework import serializers
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    skills_list = serializers.ListField(read_only=True)
    location = serializers.CharField(read_only=True)
    availability_hours = serializers.IntegerField(read_only=True)
    mentor_rating = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'email', 'role', 'profile', 'display_name', 'skills_list',
            'location', 'availability_hours', 'mentor_rating', 'completion_rate',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_mentor_rating(self, obj):
        if obj.role == 'mentor':
            return obj.get_mentor_rating()
        return None

    def get_completion_rate(self, obj):
        return obj.get_completion_rate()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'role', 'profile', 'password', 'password_confirm']

    def validate_email(self, value):
        """Validate email uniqueness and format."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_role(self, value):
        """Validate role choices."""
        if value not in ['learner', 'mentor']:
            raise serializers.ValidationError("Role must be either 'learner' or 'mentor'.")
        return value

    def validate_profile(self, value):
        """Comprehensive profile validation."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Profile must be a JSON object")

        # Required fields
        required_fields = ['skills', 'location']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Profile must contain '{field}' field")

        # Skills validation
        if 'skills' in value:
            skills = value['skills']
            if not isinstance(skills, list):
                raise serializers.ValidationError("Skills must be a list")
            if len(skills) > 20:
                raise serializers.ValidationError("Maximum 20 skills allowed")
            if len(skills) < 1:
                raise serializers.ValidationError("At least one skill is required")

            # Validate skill format
            for skill in skills:
                if not isinstance(skill, str) or len(skill.strip()) < 2:
                    raise serializers.ValidationError("Each skill must be a string with at least 2 characters")

        # Location validation
        if 'location' in value:
            location = value['location']
            if not isinstance(location, str) or len(location.strip()) < 2:
                raise serializers.ValidationError("Location must be a string with at least 2 characters")

        # Availability validation (for mentors)
        if 'availability' in value:
            availability = value['availability']
            if not isinstance(availability, (int, float)) or not (0 <= availability <= 168):
                raise serializers.ValidationError("Availability must be between 0-168 hours/week")

        # Learning goals validation (for learners)
        if 'learning_goals' in value:
            goals = value['learning_goals']
            if not isinstance(goals, list):
                raise serializers.ValidationError("Learning goals must be a list")

        return value

    def validate(self, attrs):
        """Cross-field validation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")

        # Additional validation using model validation
        try:
            user = User(**{k: v for k, v in attrs.items() if k not in ['password', 'password_confirm']})
            user.clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role', 'profile', 'updated_at']
        read_only_fields = ['updated_at']

    def validate_role(self, value):
        """Prevent role changes for existing users."""
        if self.instance and self.instance.role != value:
            raise serializers.ValidationError("Role cannot be changed after registration")
        return value

    def validate_profile(self, value):
        """Validate profile updates."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Profile must be a JSON object")

        # For updates, we allow partial updates but validate what's provided
        if 'skills' in value:
            skills = value['skills']
            if not isinstance(skills, list):
                raise serializers.ValidationError("Skills must be a list")
            if len(skills) > 20:
                raise serializers.ValidationError("Maximum 20 skills allowed")

        if 'availability' in value:
            availability = value['availability']
            if not isinstance(availability, (int, float)) or not (0 <= availability <= 168):
                raise serializers.ValidationError("Availability must be between 0-168 hours/week")

        return value

    def update(self, instance, validated_data):
        """Custom update logic."""
        profile_data = validated_data.pop('profile', {})

        # Update profile by merging with existing data
        if profile_data:
            current_profile = instance.profile or {}
            current_profile.update(profile_data)
            instance.profile = current_profile

        return super().update(instance, validated_data)


class MentorListSerializer(serializers.ModelSerializer):
    """Serializer for mentor listings with filtering."""
    # display_name field removed - redundant with email
    skills_list = serializers.ListField(read_only=True)
    location = serializers.CharField(read_only=True)
    availability_hours = serializers.IntegerField(read_only=True)
    mentor_rating = serializers.SerializerMethodField()
    completion_rate = serializers.SerializerMethodField()
    mentor_rating = serializers.SerializerMethodField()
    total_sessions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'display_name', 'email', 'skills_list', 'location',
            'availability_hours', 'mentor_rating', 'total_sessions'
        ]

    def get_mentor_rating(self, obj):
        return obj.get_mentor_rating()

    def get_total_sessions(self, obj):
        from matches.models import MentorMatch
        return MentorMatch.objects.filter(
            mentor=obj,
            status__in=['active', 'completed']
        ).count()