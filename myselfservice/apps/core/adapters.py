from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Permission, User
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        try:
            email = sociallogin.user.email
            if email:
                user = User.objects.filter(email=email).first()
                if user:
                    sociallogin.connect(request, user)
            
            if not sociallogin.user.id:
                sociallogin.user.save()
                    
            extra_data = sociallogin.account.extra_data
            logger.debug(f"Complete Token data: {extra_data}")

            resource_access = extra_data.get('resource_access', {})
            client_access = resource_access.get('django', {})
            client_roles = client_access.get('roles', [])

            logger.debug(f"Found client roles: {client_roles}")
            
            for role_name in client_roles:
                for perm_value in settings.PERMISSION_REQUIRED.values():
                    app_label, codename = perm_value.split('.')
                    
                    if role_name == codename:
                        try:
                            permission = Permission.objects.get(
                                codename=codename,
                                content_type__app_label=app_label
                            )
                            sociallogin.user.user_permissions.add(permission)
                            logger.debug(f"Added permission '{perm_value}' to user {sociallogin.user}")
                        except Permission.DoesNotExist:
                            logger.warning(f"Permission {perm_value} does not exist in database")

        except Exception as e:
            logger.error(f"Error in pre_social_login: {str(e)}", exc_info=True)
                
        return super().pre_social_login(request, sociallogin)