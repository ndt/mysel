# Register your models here.
from django.contrib import admin

from apps.core.admin import BaseAccountAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages

from .models import EmailDevice,User
from .services import LdapService
from django.contrib.auth.models import User
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False

@admin.register(EmailDevice)
class EmailAdmin(BaseAccountAdmin):
    list_display = ('username', 'comment', 'owner', 'updated_at', 'status')
    search_fields = ('username', 'owner')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)

    def mail_login_by_ldap(self, obj):
        try:
            return obj.userprofile.mail_login_by_ldap
        except UserProfile.DoesNotExist:
            return False
    mail_login_by_ldap.boolean = True

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            try:
                ldap = LdapService()
                ldap_value = ldap.get_mail_login(obj.username)
                
                if hasattr(obj, 'userprofile'):
                    obj.userprofile.mail_login_by_ldap = ldap_value
                    obj.userprofile.save()
                else:
                    profile = UserProfile.objects.create(user=obj, mail_login_by_ldap=ldap_value)
            except Exception as e:
                messages.error(request, f'LDAP Fehler: {str(e)}')
        return super().get_form(request, obj, **kwargs)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, UserProfile) and formset.has_changed():
                ldap = LdapService()
                if ldap.set_mail_login(instance.user.username, instance.mail_login_by_ldap):
                    instance.save()
                else:
                    messages.error(request, 'LDAP Update fehlgeschlagen')
        formset.save_m2m()

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)