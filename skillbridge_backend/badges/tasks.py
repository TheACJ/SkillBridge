"""
Celery tasks for badges app.
"""

from celery import shared_task
from django.utils import timezone
from django.db.models import Count, Q
from .models import Badge
from users.models import User
from matches.models import MentorMatch
from notifications.tasks import send_notification


@shared_task
def award_achievement_badges():
    """
    Check and award achievement badges based on user activities.
    """
    badges_awarded = []

    # Badge 1: First Steps - Complete first module
    first_steps_users = User.objects.filter(
        ~Q(badges__type='First Steps'),
        roadmaps__modules__icontains='"completed": true'
    ).distinct()

    for user in first_steps_users:
        try:
            Badge.objects.create(
                mentor=user,
                type='First Steps',
                criteria={'first_module_completed': True}
            )

            send_notification.delay(
                user_id=user.id,
                notification_type='badge_awarded',
                content="🎉 Congratulations! You've earned the 'First Steps' badge for completing your first learning module!"
            )

            badges_awarded.append({'user': user.id, 'badge': 'First Steps'})

        except Exception as e:
            print(f"Error awarding First Steps badge to user {user.id}: {str(e)}")
            continue

    # Badge 2: Mentor - Complete first mentorship session
    mentor_users = User.objects.filter(
        ~Q(badges__type='Mentor'),
        mentor_matches__status='completed'
    ).distinct()

    for user in mentor_users:
        try:
            completed_sessions = MentorMatch.objects.filter(
                mentor=user,
                status='completed'
            ).count()

            if completed_sessions >= 1:
                Badge.objects.create(
                    mentor=user,
                    type='Mentor',
                    criteria={'sessions_completed': completed_sessions}
                )

                send_notification.delay(
                    user_id=user.id,
                    notification_type='badge_awarded',
                    content="🏆 Amazing! You've earned the 'Mentor' badge for completing your first mentorship session!"
                )

                badges_awarded.append({'user': user.id, 'badge': 'Mentor'})

        except Exception as e:
            print(f"Error awarding Mentor badge to user {user.id}: {str(e)}")
            continue

    # Badge 3: Dedicated Learner - 30 days of consistent activity
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)

    dedicated_learners = User.objects.filter(
        ~Q(badges__type='Dedicated Learner'),
        progress_logs__timestamp__gte=thirty_days_ago
    ).annotate(
        active_days=Count('progress_logs__timestamp__date', distinct=True)
    ).filter(active_days__gte=20).distinct()

    for user in dedicated_learners:
        try:
            Badge.objects.create(
                mentor=user,
                type='Dedicated Learner',
                criteria={'active_days_in_30': user.active_days}
            )

            send_notification.delay(
                user_id=user.id,
                notification_type='badge_awarded',
                content="🌟 Outstanding! You've earned the 'Dedicated Learner' badge for 20+ days of consistent learning!"
            )

            badges_awarded.append({'user': user.id, 'badge': 'Dedicated Learner'})

        except Exception as e:
            print(f"Error awarding Dedicated Learner badge to user {user.id}: {str(e)}")
            continue

    # Badge 4: Code Contributor - 100+ commits
    code_contributors = User.objects.filter(
        ~Q(badges__type='Code Contributor'),
        progress_logs__event_type='commit'
    ).annotate(
        total_commits=Count('progress_logs')
    ).filter(total_commits__gte=100).distinct()

    for user in code_contributors:
        try:
            Badge.objects.create(
                mentor=user,
                type='Code Contributor',
                criteria={'total_commits': user.total_commits}
            )

            send_notification.delay(
                user_id=user.id,
                notification_type='badge_awarded',
                content="💻 Incredible! You've earned the 'Code Contributor' badge for 100+ code commits!"
            )

            badges_awarded.append({'user': user.id, 'badge': 'Code Contributor'})

        except Exception as e:
            print(f"Error awarding Code Contributor badge to user {user.id}: {str(e)}")
            continue

    # Badge 5: Community Builder - Multiple forum posts
    community_builders = User.objects.filter(
        ~Q(badges__type='Community Builder'),
        forum_posts__isnull=False
    ).annotate(
        total_posts=Count('forum_posts')
    ).filter(total_posts__gte=10).distinct()

    for user in community_builders:
        try:
            Badge.objects.create(
                mentor=user,
                type='Community Builder',
                criteria={'forum_posts': user.total_posts}
            )

            send_notification.delay(
                user_id=user.id,
                notification_type='badge_awarded',
                content="🤝 Fantastic! You've earned the 'Community Builder' badge for being active in our forums!"
            )

            badges_awarded.append({'user': user.id, 'badge': 'Community Builder'})

        except Exception as e:
            print(f"Error awarding Community Builder badge to user {user.id}: {str(e)}")
            continue

    return badges_awarded


