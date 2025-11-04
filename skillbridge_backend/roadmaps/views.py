from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Roadmap
from .serializers import RoadmapSerializer, RoadmapCreateSerializer, RoadmapProgressUpdateSerializer


class RoadmapListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoadmapCreateSerializer
        return RoadmapSerializer

    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RoadmapDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user)


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

        # Generate roadmap using OpenAI
        roadmap_data = openai_integration.generate_roadmap(
            domain=domain,
            skill_level=skill_level,
            time_availability=time_availability,
            user_context=user_context
        )

        serializer = RoadmapCreateSerializer(data=roadmap_data, context={'request': request})
        if serializer.is_valid():
            roadmap = serializer.save()
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
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
