from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ForumPost


@receiver(post_save, sender=ForumPost)
def forum_post_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for ForumPost model post-save events.
    Used for forum post notifications and moderation.
    """
    if created:
        # Forum post creation logic can be added here
        pass