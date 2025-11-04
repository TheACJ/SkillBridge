from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Badge
from .serializers import BadgeSerializer, BadgeCreateSerializer


class BadgeListView(generics.ListAPIView):
    serializer_class = BadgeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'mentor':
            return Badge.objects.filter(mentor=user)
        return Badge.objects.none()  # Learners don't have badges to award


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def award_badge(request):
    """
    Award a badge to a mentor (admin only)
    """
    if request.user.role != 'admin':
        return Response({'error': 'Only admins can award badges'}, status=status.HTTP_403_FORBIDDEN)

    serializer = BadgeCreateSerializer(data=request.data)
    if serializer.is_valid():
        badge = serializer.save()
        return Response(BadgeSerializer(badge).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
