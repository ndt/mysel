import random
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models, connection
from apps.core.models import BaseAccountModel
from .services import LdapService

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mail_login_by_ldap = models.BooleanField(
        default=False,
        verbose_name="Mail Login via LDAP",
        help_text="Aktiviert LDAP Login für Mail"
    )

class EmailDevice(BaseAccountModel):
    comment = models.CharField(max_length=510, blank=True, verbose_name='Kommentar')
    
    class Meta:
        verbose_name = 'Email Account'
        verbose_name_plural = 'Email Accounts'
        permissions = [
            ("emaildevice_access", "Can manage Email accounts"),
        ]

    @classmethod
    def check_account_limit(cls, owner):
        """Prüft ob der Benutzer das Limit erreicht hat"""
        active_accounts = cls.objects.filter(
            owner=owner,
            status=cls.Status.ACTIVE
        ).count()
        return active_accounts < settings.EMAILDEVICE_SETTINGS['MAX_ACCOUNTS']
    
    def save(self, *args, **kwargs):
        """Passwörter werden nicht plaintext gespeichert, sondern bcrypt gehashed.
           Sie können nur einmalig angezeigt werden."""
        if self.password and not self.password.startswith('$2'):
            with connection.cursor() as cursor:
                cursor.execute("SELECT crypt(%s, gen_salt('bf'))", [self.password])
                self.password = cursor.fetchone()[0]

            if settings.EMAILDEVICE_SETTINGS.get('DEACTIVATE_LDAP_LOGIN_AFTER_CREATE'):
                ldap = LdapService()
                if ldap.set_mail_login(self.owner.username, False):
                    profile, created = UserProfile.objects.get_or_create(user=self.owner)
                    profile.mail_login_by_ldap = False
                    profile.save()

        super().save(*args, **kwargs)
    
    @classmethod
    def generate_unique_username(cls, base_username, domain):
        while True:
            suffix = str(random.randint(10, 99))
            test_username = f"{base_username}_{suffix}@{domain}"
            if not cls.objects.filter(username=test_username).exists():
                return test_username