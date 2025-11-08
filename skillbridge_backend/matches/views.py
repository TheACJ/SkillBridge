import logging
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
            return MentorMatch.objects.filter(mentor=user).select_related('learner')
        else:
            return MentorMatch.objects.filter(learner=user).select_related('mentor')


class MentorMatchDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = MentorMatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return MentorMatch.objects.filter(mentor=user).select_related('learner')
        else:
            return MentorMatch.objects.filter(learner=user).select_related('mentor')

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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def rate_mentor(request, match_id):
    """
    Rate a mentor after completing a match
    """
    match = get_object_or_404(MentorMatch, id=match_id)
    user = request.user

    # Only learners can rate mentors
    if user != match.learner:
        return Response({'error': 'Only learners can rate mentors'}, status=status.HTTP_403_FORBIDDEN)

    # Only allow rating completed matches
    if match.status != 'completed':
        return Response({'error': 'Can only rate completed matches'}, status=status.HTTP_400_BAD_REQUEST)

    rating = request.data.get('rating')
    review = request.data.get('review', '')

    if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
        return Response({'error': 'Rating must be an integer between 1 and 5'}, 
                       status=status.HTTP_400_BAD_REQUEST)

    # Update mentor's profile rating
    mentor_profile = match.mentor.profile or {}
    current_rating = mentor_profile.get('rating', 0.0)
    total_ratings = mentor_profile.get('total_ratings', 0)

    # Calculate new average rating
    new_total_ratings = total_ratings + 1
    new_average = ((current_rating * total_ratings) + rating) / new_total_ratings

    mentor_profile['rating'] = round(new_average, 2)
    mentor_profile['total_ratings'] = new_total_ratings

    match.mentor.profile = mentor_profile
    match.mentor.save()

    # Update match with rating
    match.rating = rating
    match.session_schedule = review  # Store review in session_schedule field
    match.save()

    return Response({
        'message': 'Mentor rated successfully',
        'rating': rating,
        'new_average_rating': new_average,
        'total_ratings': new_total_ratings
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_mentor_reviews(request, mentor_id):
    """
    Get all reviews for a mentor
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        mentor = User.objects.get(id=mentor_id, role='mentor')
    except User.DoesNotExist:
        return Response({'error': 'Mentor not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get completed matches with ratings
    reviewed_matches = MentorMatch.objects.filter(
        mentor=mentor,
        status='completed',
        rating__isnull=False
    ).select_related('learner').only('id', 'rating', 'session_schedule', 'created_at', 'learner__email')

    reviews = []
    for match in reviewed_matches:
        reviews.append({
            'match_id': match.id,
            'rating': match.rating,
            'review': match.session_schedule,  # Review stored here
            'learner_name': match.learner.email,
            'completed_at': match.created_at,
        })

    # Calculate statistics
    if reviews:
        ratings = [r['rating'] for r in reviews]
        average_rating = sum(ratings) / len(ratings)
    else:
        average_rating = 0.0

    return Response({
        'mentor_id': mentor_id,
        'average_rating': round(average_rating, 2),
        'total_reviews': len(reviews),
        'reviews': reviews
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_match_history(request):
    """
    Get user's complete match history
    """
    user = request.user
    
    if user.role == 'mentor':
        matches = MentorMatch.objects.filter(mentor=user).select_related('learner').order_by('-created_at')
    else:
        matches = MentorMatch.objects.filter(learner=user).select_related('mentor').order_by('-created_at')
    
    serializer = MentorMatchSerializer(matches, many=True)
    
    return Response({
        'matches': serializer.data,
        'total_matches': matches.count(),
        'role': user.role
    })
