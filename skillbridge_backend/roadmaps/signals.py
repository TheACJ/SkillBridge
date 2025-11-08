from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Roadmap
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=Roadmap)
def roadmap_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Roadmap model post-save events.
    Used for roadmap creation/setup tasks and audit logging.
    """
    if created:
        AuditLog.log_security_event(
            'ROADMAP_CREATED',
            instance.user,
            f'New roadmap created: {instance.domain} ({instance.user.email})'
        )
        # Roadmap creation logic can be added here
    else:
        AuditLog.log_security_event(
            'ROADMAP_UPDATED',
            instance.user,
            f'Roadmap updated: {instance.domain} ({instance.user.email})'
        )


@receiver(pre_delete, sender=Roadmap)
def roadmap_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for Roadmap model pre-delete events.
    Used for audit logging before roadmap deletion.
    """
    AuditLog.log_security_event(
        'ROADMAP_DELETED',
        instance.user,
        f'Roadmap deleted: {instance.domain} ({instance.user.email})'
    )