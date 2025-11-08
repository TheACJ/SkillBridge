from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Badge
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=Badge)
def badge_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Badge model post-save events.
    Used for badge awarding notifications and audit logging.
    """
    if created:
        AuditLog.log_security_event(
            'BADGE_AWARDED',
            instance.mentor,
            f'Badge "{instance.type}" awarded to mentor {instance.mentor.email}'
        )
        # Badge awarding logic can be added here
    else:
        AuditLog.log_security_event(
            'BADGE_UPDATED',
            instance.mentor,
            f'Badge "{instance.type}" updated for mentor {instance.mentor.email}'
        )


@receiver(pre_delete, sender=Badge)
def badge_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for Badge model pre-delete events.
    Used for audit logging before badge deletion.
    """
    AuditLog.log_security_event(
        'BADGE_REVOKED',
        instance.mentor,
        f'Badge "{instance.type}" revoked from mentor {instance.mentor.email}'
    )