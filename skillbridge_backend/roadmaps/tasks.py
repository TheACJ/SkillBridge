"""
Celery tasks for roadmaps app.
"""

from celery import shared_task
from django.utils import timezone
from .models import Roadmap
from users.models import User
from notifications.tasks import send_notification


@shared_task
def generate_roadmap_ai(user_id, domain, skill_level='beginner', time_availability='part-time'):
    """
    Generate a personalized roadmap using AI integration.
    This is an async version of the roadmap generation.
    """
    try:
        from .integrations import OpenAIIntegration

        user = User.objects.get(id=user_id)

        # Initialize OpenAI integration
        openai_integration = OpenAIIntegration()

        # Get user context for personalization
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

        # Create the roadmap
        roadmap = Roadmap.objects.create(
            user=user,
            domain=domain,
            modules=roadmap_data.get('modules', []),
            progress=roadmap_data.get('progress', 0)
        )

        # Send success notification
        send_notification.delay(
            user_id=user.id,
            notification_type='progress_update',
            content=f"🎉 Your personalized {domain} roadmap has been generated! Start your learning journey today."
        )

        return roadmap.id

    except User.DoesNotExist:
        print(f"User {user_id} not found for roadmap generation")
        return None
    except Exception as e:
        print(f"Error generating roadmap for user {user_id}: {str(e)}")

        # Send error notification
        try:
            send_notification.delay(
                user_id=user_id,
                notification_type='progress_update',
                content="❌ Sorry, we encountered an error generating your roadmap. Please try again or contact support."
            )
        except:
            pass

        raise


@shared_task
def update_roadmap_progress(roadmap_id):
    """
    Update progress for a specific roadmap based on completed modules.
    """
    try:
        roadmap = Roadmap.objects.get(id=roadmap_id)

        modules = roadmap.modules or []
        if not modules:
            return roadmap.progress

        completed_modules = sum(1 for module in modules if module.get('completed', False))
        total_modules = len(modules)

        if total_modules > 0:
            new_progress = (completed_modules / total_modules) * 100
            old_progress = roadmap.progress

            if abs(new_progress - old_progress) > 1:  # Only update if significant change
                roadmap.progress = round(new_progress, 2)
                roadmap.save()

                # Send progress notification if significant improvement
                if new_progress > old_progress and new_progress - old_progress >= 10:
                    send_notification.delay(
                        user_id=roadmap.user.id,
                        notification_type='progress_update',
                        content=f"🚀 Great progress on your {roadmap.domain} roadmap! You've reached {roadmap.progress:.1f}% completion."
                    )

                return roadmap.progress

        return roadmap.progress

    except Roadmap.DoesNotExist:
        print(f"Roadmap {roadmap_id} not found for progress update")
        return None
    except Exception as e:
        print(f"Error updating progress for roadmap {roadmap_id}: {str(e)}")
        raise


@shared_task
def check_roadmap_completion():
    """
    Check for roadmaps that have reached 100% completion and celebrate achievements.
    """
    completed_roadmaps = Roadmap.objects.filter(
        progress=100.0,
        user__notifications__type='progress_update',
        user__notifications__content__icontains='completed'
    ).exclude(
        user__notifications__content__icontains='100%'
    ).select_related('user')

    celebrations_sent = []

    for roadmap in completed_roadmaps:
        try:
            # Send completion celebration
            send_notification.delay(
                user_id=roadmap.user.id,
                notification_type='progress_update',
                content=f"🎊 CONGRATULATIONS! You've completed your {roadmap.domain} roadmap! 🎉\n\nYou're now ready to take on new challenges. Consider mentoring others or exploring advanced topics in {roadmap.domain}."
            )

            celebrations_sent.append({
                'user_id': roadmap.user.id,
                'roadmap_domain': roadmap.domain
            })

        except Exception as e:
            print(f"Error sending completion celebration for roadmap {roadmap.id}: {str(e)}")
            continue

    return celebrations_sent


@shared_task
def generate_roadmap_insights(user_id):
    """
    Generate insights about a user's roadmap progress and learning patterns.
    """
    try:
        user = User.objects.get(id=user_id)

        # Get all user's roadmaps
        roadmaps = Roadmap.objects.filter(user=user)

        if not roadmaps.exists():
            return None

        insights = {
            'total_roadmaps': roadmaps.count(),
            'completed_roadmaps': roadmaps.filter(progress=100.0).count(),
            'in_progress_roadmaps': roadmaps.filter(progress__gt=0, progress__lt=100.0).count(),
            'average_progress': roadmaps.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0,
            'most_advanced_domain': None,
            'learning_streak': 0  # Could be calculated from progress logs
        }

        # Find most advanced domain
        highest_progress_roadmap = roadmaps.order_by('-progress').first()
        if highest_progress_roadmap:
            insights['most_advanced_domain'] = {
                'domain': highest_progress_roadmap.domain,
                'progress': highest_progress_roadmap.progress
            }

        # Generate personalized insights message
        message = f"📊 Your Learning Insights:\n\n"
        message += f"• Total roadmaps: {insights['total_roadmaps']}\n"
        message += f"• Completed: {insights['completed_roadmaps']}\n"
        message += f"• Average progress: {insights['average_progress']:.1f}%\n"

        if insights['most_advanced_domain']:
            message += f"• Most advanced: {insights['most_advanced_domain']['domain']} ({insights['most_advanced_domain']['progress']:.1f}%)\n"

        if insights['completed_roadmaps'] > 0:
            message += f"\n🎉 Keep up the excellent work!"

        # Send insights notification
        send_notification.delay(
            user_id=user.id,
            notification_type='progress_update',
            content=message
        )

        return insights

    except User.DoesNotExist:
        print(f"User {user_id} not found for insights generation")
        return None
    except Exception as e:
        print(f"Error generating insights for user {user_id}: {str(e)}")
        raise


@shared_task
def cleanup_inactive_roadmaps():
    """
    Clean up or archive roadmaps that haven't been touched in a long time.
    """
    six_months_ago = timezone.now() - timezone.timedelta(days=180)

    # Find roadmaps not updated in 6 months and with low progress
    inactive_roadmaps = Roadmap.objects.filter(
        updated_at__lt=six_months_ago,
        progress__lt=10.0
    )

    # For now, just count them. In the future, could archive or notify users
    inactive_count = inactive_roadmaps.count()

    print(f"Found {inactive_count} inactive roadmaps")

    return inactive_count