from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import ForumPost
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=ForumPost)
def forum_post_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for ForumPost model post-save events.
    Used for forum post notifications, moderation, and audit logging.
    """
    if created:
        AuditLog.log_data_access(
            'create',
            instance.user,
            'ForumPost',
            str(instance.id)
        )
        # Forum post creation logic can be added here
    else:
        AuditLog.log_data_access(
            'update',
            instance.user,
            'ForumPost',
            str(instance.id)
        )


@receiver(pre_delete, sender=ForumPost)
def forum_post_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for ForumPost model pre-delete events.
    Used for audit logging before forum post deletion.
    """
    AuditLog.log_data_access(
        'delete',
        instance.user,
        'ForumPost',
        str(instance.id)
    )