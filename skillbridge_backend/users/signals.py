from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import User
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for User model post-save events.
    Used for user creation/setup tasks and audit logging.
    """
    if created:
        AuditLog.log_security_event(
            'USER_CREATED',
            instance,
            f'New user account created: {instance.email}'
        )
        # User creation logic can be added here
    else:
        AuditLog.log_security_event(
            'USER_UPDATED',
            instance,
            f'User profile updated: {instance.email}'
        )


@receiver(pre_delete, sender=User)
def user_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for User model pre-delete events.
    Used for audit logging before user deletion.
    """
    AuditLog.log_security_event(
        'USER_DELETED',
        instance,
        f'User account deleted: {instance.email}'
    )