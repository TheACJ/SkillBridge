from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification


@receiver(post_save, sender=Notification)
def notification_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Notification model post-save events.
    Used for notification delivery and user alerts.
    """
    if created:
        # Notification creation logic can be added here
        pass