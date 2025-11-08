import logging
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from .models import Roadmap
from .serializers import RoadmapSerializer, RoadmapCreateSerializer, RoadmapProgressUpdateSerializer


class RoadmapListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoadmapCreateSerializer
        return RoadmapSerializer

    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user).select_related()

    def list(self, request, *args, **kwargs):
        # Cache user roadmaps for 5 minutes
        cache_key = f"user_roadmaps_{request.user.id}"
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)

        queryset = Roadmap.objects.filter(user=request.user).select_related()
        serializer = RoadmapSerializer(queryset, many=True)
        cache.set(cache_key, serializer.data, 300)  # 5 minutes
        return Response(serializer.data)

    def perform_create(self, serializer):
        roadmap = serializer.save(user=self.request.user)
        # Invalidate cache when new roadmap is created
        cache_key = f"user_roadmaps_{self.request.user.id}"
        cache.delete(cache_key)


class RoadmapDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user).select_related()

    def perform_update(self, serializer):
        roadmap = serializer.save()
        # Invalidate cache when roadmap is updated
        cache_key = f"user_roadmaps_{self.request.user.id}"
        cache.delete(cache_key)

    def perform_destroy(self, instance):
        # Invalidate cache when roadmap is deleted
        cache_key = f"user_roadmaps_{self.request.user.id}"
        cache.delete(cache_key)
        instance.delete()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_roadmap(request):
    """
    Generate a personalized roadmap using OpenAI integration
    """
    from .integrations import OpenAIIntegration

    domain = request.data.get('domain')
    skill_level = request.data.get('skill_level', 'beginner')
    time_availability = request.data.get('time_availability', 'part-time')

    if not domain:
        return Response({'error': 'Domain is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()

        # Get user context for personalization
        user = request.user
        user_context = {
            'skills': user.profile.get('skills', []) if user.profile else [],
            'learning_goals': user.profile.get('learning_goals', []) if user.profile else [],
            'experience_level': user.profile.get('experience_level', 'beginner') if user.profile else 'beginner'
        }

        # Generate roadmap using service (with caching)
        from .services import RoadmapService
        roadmap_data = RoadmapService.generate_roadmap(
            domain=domain,
            skill_level=skill_level,
            time_availability=time_availability,
            user_context=user_context
        )

        serializer = RoadmapCreateSerializer(data=roadmap_data, context={'request': request})
        if serializer.is_valid():
            roadmap = serializer.save()
            # Invalidate user cache when new roadmap is created
            RoadmapService.invalidate_user_cache(request.user.id)
            return Response(RoadmapSerializer(roadmap).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        return Response({'error': 'Failed to generate roadmap'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PATCH'])
@permission_classes([permissions.IsAuthenticated])
def update_roadmap_progress(request, roadmap_id):
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)

    serializer = RoadmapProgressUpdateSerializer(roadmap, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # Invalidate progress cache when progress is updated
        from .services import RoadmapService
        RoadmapService.invalidate_roadmap_cache(roadmap_id)
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def share_roadmap(request, roadmap_id):
    """
    Share a roadmap with other users
    """
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)

    share_type = request.data.get('share_type', 'public')  # 'public', 'private', 'link'

    if share_type not in ['public', 'private', 'link']:
        return Response({'error': 'Invalid share type'}, status=status.HTTP_400_BAD_REQUEST)

    # Create a shareable token
    import uuid
    share_token = str(uuid.uuid4()) if share_type == 'link' else None

    # Store sharing preference (would need additional fields in production)
    roadmap_data = RoadmapSerializer(roadmap).data
    roadmap_data['share_type'] = share_type
    roadmap_data['share_token'] = share_token
    roadmap_data['shared_at'] = request.build_absolute_uri(f'/api/v1/roadmaps/shared/{share_token}/') if share_token else None

    logger.info(f"Roadmap {roadmap_id} shared as {share_type} by {request.user.email}")

    return Response({
        'message': f'Roadmap shared as {share_type}',
        'share_type': share_type,
        'shared_at': roadmap_data['shared_at'],
        'share_token': share_token
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_shared_roadmap(request, token):
    """
    Access a shared roadmap using token
    """
    try:
        # Find roadmap by token (would need token field in production)
        # For now, this is a placeholder
        return Response({'error': 'Shared roadmap access not fully implemented'},
                       status=status.HTTP_501_NOT_IMPLEMENTED)
    except Exception as e:
        logger.error(f"Error accessing shared roadmap: {str(e)}")
        return Response({'error': 'Failed to access shared roadmap'},
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_roadmap_analytics(request, roadmap_id):
    """
    Get analytics for a roadmap (views, progress, etc.)
    """
    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)

    # Calculate analytics
    total_modules = len(roadmap.modules) if roadmap.modules else 0
    completed_modules = sum(1 for module in (roadmap.modules or []) if module.get('completed', False))

    progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0

    analytics = {
        'roadmap_id': roadmap_id,
        'domain': roadmap.domain,
        'progress_percentage': round(progress_percentage, 2),
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'started_at': roadmap.created_at,
        'last_updated': roadmap.updated_at,
        'estimated_completion': None  # Would calculate based on progress rate
    }

    return Response(analytics)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def duplicate_roadmap(request, roadmap_id):
    """
    Create a copy of an existing roadmap
    """
    original_roadmap = get_object_or_404(Roadmap, id=roadmap_id)

    # Can duplicate own roadmap or public/shared roadmaps
    user = request.user
    if original_roadmap.user != user:
        # Check if roadmap is shared/public (simplified check)
        if not hasattr(original_roadmap, 'is_shared') or not original_roadmap.is_shared:
            return Response({'error': 'Can only duplicate your own or shared roadmaps'},
                           status=status.HTTP_403_FORBIDDEN)

    # Create duplicate
    roadmap_data = RoadmapSerializer(original_roadmap).data
    roadmap_data.pop('id', None)  # Remove ID to create new record
    roadmap_data['domain'] = f"{roadmap_data['domain']} (Copy)"
    roadmap_data['progress'] = 0.0  # Reset progress

    serializer = RoadmapCreateSerializer(data=roadmap_data, context={'request': request})
    if serializer.is_valid():
        duplicate_roadmap = serializer.save(user=user)
        logger.info(f"Roadmap {roadmap_id} duplicated as {duplicate_roadmap.id} by {user.email}")

        return Response({
            'message': 'Roadmap duplicated successfully',
            'new_roadmap_id': duplicate_roadmap.id,
            'domain': duplicate_roadmap.domain
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
