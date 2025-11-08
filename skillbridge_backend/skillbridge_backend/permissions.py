"""
Custom permission classes for SkillBridge
Provides role-based access control and object-level permissions
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from typing import Any


class IsOwnerOrAdmin(BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow read permissions for safe methods
        if request.method in SAFE_METHODS:
            return True

        # Check if user is admin/staff
        if request.user.is_staff:
            return True

        # Check if user owns the object
        return hasattr(obj, 'user') and obj.user == request.user


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    Read permissions are allowed to any authenticated user.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class RoleBasedPermission(BasePermission):
    """
    Role-based permission system that checks user roles against required permissions.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Define role permissions mapping
        role_permissions = {
            'admin': ['create', 'read', 'update', 'delete', 'manage'],
            'mentor': ['create', 'read', 'update', 'manage_mentees'],
            'learner': ['read', 'update', 'create_basic']
        }

        user_role = request.user.role
        required_permission = getattr(view, 'required_permission', 'read')

        user_permissions = role_permissions.get(user_role, [])
        return required_permission in user_permissions

    def has_object_permission(self, request, view, obj):
        # For object-level permissions, check ownership or role
        if request.user.is_staff:
            return True

        # Check object ownership
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Special cases for different object types
        if hasattr(obj, 'mentor') and obj.mentor == request.user:
            return True

        if hasattr(obj, 'learner') and obj.learner == request.user:
            return True

        return False


class MentorPermission(BasePermission):
    """
    Permission class for mentor-specific operations.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['mentor', 'admin']
        )


class AdminOrMentorPermission(BasePermission):
    """
    Permission class that allows admin or mentor access.
    """

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.role == 'mentor')
        )


class OwnProfilePermission(BasePermission):
    """
    Permission class for users to access/modify their own profiles.
    """

    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_staff


class ForumPermission(BasePermission):
    """
    Permission class for forum operations with moderation support.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow read access to all authenticated users
        if request.method in SAFE_METHODS:
            return True

        # Allow users to modify their own posts
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Allow moderators and admins to modify any post
        return (
            request.user.is_staff or
            request.user.role in ['mentor', 'admin']
        )


class BadgePermission(BasePermission):
    """
    Permission class for badge operations.
    Only admins can award badges, mentors can view their own badges.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Only admins can create/modify badges
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            # Users can view badges awarded to them or by them
            return (
                (hasattr(obj, 'mentor') and obj.mentor == request.user) or
                request.user.is_staff
            )
        return request.user and request.user.is_staff


class NotificationPermission(BasePermission):
    """
    Permission class for notification operations.
    Users can only access their own notifications.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff


class RoadmapPermission(BasePermission):
    """
    Permission class for roadmap operations.
    Users can access their own roadmaps, shared roadmaps, or public ones.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow access to own roadmaps
        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        # Allow access to shared/public roadmaps
        if hasattr(obj, 'is_shared') and obj.is_shared:
            return True

        # Allow admin access
        return request.user.is_staff


class MatchPermission(BasePermission):
    """
    Permission class for mentor match operations.
    Users can access matches they are part of.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow access if user is part of the match
        return (
            obj.learner == request.user or
            obj.mentor == request.user or
            request.user.is_staff
        )


class ProgressPermission(BasePermission):
    """
    Permission class for progress tracking operations.
    Users can access their own progress data.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff