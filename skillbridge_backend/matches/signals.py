from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import MentorMatch
from skillbridge_backend.security import AuditLog


@receiver(post_save, sender=MentorMatch)
def mentor_match_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for MentorMatch model post-save events.
    Used for match creation notifications and audit logging.
    """
    if created:
        AuditLog.log_security_event(
            'MENTOR_MATCH_CREATED',
            instance.learner,
            f'Mentor match created: {instance.learner.email} ↔ {instance.mentor.email}'
        )
        # Match creation logic can be added here
    else:
        AuditLog.log_security_event(
            'MENTOR_MATCH_UPDATED',
            instance.learner,
            f'Mentor match updated: {instance.learner.email} ↔ {instance.mentor.email} (Status: {instance.status})'
        )


@receiver(pre_delete, sender=MentorMatch)
def mentor_match_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for MentorMatch model pre-delete events.
    Used for audit logging before match deletion.
    """
    AuditLog.log_security_event(
        'MENTOR_MATCH_DELETED',
        instance.learner,
        f'Mentor match deleted: {instance.learner.email} ↔ {instance.mentor.email}'
    )