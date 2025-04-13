from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Creates a UserProfile instance for a User instance when it is saved and
    created for the first time. The UserProfile instance is created with the
    User instance as its user foreign key.

    Args:
        sender (User): The User model class that sent the post_save signal.
        instance (User): The actual User instance that was saved.
        created (bool): A boolean indicating whether the User instance was
            created or updated.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if created and not hasattr(instance, '_profile_created'):
        instance._profile_created = True
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Saves the UserProfile instance associated with a User instance when it is
    saved and has a _profile_created attribute. This is used to save the
    UserProfile when it is created and the User instance is saved for the
    first time.

    Args:
        sender (User): The User model class that sent the post_save signal.
        instance (User): The actual User instance that was saved.
        **kwargs: Additional keyword arguments.

    Returns:
        None
    """
    if hasattr(instance, '_profile_created'):
        instance.userprofile.save()
        del instance._profile_created
