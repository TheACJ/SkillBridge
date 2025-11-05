"""
Celery tasks for progress tracking app.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Avg
from .models import ProgressLog
from roadmaps.models import Roadmap
from users.models import User
from notifications.tasks import send_notification


@shared_task
def update_roadmap_progress_from_github():
    """
    Update roadmap progress based on recent GitHub activity.
    This task analyzes recent commits and updates roadmap progress accordingly.
    """
    # Get data from the last 7 days
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)

    # Group progress logs by roadmap and count commits
    roadmap_progress = ProgressLog.objects.filter(
        event_type='commit',
        timestamp__gte=seven_days_ago
    ).values('roadmap').annotate(
        commit_count=Count('id')
    ).order_by('-commit_count')

    updated_roadmaps = []

    for progress_data in roadmap_progress:
        try:
            roadmap = Roadmap.objects.get(id=progress_data['roadmap'])
            commit_count = progress_data['commit_count']

            # Calculate progress increase based on commit activity
            # Simple algorithm: 1-5% progress increase based on commit volume
            progress_increase = min(commit_count * 2, 10)  # Max 10% per week

            old_progress = roadmap.progress
            new_progress = min(old_progress + progress_increase, 100.0)

            if new_progress > old_progress:
                roadmap.progress = new_progress
                roadmap.save()

                updated_roadmaps.append({
                    'roadmap_id': roadmap.id,
                    'old_progress': old_progress,
                    'new_progress': new_progress,
                    'commits': commit_count
                })

                # Send notification if significant progress made
                if new_progress - old_progress >= 5:
                    send_notification.delay(
                        user_id=roadmap.user.id,
                        notification_type='progress_update',
                        content=f"Great progress on your {roadmap.domain} roadmap! You've reached {new_progress:.1f}% completion."
                    )

        except Roadmap.DoesNotExist:
            continue
        except Exception as e:
            print(f"Error updating roadmap {progress_data['roadmap']}: {str(e)}")
            continue

    return updated_roadmaps


@shared_task
def generate_weekly_progress_reports():
    """
    Generate weekly progress reports for all active users.
    """
    # Get users with recent activity (last 7 days)
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)

    active_users = User.objects.filter(
        progress_logs__timestamp__gte=seven_days_ago
    ).distinct()

    reports_generated = []

    for user in active_users:
        try:
            # Get user's progress summary
            progress_summary = ProgressLog.objects.filter(
                user=user,
                timestamp__gte=seven_days_ago
            ).aggregate(
                total_commits=Count('id', filter={'event_type': 'commit'}),
                total_modules=Count('id', filter={'event_type': 'module_complete'}),
                avg_commits_per_day=Count('id', filter={'event_type': 'commit'}) / 7.0
            )

            # Get roadmap progress updates
            roadmaps = Roadmap.objects.filter(user=user)
            roadmap_updates = []

            for roadmap in roadmaps:
                recent_progress = ProgressLog.objects.filter(
                    user=user,
                    roadmap=roadmap,
                    timestamp__gte=seven_days_ago
                ).count()

                if recent_progress > 0:
                    roadmap_updates.append({
                        'domain': roadmap.domain,
                        'current_progress': roadmap.progress,
                        'recent_activity': recent_progress
                    })

            # Generate report content
            report_content = f"""
Weekly Progress Report:

📊 Overall Activity:
- Total commits: {progress_summary['total_commits']}
- Modules completed: {progress_summary['total_modules']}
- Average commits/day: {progress_summary['avg_commits_per_day']:.1f}

🎯 Roadmap Updates:
"""

            for update in roadmap_updates:
                report_content += f"- {update['domain']}: {update['current_progress']:.1f}% complete ({update['recent_activity']} activities)\n"

            report_content += "\nKeep up the great work! 🚀"

            # Send the report
            send_notification.delay(
                user_id=user.id,
                notification_type='progress_update',
                content=report_content.strip()
            )

            reports_generated.append({
                'user_id': user.id,
                'commits': progress_summary['total_commits'],
                'modules': progress_summary['total_modules']
            })

        except Exception as e:
            print(f"Error generating report for user {user.id}: {str(e)}")
            continue

    return reports_generated


@shared_task
def cleanup_old_progress_logs():
    """
    Clean up old progress logs (older than 90 days).
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=90)

    old_logs = ProgressLog.objects.filter(timestamp__lt=cutoff_date)

    deleted_count = old_logs.delete()[0]

    print(f"Cleaned up {deleted_count} old progress logs")

    return deleted_count


@shared_task
def analyze_user_progress_patterns(user_id):
    """
    Analyze progress patterns for a specific user and provide insights.
    """
    try:
        user = User.objects.get(id=user_id)

        # Analyze commit patterns over the last 30 days
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

        daily_commits = ProgressLog.objects.filter(
            user=user,
            event_type='commit',
            timestamp__gte=thirty_days_ago
        ).extra(
            select={'day': 'DATE(timestamp)'}
        ).values('day').annotate(
            commit_count=Count('id')
        ).order_by('day')

        # Calculate consistency score (days with commits / total days)
        total_days = 30
        active_days = len([day for day in daily_commits if day['commit_count'] > 0])
        consistency_score = (active_days / total_days) * 100

        # Generate insights
        insights = []

        if consistency_score >= 80:
            insights.append("Excellent consistency! You're coding almost every day.")
        elif consistency_score >= 60:
            insights.append("Good consistency. Try to code a bit more regularly.")
        else:
            insights.append("Consider increasing your coding frequency for better progress.")

        # Analyze peak coding times
        hourly_commits = ProgressLog.objects.filter(
            user=user,
            event_type='commit',
            timestamp__gte=thirty_days_ago
        ).extra(
            select={'hour': 'EXTRACT(hour FROM timestamp)'}
        ).values('hour').annotate(
            commit_count=Count('id')
        ).order_by('-commit_count')

        if hourly_commits:
            peak_hour = hourly_commits[0]['hour']
            insights.append(f"Your most productive coding hour is {peak_hour}:00.")

        # Send insights notification
        insights_content = "📈 Progress Insights:\n\n" + "\n".join(f"• {insight}" for insight in insights)

        send_notification.delay(
            user_id=user.id,
            notification_type='progress_update',
            content=insights_content
        )

        return {
            'user_id': user_id,
            'consistency_score': consistency_score,
            'insights_count': len(insights)
        }

    except User.DoesNotExist:
        print(f"User {user_id} not found for progress analysis")
        return None
    except Exception as e:
        print(f"Error analyzing progress for user {user_id}: {str(e)}")
        raise