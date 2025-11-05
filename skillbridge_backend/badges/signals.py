from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Badge


@receiver(post_save, sender=Badge)
def badge_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Badge model post-save events.
    Used for badge awarding notifications and gamification updates.
    """
    if created:
        # Badge awarding logic can be added here
        pass