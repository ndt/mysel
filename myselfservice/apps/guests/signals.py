from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import GuestAccount

@receiver(post_save, sender=get_user_model())
def assign_pending_guests(sender, instance, **kwargs):
    GuestAccount.objects.filter(
        temp_owner_email=instance.email,
        owner__isnull=True
    ).update(
        owner=instance,
        temp_owner_email=None
    )