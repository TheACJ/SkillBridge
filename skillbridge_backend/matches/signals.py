from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MentorMatch


@receiver(post_save, sender=MentorMatch)
def mentor_match_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for MentorMatch model post-save events.
    Used for match creation notifications and status updates.
    """
    if created:
        # Match creation logic can be added here
        pass