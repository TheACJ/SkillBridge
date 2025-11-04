from rest_framework import serializers
from .models import Notification
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'user_details', 'type', 'content', 'read', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationMarkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['read']

    def update(self, instance, validated_data):
        instance.read = True
        instance.save()
        return instance