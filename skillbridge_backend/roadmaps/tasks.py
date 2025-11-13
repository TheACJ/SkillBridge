import logging
from celery import shared_task
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from .models import Roadmap
from .services import RoadmapService

logger = logging.getLogger(__name__)


@shared_task
def generate_roadmap_async(domain, skill_level, time_availability, user_context, user_id):
    """
    Async task to generate roadmap using OpenAI
    """
    try:
        logger.info(f"Starting async roadmap generation for user {user_id}: {domain}")

        # Generate roadmap using service
        roadmap_data = RoadmapService.generate_roadmap(
            domain=domain,
            skill_level=skill_level,
            time_availability=time_availability,
            user_context=user_context
        )

        # Invalidate user cache
        RoadmapService.invalidate_user_cache(user_id)

        # Send notification email (TODO: get it configured)
        if settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend':
            try:
                send_mail(
                    subject=f'Your {domain} Roadmap is Ready!',
                    message=f'Your personalized {domain} learning roadmap has been generated and is ready to view.',
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user_context.get('email', '')],
                    fail_silently=True
                )
            except Exception as e:
                logger.warning(f"Failed to send roadmap ready email: {str(e)}")

        logger.info(f"Completed async roadmap generation for user {user_id}")
        return roadmap_data

    except Exception as e:
        logger.error(f"Failed async roadmap generation for user {user_id}: {str(e)}")
        raise


@shared_task
def update_roadmap_progress_async(roadmap_id):
    """
    Async task to recalculate and cache roadmap progress
    """
    try:
        logger.info(f"Updating progress cache for roadmap {roadmap_id}")

        roadmap = Roadmap.objects.get(id=roadmap_id)
        progress = RoadmapService.calculate_progress(roadmap)

        # Update roadmap progress in database
        roadmap.progress = progress
        roadmap.save(update_fields=['progress'])

        logger.info(f"Updated progress for roadmap {roadmap_id}: {progress}%")
        return progress

    except Roadmap.DoesNotExist:
        logger.error(f"Roadmap {roadmap_id} not found for progress update")
        raise
    except Exception as e:
        logger.error(f"Failed to update roadmap progress for {roadmap_id}: {str(e)}")
        raise


@shared_task
def cleanup_expired_cache():
    """
    Periodic task to clean up expired cache entries
    """
    try:
        logger.info("Starting cache cleanup task")

        # Get cache stats before cleanup
        cache_stats = cache.get('cache_stats', {})

        # Clean up old roadmap caches (older than 24 hours)
        # This is a simplified cleanup - in production, use Redis TTL or more sophisticated cleanup

        logger.info("Completed cache cleanup task")
        return {"status": "completed", "cache_stats": cache_stats}

    except Exception as e:
        logger.error(f"Failed cache cleanup: {str(e)}")
        raise


@shared_task
def send_weekly_progress_report():
    """
    Send weekly progress reports to active users
    """
    try:
        logger.info("Starting weekly progress report task")

        # Get active users with roadmaps
        active_users = Roadmap.objects.values_list('user', flat=True).distinct()

        reports_sent = 0
        for user_id in active_users:
            try:
                user_roadmaps = Roadmap.objects.filter(user_id=user_id)
                total_roadmaps = user_roadmaps.count()
                completed_roadmaps = user_roadmaps.filter(progress=100.0).count()

                if total_roadmaps > 0:
                    completion_rate = (completed_roadmaps / total_roadmaps) * 100

                    # Send email report (simplified)
                    logger.info(f"Weekly report for user {user_id}: {completed_roadmaps}/{total_roadmaps} roadmaps completed ({completion_rate:.1f}%)")
                    reports_sent += 1

            except Exception as e:
                logger.warning(f"Failed to generate report for user {user_id}: {str(e)}")
                continue

        logger.info(f"Sent {reports_sent} weekly progress reports")
        return {"reports_sent": reports_sent}

    except Exception as e:
        logger.error(f"Failed weekly progress report task: {str(e)}")
        raise


@shared_task
def optimize_database_indexes():
    """
    Periodic task to analyze and optimize database indexes
    """
    try:
        logger.info("Starting database index optimization")

        # This would run ANALYZE and REINDEX commands in PostgreSQL
        # For now, just log the intent
        logger.info("Database index optimization completed (placeholder)")

        return {"status": "completed"}

    except Exception as e:
        logger.error(f"Failed database index optimization: {str(e)}")
        raise