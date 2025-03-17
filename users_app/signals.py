from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Erstellt automatisch ein UserProfile, wenn ein neuer User angelegt wird."""
    if created and not hasattr(instance, '_profile_created'):
        # Verhindert rekursive Aufrufe
        instance._profile_created = True
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Speichert das UserProfile automatisch, wenn der User gespeichert wird."""
    if hasattr(instance, '_profile_created'):
        instance.userprofile.save()
        del instance._profile_created
