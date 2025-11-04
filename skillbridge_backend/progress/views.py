from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import ProgressLog
from .serializers import ProgressLogSerializer, ProgressLogCreateSerializer
from .integrations import GitHubIntegration


class ProgressLogListView(generics.ListAPIView):
    serializer_class = ProgressLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProgressLog.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def log_progress(request):
    """
    Log progress event (GitHub webhook or manual)
    """
    serializer = ProgressLogCreateSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        progress_log = serializer.save()
        return Response(ProgressLogSerializer(progress_log).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_roadmap_progress(request, roadmap_id):
    """
    Get progress details for a specific roadmap
    """
    from roadmaps.models import Roadmap
    from django.shortcuts import get_object_or_404

    roadmap = get_object_or_404(Roadmap, id=roadmap_id, user=request.user)
    progress_logs = ProgressLog.objects.filter(user=request.user, roadmap=roadmap)

    # Calculate progress metrics
    total_commits = sum(log.details.get('commits', 0) for log in progress_logs if log.event_type == 'commit')
    completed_modules = progress_logs.filter(event_type='module_complete').count()

    return Response({
        'roadmap_id': roadmap_id,
        'total_commits': total_commits,
        'completed_modules': completed_modules,
        'recent_logs': ProgressLogSerializer(progress_logs[:10], many=True).data
    })


@api_view(['POST'])
@method_decorator(csrf_exempt, name='dispatch')
def github_webhook(request):
    """
    Handle GitHub webhooks for progress tracking
    """
    github_integration = GitHubIntegration()

    # Get signature from headers
    signature = request.META.get('HTTP_X_HUB_SIGNATURE_256', '')

    try:
        payload = request.data if hasattr(request, 'data') else {}
        success = github_integration.process_webhook(payload, signature)

        if success:
            return Response({'status': 'processed'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'webhook processing failed'}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        logger.error(f"GitHub webhook error: {str(e)}")
        return Response({'error': 'internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_repositories(request):
    """
    Get user's GitHub repositories
    """
    github_integration = GitHubIntegration()
    repositories = github_integration.get_user_repositories(request.user)

    return Response({'repositories': repositories})
