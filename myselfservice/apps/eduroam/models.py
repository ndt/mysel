from django.conf import settings 
from django.db import models
from apps.core.models import BaseAccountModel

class EduroamAccount(BaseAccountModel):
    comment = models.CharField(max_length=510, blank=True, verbose_name='Kommentar')
    realm = models.CharField(max_length=510, default='thga.de', verbose_name='Realm')

    class Meta:
        verbose_name = 'Eduroam Account'
        verbose_name_plural = 'Eduroam Accounts'
        permissions = [
            ("eduroam_access", "Can manage eduroam accounts"),
        ]

    @classmethod
    def check_account_limit(cls, owner):
        """Prüft ob der Benutzer das Limit erreicht hat"""
        active_accounts = cls.objects.filter(
            owner=owner,
            status=cls.Status.ACTIVE
        ).count()
        return active_accounts < settings.EDUROAM_SETTINGS['MAX_ACCOUNTS']