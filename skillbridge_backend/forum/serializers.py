from rest_framework import serializers
from .models import ForumPost
from users.serializers import UserSerializer


class ForumPostSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='user', read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'user', 'author_details', 'category', 'content',
            'parent', 'reply_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_reply_count(self, obj):
        return obj.replies.count()


class ForumPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumPost
        fields = ['category', 'content', 'parent']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ForumPostListSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source='user', read_only=True)
    reply_count = serializers.SerializerMethodField()

    class Meta:
        model = ForumPost
        fields = [
            'id', 'author_details', 'category', 'content',
            'reply_count', 'created_at'
        ]

    def get_reply_count(self, obj):
        return obj.replies.count()