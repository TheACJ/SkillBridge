from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ProgressLog


@receiver(post_save, sender=ProgressLog)
def progress_log_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for ProgressLog model post-save events.
    Used for progress updates and roadmap recalculations.
    """
    if created:
        # Progress logging logic can be added here
        pass