@shared_task
def award_mentor_badges():
    """
    Award special badges for exceptional mentoring performance.
    """
    badges_awarded = []

    # Badge: Mentor Extraordinaire - 10+ completed sessions with high ratings
    mentor_extraordinaire = User.objects.filter(
        ~Q(badges__type='Mentor Extraordinaire'),
        mentor_matches__status='completed',
        mentor_matches__rating__gte=4
    ).annotate(
        high_rated_sessions=Count('mentor_matches')
    ).filter(high_rated_sessions__gte=10).distinct()

    for mentor in mentor_extraordinaire:
        try:
            Badge.objects.create(
                mentor=mentor,
                type='Mentor Extraordinaire',
                criteria={'high_rated_sessions': mentor.high_rated_sessions}
            )

            send_notification.delay(
                user_id=mentor.id,
                notification_type='badge_awarded',
                content="⭐ Extraordinary! You've earned the 'Mentor Extraordinaire' badge for 10+ highly-rated mentorship sessions!"
            )

            badges_awarded.append({'user': mentor.id, 'badge': 'Mentor Extraordinaire'})

        except Exception as e:
            print(f"Error awarding Mentor Extraordinaire badge to user {mentor.id}: {str(e)}")
            continue

    # Badge: Knowledge Sharer - Helped 5+ learners complete roadmaps
    knowledge_sharers = User.objects.filter(
        ~Q(badges__type='Knowledge Sharer'),
        mentor_matches__status='completed',
        mentor_matches__learner__roadmaps__progress=100.0
    ).annotate(
        learners_completed=Count('mentor_matches__learner', distinct=True)
    ).filter(learners_completed__gte=5).distinct()

    for mentor in knowledge_sharers:
        try:
            Badge.objects.create(
                mentor=mentor,
                type='Knowledge Sharer',
                criteria={'learners_completed_roadmaps': mentor.learners_completed}
            )

            send_notification.delay(
                user_id=mentor.id,
                notification_type='badge_awarded',
                content="🎓 Brilliant! You've earned the 'Knowledge Sharer' badge for helping 5+ learners complete their roadmaps!"
            )

            badges_awarded.append({'user': mentor.id, 'badge': 'Knowledge Sharer'})

        except Exception as e:
            print(f"Error awarding Knowledge Sharer badge to user {mentor.id}: {str(e)}")
            continue

    return badges_awarded


@shared_task
def check_and_award_badge(user_id, badge_type, criteria):
    """
    Check if a user qualifies for a specific badge and award it if they do.
    """
    try:
        user = User.objects.get(id=user_id)

        # Check if user already has this badge
        if Badge.objects.filter(mentor=user, type=badge_type).exists():
            return None

        # Create the badge
        badge = Badge.objects.create(
            mentor=user,
            type=badge_type,
            criteria=criteria
        )

        # Send notification
        send_notification.delay(
            user_id=user.id,
            notification_type='badge_awarded',
            content=f"🎉 Congratulations! You've earned the '{badge_type}' badge!"
        )

        return badge.id

    except User.DoesNotExist:
        print(f"User {user_id} not found for badge award")
        return None
    except Exception as e:
        print(f"Error awarding badge to user {user_id}: {str(e)}")
        raise


@shared_task
def cleanup_expired_badges():
    """
    Clean up badges that may no longer be relevant (if needed in the future).
    For now, this is a placeholder for potential future badge expiration logic.
    """
    # Currently, badges don't expire, but this could be used for
    # time-limited achievements or streak badges in the future

    return 0