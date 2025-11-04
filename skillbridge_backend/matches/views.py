from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MentorMatch
from .serializers import MentorMatchSerializer, MentorMatchCreateSerializer, MentorMatchUpdateSerializer


class MentorMatchListView(generics.ListAPIView):
    serializer_class = MentorMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return MentorMatch.objects.filter(mentor=user)
        else:
            return MentorMatch.objects.filter(learner=user)


class MentorMatchDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = MentorMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return MentorMatch.objects.filter(mentor=user)
        else:
            return MentorMatch.objects.filter(learner=user)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return MentorMatchUpdateSerializer
        return MentorMatchSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_mentor_match(request):
    """
    Create a mentor match request (calls Rust microservice for matching algorithm)
    """
    learner_needs = request.data.get('learner_needs', {})

    # TODO: Call Rust microservice for mentor matching
    # For now, return mock response
    mock_mentor_id = request.data.get('mentor_id')
    if not mock_mentor_id:
        return Response({'error': 'Mentor ID required for mock matching'}, status=status.HTTP_400_BAD_REQUEST)

    match_data = {'mentor': mock_mentor_id}
    serializer = MentorMatchCreateSerializer(data=match_data, context={'request': request})

    if serializer.is_valid():
        match = serializer.save()
        return Response(MentorMatchSerializer(match).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_match_message(request, match_id):
    """
    Send a message in a mentor match (placeholder for chat functionality)
    """
    match = get_object_or_404(MentorMatch, id=match_id)
    user = request.user

    # Check if user is part of this match
    if user not in [match.learner, match.mentor]:
        return Response({'error': 'Not authorized for this match'}, status=status.HTTP_403_FORBIDDEN)

    message = request.data.get('message')
    if not message:
        return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

    # TODO: Implement chat storage (could be separate ChatMessage model or JSON field)
    # For now, just return success
    return Response({
        'message': 'Message sent successfully',
        'match_id': match_id,
        'sender': user.email,
        'content': message
    })
