# apps/eduroam/management/commands/cleanup_eduroam.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.eduroam.models import EduroamAccount

class Command(BaseCommand):
    help = 'Cleanup deleted eduroam accounts'

    def handle(self, *args, **options):
        # Permanently delete accounts that have been marked as deleted
        # for more than 30 days
        cutoff_date = timezone.now() - timezone.timedelta(days=30)
        deleted_accounts = EduroamAccount.objects.filter(
            status=EduroamAccount.Status.DELETED,
            updated_at__lt=cutoff_date
        )
        
        count = deleted_accounts.count()
        # Hier werden die Accounts wirklich aus der Datenbank gelöscht
        deleted_accounts.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} old accounts')
        )