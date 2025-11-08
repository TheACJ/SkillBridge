from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Notification
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=Notification)
def notification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Notification model post-save events.
    Used for notification delivery, user alerts, and audit logging.
    """
    if created:
        AuditLog.log_data_access(
            'create',
            instance.user,
            'Notification',
            str(instance.id)
        )
        # Notification creation logic can be added here
    else:
        AuditLog.log_data_access(
            'update',
            instance.user,
            'Notification',
            str(instance.id)
        )


@receiver(pre_delete, sender=Notification)
def notification_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for Notification model pre-delete events.
    Used for audit logging before notification deletion.
    """
    AuditLog.log_data_access(
        'delete',
        instance.user,
        'Notification',
        str(instance.id)
    )