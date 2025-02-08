# apps/core/models.py
from django.conf import settings
from django.db import models
from django.utils import timezone 
from .utils import logger
class AccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(status=BaseAccountModel.Status.HARD_DELETED)

class AdminAccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()
    
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseAccountModel(BaseModel):
    objects = AccountManager()
    all_objects = AdminAccountManager()

    class Status:
        PENDING = 0
        ACTIVE = 1
        BANNED = 2
        DELETED = -1
        HARD_DELETED = -2 # Nur intern sichtbar

    STATUS_CHOICES = [
        (Status.PENDING, 'Unbestätigt'),
        (Status.ACTIVE, 'Aktiv'),
        (Status.BANNED, 'Gebannt'),
        (Status.DELETED, 'Gelöscht'),
        (Status.HARD_DELETED, 'Endgültig gelöscht'),
    ]

    username = models.EmailField(verbose_name='E-Mail Adresse', unique=True)
    password = models.CharField(max_length=510, verbose_name='Passwort')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_sponsored', verbose_name='Gastgeber:in')
    status = models.IntegerField(choices=STATUS_CHOICES,default=Status.ACTIVE,verbose_name='Status')
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='Startdatum')
    end_date = models.DateTimeField(null=True,blank=True, verbose_name='Enddatum')

    class Meta:
        abstract = True

    @property
    def is_pending(self):
        return self.status == self.Status.PENDING

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_banned(self):
        return self.status == self.Status.BANNED

    @property
    def is_deleted(self):
        return self.status == self.Status.DELETED

    @property
    def is_expired(self):
        return self.end_date and self.end_date < timezone.now()
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            logger.info(f"New account created: {self.__class__.__name__} - {self.username}")
        else:
            logger.info(f"Account updated: {self.__class__.__name__} - {self.username}")

    def ban(self):
        logger.info(f"Account marked as banned: {self.__class__.__name__} - {self.username}")
        self.status = self.Status.BANNED
        self.save()

    def delete(self):
        logger.info(f"Account marked as deleted: {self.__class__.__name__} - {self.username}")
        self.status = self.Status.DELETED
        self.save()

    def hard_delete(self):
        logger.info(f"Account hard deleted: {self.__class__.__name__} - {self.username}")
        self.username = f"deleted_{self.id}_{self.username}"
        self.status = self.Status.HARD_DELETED
        self.save()
