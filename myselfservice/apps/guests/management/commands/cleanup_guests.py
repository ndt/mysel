# apps/guests/management/commands/cleanup_guests.py 
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.guests.models import GuestAccount

class Command(BaseCommand):
    help = 'Cleanup expired guest accounts'

    def handle(self, *args, **options):
        expired_guests = GuestAccount.objects.filter(
            end_date__lt=timezone.now() - timezone.timedelta(days=14)
        )
        count = 0
        for guest in expired_guests:
            count += 1
            self.stdout.write(
                f'Setting guest to HARD_DELETED: {guest.username} ({guest.name})'
            )
            guest.hard_delete()
            
        self.stdout.write(f'Cleaned up {count} expired guest accounts')