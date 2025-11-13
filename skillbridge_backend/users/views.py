from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.conf import settings
from roadmaps.models import Roadmap
from matches.models import MentorMatch
from forum.models import ForumPost
from notifications.models import Notification
from .models import User
from .serializers import UserSerializer, UserProfileUpdateSerializer

# Authentication views
@api_view(['POST'])
def register_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    user = authenticate(email=email, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
        })
    except Exception:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def request_password_reset(request):
    email = request.data.get('email')
    try:
        user = User.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
        # TODO:Send email logic here
        return Response({'message': 'Password reset email sent'})
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reset_password(request):
    uidb64 = request.data.get('uid')
    token = request.data.get('token')
    password = request.data.get('password')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            user.set_password(password)
            user.save()
            return Response({'message': 'Password reset successful'})
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception:
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(UserSerializer(request.user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MentorListView(APIView):
    def get(self, request):
        mentors = User.objects.filter(role='mentor').select_related()
        serializer = UserSerializer(mentors, many=True)
        return Response(serializer.data)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
@cache_page(300)  # Cache for 5 minutes
def get_user_statistics(request):
    """
    Get user statistics - roadmaps, matches, forum posts, etc.
    """
    user = request.user

    stats = {
        'total_roadmaps': Roadmap.objects.filter(user=user).only('id').count(),
        'completed_roadmaps': Roadmap.objects.filter(user=user, progress=100.0).only('id').count(),
        'active_matches': MentorMatch.objects.filter(
            learner=user, status__in=['pending', 'active']
        ).only('id').count() if user.role != 'mentor' else MentorMatch.objects.filter(
            mentor=user, status__in=['pending', 'active']
        ).only('id').count(),
        'total_forum_posts': ForumPost.objects.filter(user=user).only('id').count(),
        'unread_notifications': Notification.objects.filter(user=user, read=False).only('id').count(),
    }

    # Add role-specific stats
    if user.role == 'mentor':
        from badges.models import Badge
        stats.update({
            'badges_awarded': Badge.objects.filter(mentor=user).only('id').count(),
            'average_rating': user.profile.get('rating', 0.0) if user.profile else 0.0,
            'total_mentees': MentorMatch.objects.filter(
                mentor=user, status='completed'
            ).only('id').count(),
        })

    return Response(stats)
