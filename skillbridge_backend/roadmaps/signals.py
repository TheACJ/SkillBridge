from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Roadmap


@receiver(post_save, sender=Roadmap)
def roadmap_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for Roadmap model post-save events.
    Used for roadmap creation/setup tasks and progress updates.
    """
    if created:
        # Roadmap creation logic can be added here
        pass