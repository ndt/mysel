from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import EduroamAccount

@receiver(pre_save, sender=EduroamAccount)
def create_username(sender, instance, **kwargs):
    """Generiert automatisch einen Benutzernamen wenn keiner gesetzt ist"""
    if not instance.username:
        # Format: eduXXXX@realm
        while True:
            number = get_random_string(5, '0123456789')
            username = f'edu{number}@{instance.realm}'
            if not EduroamAccount.objects.filter(username=username).exists():
                instance.username = username
                break