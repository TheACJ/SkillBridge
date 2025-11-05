"""
Celery tasks for notifications app.
"""

from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import Notification
from users.models import User


@shared_task
def cleanup_old_notifications():
    """
    Clean up old notifications that are older than 30 days.
    """
    cutoff_date = timezone.now() - timezone.timedelta(days=30)

    # Delete old read notifications
    old_read_notifications = Notification.objects.filter(
        read=True,
        created_at__lt=cutoff_date
    )

    deleted_count = old_read_notifications.delete()[0]

    # Log the cleanup
    print(f"Cleaned up {deleted_count} old notifications")

    return deleted_count


@shared_task
def send_notification(user_id, notification_type, content, **kwargs):
    """
    Send a notification to a specific user.
    """
    try:
        user = User.objects.get(id=user_id)

        notification = Notification.objects.create(
            user=user,
            type=notification_type,
            content=content,
            **kwargs
        )

        # Here you could add email notifications, push notifications, etc.
        # For now, just create the database record

        return notification.id

    except User.DoesNotExist:
        print(f"User {user_id} not found for notification")
        return None
    except Exception as e:
        print(f"Error sending notification: {str(e)}")
        raise


@shared_task
def send_bulk_notifications(user_ids, notification_type, content, **kwargs):
    """
    Send the same notification to multiple users.
    """
    notifications_created = []

    for user_id in user_ids:
        try:
            user = User.objects.get(id=user_id)

            notification = Notification.objects.create(
                user=user,
                type=notification_type,
                content=content,
                **kwargs
            )

            notifications_created.append(notification.id)

        except User.DoesNotExist:
            print(f"User {user_id} not found for bulk notification")
            continue
        except Exception as e:
            print(f"Error sending bulk notification to user {user_id}: {str(e)}")
            continue

    return notifications_created


@shared_task
def mark_notifications_as_read(user_id, notification_ids=None):
    """
    Mark specific notifications as read for a user.
    If notification_ids is None, mark all unread notifications as read.
    """
    try:
        user = User.objects.get(id=user_id)

        if notification_ids:
            notifications = Notification.objects.filter(
                user=user,
                id__in=notification_ids,
                read=False
            )
        else:
            notifications = Notification.objects.filter(
                user=user,
                read=False
            )

        updated_count = notifications.update(read=True)

        return updated_count

    except User.DoesNotExist:
        print(f"User {user_id} not found for marking notifications as read")
        return 0
    except Exception as e:
        print(f"Error marking notifications as read: {str(e)}")
        raise