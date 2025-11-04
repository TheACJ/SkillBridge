from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from .models import ForumPost
from .serializers import ForumPostSerializer, ForumPostCreateSerializer, ForumPostListSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ForumPostListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ForumPostCreateSerializer
        return ForumPostListSerializer

    def get_queryset(self):
        queryset = ForumPost.objects.select_related('user')

        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Search functionality
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) | Q(user__email__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ForumPostDetailView(generics.RetrieveAPIView):
    serializer_class = ForumPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ForumPost.objects.select_related('user')


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_forum_replies(request, post_id):
    """
    Get all replies for a specific forum post
    """
    try:
        post = ForumPost.objects.get(id=post_id)
    except ForumPost.DoesNotExist:
        return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    replies = ForumPost.objects.filter(parent=post).select_related('user').order_by('created_at')
    serializer = ForumPostListSerializer(replies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_categories(request):
    """
    Get available forum categories
    """
    categories = ForumPost.objects.values_list('category', flat=True).distinct()
    return Response(list(categories))
