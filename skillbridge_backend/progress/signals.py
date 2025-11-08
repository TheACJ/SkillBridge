from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import ProgressLog
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=ProgressLog)
def progress_log_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for ProgressLog model post-save events.
    Used for progress updates, audit logging, and roadmap recalculations.
    """
    if created:
        AuditLog.log_data_access(
            'create',
            instance.user,
            'ProgressLog',
            str(instance.id)
        )
        # Progress logging logic can be added here
    else:
        AuditLog.log_data_access(
            'update',
            instance.user,
            'ProgressLog',
            str(instance.id)
        )


@receiver(pre_delete, sender=ProgressLog)
def progress_log_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for ProgressLog model pre-delete events.
    Used for audit logging before progress log deletion.
    """
    AuditLog.log_data_access(
        'delete',
        instance.user,
        'ProgressLog',
        str(instance.id)
    )