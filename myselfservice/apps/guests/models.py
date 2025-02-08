from datetime import timedelta
from django.conf import settings
from django.utils import timezone 
from django.db import models
from apps.core.models import BaseAccountModel
from apps.core.utils import generate_password
from django.contrib.auth import get_user_model

User = get_user_model()

class GuestAccount(BaseAccountModel):

    DURATIONS = {
        3: '3 Tage',
        7: '7 Tage', 
        14: '2 Wochen',
        28: '4 Wochen'
    }
    class Meta:
        permissions = [
            ("sponsoring_access", "Can access guest sponsoring"),
        ]
    name = models.CharField(max_length=510, verbose_name='Name')    
    duration = models.IntegerField(default=7, choices=[(k,v) for k,v in DURATIONS.items()],verbose_name="Zugangsdauer")
    extension_count = models.PositiveIntegerField(default=0)
    message = models.TextField(blank=True, verbose_name='Kommentar')
    username = models.EmailField(verbose_name='E-Mail-Adresse', unique=True, error_messages={'unique': 'Ein Gastzugang mit dieser E-Mail-Adresse existiert bereits.'})

    temp_owner_email = models.EmailField(
        verbose_name='Temporäre Gastgeber Email',
        null=True,
        blank=True
    )
    
    # Owner-Field überschreiben
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='%(class)s_sponsored',
        verbose_name='Gastgeber:in',
        null=True
    )

    def save(self, *args, **kwargs):
        if not self.start_date:
            self.start_date = timezone.now()
        if not self.end_date:
            self.end_date = self.start_date + timedelta(days=self.duration)
        if not self.password:
            self.password=generate_password()

        super().save(*args, **kwargs)

    def activate(self, duration=None):
        """Aktiviert einen Gast-Account aus einer Anfrage oder aus einem selbst erstellten Form"""
        if not GuestAccount.can_owner_more(self.owner):
            raise Exception(f'Sie haben das Limit von {settings.GUEST_SETTINGS['LIMIT_ACTIVE_GUESTS']} aktiven Gästen erreicht.')
            
        self.status = self.Status.ACTIVE
        if duration:
            self.duration = duration
        
        self.save()
        return True

    def create_pending_user(self, temp_owner_email):
        """Erstellt einen neuen pending Gastaccount aus einer Bewerbung"""
        try:
            self.owner = User.objects.get(email=temp_owner_email)
            self.temp_owner_email = None
        except User.DoesNotExist:
            self.owner = None
            self.temp_owner_email = temp_owner_email
            
        self.status = self.Status.PENDING
        self.save()
        
    def extend(self, duration=None):
        """Verlängert einen bestehenden Gast-Account"""
        if self.extension_count >= settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']:
            raise Exception(f'Limit von {settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']} Verlängerungen für den Gast-Account "{self.username}" erreicht')
        
        
        self.extension_count += 1

        if duration:
            self.duration = duration

        self.end_date = self.end_date + timedelta(days=self.duration)
        self.save()
        return True

    def reactivate(self, duration=None):
        """Reaktiviert einen bestehenden Gast-Account"""
        if not GuestAccount.can_owner_more(self.owner):
            raise Exception(f'Sie haben das Gästelimit von {settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']} Gästen erreicht.')
        
        if self.extension_count >= settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']:
            raise Exception(f'Limit von {settings.GUEST_SETTINGS['LIMIT_EXTEND_GUEST']} Verlängerungen für den Gast-Account "{self.username}" erreicht')
        
        self.extension_count += 1
        
        if duration:
            self.duration = duration

        self.end_date = self.end_date + timedelta(days=self.duration)
        self.status = self.Status.ACTIVE
        self.save()
        return True

    @classmethod
    def can_owner_more(cls, owner):
        """Prüft ob Owner weitere Gäste erstellen darf"""
        return cls.objects.filter(
            owner=owner,
            status=cls.Status.ACTIVE,
            end_date__gte=timezone.now()
        ).count() < settings.GUEST_SETTINGS['LIMIT_ACTIVE_GUESTS']