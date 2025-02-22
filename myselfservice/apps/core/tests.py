from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.tests import MockedResponse

class KeycloakAuthenticationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.provider_config = {
            'authorization_endpoint': 'http://keycloak/auth',
            'token_endpoint': 'http://keycloak/token',
            'userinfo_endpoint': 'http://keycloak/userinfo',
        }
        
        self.user_info = {
            'sub': '12345',
            'email': 'testuser1@example.org',
            'preferred_username': 'testuser1',
            'groups': ['eduroam_access']
        }

    @patch('allauth.socialaccount.providers.oauth2.views.OAuth2Adapter.get_provider')
    def test_oidc_login_and_permission(self, mock_adapter):
        mock_adapter.return_value.get_provider_config.return_value = self.provider_config
        
        token_response = {
            'access_token': 'fake_access_token',
            'token_type': 'Bearer',
            'expires_in': 3600,
            'refresh_token': 'fake_refresh_token',
            'id_token': 'fake_id_token'
        }
        
        with patch('allauth.socialaccount.providers.oauth2.views.OAuth2LoginView.dispatch') as mock_login:
            mock_login.return_value = MockedResponse(200, token_response)
            
            with patch('allauth.socialaccount.providers.oauth2.views.OAuth2CallbackView.get_client') as mock_client:
                mock_client.return_value.get_user_info.return_value = self.user_info
                
                response = self.client.get(reverse('oidc_login'))
                self.assertEqual(response.status_code, 302)
                
                response = self.client.get(reverse('oidc_callback'), {'code': 'fake_code', 'state': 'fake_state'})
                self.assertEqual(response.status_code, 302)
                
                user = get_user_model().objects.get(email='testuser1@example.org')
                self.assertTrue(user.is_authenticated)
                self.assertTrue(user.has_perm('eduroam_access'))
                
                social_account = SocialAccount.objects.get(user=user)
                self.assertEqual(social_account.provider, 'keycloak')
                self.assertEqual(social_account.uid, '12345')

    def tearDown(self):
        get_user_model().objects.all().delete()
        SocialAccount.objects.all().delete()