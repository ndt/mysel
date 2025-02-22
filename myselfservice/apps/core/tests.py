from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount
from allauth.account.models import EmailAddress

class KeycloakAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.app_id = 'keycloak'
        self.test_username = 'testuser1@example.org'
        self.test_password = 'testuser1'
        
    def test_oidc_login_and_permission(self):
        """Test real OIDC login flow with Keycloak"""
        
        # Start des Login-Flows
        login_url = reverse('openid_connect_login', kwargs={'provider_id': self.app_id})
        response = self.client.get(login_url)
        self.assertEqual(response.status_code, 302)
        
        # Die Redirect-URL sollte zur Keycloak-Login-Seite führen
        keycloak_login_url = response['Location']
        self.assertIn('keycloak:8080', keycloak_login_url)
        
        # Simuliere Login bei Keycloak durch direktes POSTen der Credentials
        # (Dies erfordert, dass die Test-Keycloak-Instanz läuft und der User existiert)
        response = self.client.post(keycloak_login_url, {
            'username': self.test_username,
            'password': self.test_password
        }, follow=True)
        
        # Nach erfolgreichem Login sollte der User in Django existieren
        user = get_user_model().objects.get(username=self.test_username)
        self.assertTrue(user.is_active)
        self.assertTrue(user.has_perm('eduroam_access'))
        
        # Überprüfe den Social Account
        social_account = SocialAccount.objects.get(user=user)
        self.assertEqual(social_account.provider, 'openid_connect')
        
        # Überprüfe ob der User eingeloggt ist
        self.assertTrue(user.is_authenticated)

    def tearDown(self):
        get_user_model().objects.all().delete()
        SocialAccount.objects.all().delete()
        EmailAddress.objects.all().delete()