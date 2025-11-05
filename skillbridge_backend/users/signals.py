from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User


@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for User model post-save events.
    Used for user creation/setup tasks.
    """
    if created:
        # User creation logic can be added here
        pass