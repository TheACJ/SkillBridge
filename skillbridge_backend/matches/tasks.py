"""
Celery tasks for matches app.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Q
from .models import MentorMatch
from users.models import User
from notifications.tasks import send_notification


@shared_task
def send_session_reminders():
    """
    Send reminders for upcoming mentorship sessions.
    """
    # Get sessions happening in the next 24 hours
    tomorrow = timezone.now() + timezone.timedelta(hours=24)

    upcoming_sessions = MentorMatch.objects.filter(
        status='active',
        session_schedule__isnull=False
    ).exclude(session_schedule=[])

    reminders_sent = []

    for match in upcoming_sessions:
        try:
            # Parse session schedule (assuming it's a list of dicts with 'time' field)
            import json
            schedule = match.session_schedule

            if isinstance(schedule, str):
                schedule = json.loads(schedule)

            for session in schedule:
                if isinstance(session, dict) and 'time' in session:
                    session_time_str = session['time']
                    # Assuming time is stored as ISO string
                    from datetime import datetime
                    session_time = datetime.fromisoformat(session_time_str.replace('Z', '+00:00'))

                    # Convert to timezone-aware if needed
                    if timezone.is_naive(session_time):
                        session_time = timezone.make_aware(session_time)

                    # Check if session is within 24 hours
                    time_diff = session_time - timezone.now()

                    if timezone.timedelta(hours=1) <= time_diff <= timezone.timedelta(hours=24):
                        # Send reminder to both learner and mentor
                        topic = session.get('topic', 'mentorship session')

                        # Reminder for learner
                        send_notification.delay(
                            user_id=match.learner.id,
                            notification_type='session_reminder',
                            content=f"⏰ Reminder: You have a mentorship session on {session_time.strftime('%B %d at %I:%M %p')} about '{topic}' with {match.mentor.email}."
                        )

                        # Reminder for mentor
                        send_notification.delay(
                            user_id=match.mentor.id,
                            notification_type='session_reminder',
                            content=f"⏰ Reminder: You have a mentorship session on {session_time.strftime('%B %d at %I:%M %p')} about '{topic}' with {match.learner.email}."
                        )

                        reminders_sent.append({
                            'match_id': match.id,
                            'session_time': session_time_str,
                            'topic': topic
                        })

        except Exception as e:
            print(f"Error processing reminders for match {match.id}: {str(e)}")
            continue

    return reminders_sent


@shared_task
def check_expired_matches():
    """
    Check for matches that may need status updates or follow-ups.
    """
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

    # Find old pending matches
    old_pending_matches = MentorMatch.objects.filter(
        status='pending',
        created_at__lt=thirty_days_ago
    )

    expired_count = 0

    for match in old_pending_matches:
        try:
            # Send follow-up notification to both parties
            send_notification.delay(
                user_id=match.learner.id,
                notification_type='match',
                content=f"Your mentorship request to {match.mentor.email} is still pending. Consider following up or exploring other mentors."
            )

            send_notification.delay(
                user_id=match.mentor.id,
                notification_type='match',
                content=f"You have a pending mentorship request from {match.learner.email} that's over 30 days old. Please review and respond."
            )

            expired_count += 1

        except Exception as e:
            print(f"Error processing expired match {match.id}: {str(e)}")
            continue

    return expired_count


@shared_task
def send_match_feedback_requests():
    """
    Send feedback requests for recently completed matches.
    """
    seven_days_ago = timezone.now() - timezone.timedelta(days=7)

    # Find matches completed in the last week that don't have ratings yet
    completed_matches = MentorMatch.objects.filter(
        status='completed',
        created_at__gte=seven_days_ago,
        rating__isnull=True
    )

    feedback_requests_sent = []

    for match in completed_matches:
        try:
            # Send feedback request to learner
            send_notification.delay(
                user_id=match.learner.id,
                notification_type='match',
                content=f"How was your experience with {match.mentor.email}? Please rate your mentorship session and leave feedback!"
            )

            feedback_requests_sent.append(match.id)

        except Exception as e:
            print(f"Error sending feedback request for match {match.id}: {str(e)}")
            continue

    return feedback_requests_sent


@shared_task
def update_match_statuses():
    """
    Update match statuses based on time and activity.
    """
    sixty_days_ago = timezone.now() - timezone.timedelta(days=60)

    # Auto-complete old active matches (assuming they're finished)
    old_active_matches = MentorMatch.objects.filter(
        status='active',
        created_at__lt=sixty_days_ago
    )

    completed_count = old_active_matches.update(status='completed')

    if completed_count > 0:
        print(f"Auto-completed {completed_count} old active matches")

    return completed_count


@shared_task
def generate_match_analytics():
    """
    Generate analytics about mentorship matching performance.
    """
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

    # Calculate match success rates
    total_matches = MentorMatch.objects.filter(created_at__gte=thirty_days_ago).count()
    completed_matches = MentorMatch.objects.filter(
        created_at__gte=thirty_days_ago,
        status='completed'
    ).count()
    rejected_matches = MentorMatch.objects.filter(
        created_at__gte=thirty_days_ago,
        status='rejected'
    ).count()

    success_rate = (completed_matches / total_matches * 100) if total_matches > 0 else 0

    # Average rating for completed matches
    avg_rating = MentorMatch.objects.filter(
        status='completed',
        rating__isnull=False
    ).aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    analytics = {
        'period_days': 30,
        'total_matches': total_matches,
        'completed_matches': completed_matches,
        'rejected_matches': rejected_matches,
        'success_rate': round(success_rate, 2),
        'average_rating': round(avg_rating, 2) if avg_rating else None
    }

    print(f"Match Analytics: {analytics}")

    return analytics


@shared_task
def cleanup_old_match_data():
    """
    Clean up old match-related data that's no longer needed.
    """
    # For now, we keep all match data, but this could be used for
    # archiving old matches or cleaning up temporary data

    return 0