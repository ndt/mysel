from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import EduroamAccount
from django.conf import settings

User = get_user_model()

class EduroamTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import Permission
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        perm = Permission.objects.get(codename='eduroam_access')
        self.user.user_permissions.add(perm)
        self.client.login(username='testuser', password='testpass123')

    def test_eduroam_list_view(self):
        response = self.client.get(reverse('eduroam:list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'eduroam/eduroam_list.html')

    def test_eduroam_account_creation(self):
        response = self.client.post(reverse('eduroam:create'), {
            'comment': 'Test Device'
        })
        self.assertEqual(EduroamAccount.objects.count(), 1)
        account = EduroamAccount.objects.first()
        self.assertEqual(account.owner, self.user)
        self.assertEqual(account.comment, 'Test Device')
        self.assertTrue(account.password)

    def test_account_limit(self):
        # Create max number of accounts
        for i in range(settings.EDUROAM_SETTINGS['MAX_ACCOUNTS']):
            EduroamAccount.objects.create(
                owner=self.user,
                username=f'edu{i}@thga.de',
                password='test123',
                comment=f'Device {i}'
            )
        
        # Try to create one more
        response = self.client.post(reverse('eduroam:create'), {
            'comment': 'One Too Many'
        })
        self.assertEqual(EduroamAccount.objects.count(), settings.EDUROAM_SETTINGS['MAX_ACCOUNTS'])

    def test_password_reset(self):
        account = EduroamAccount.objects.create(
            owner=self.user,
            username='edu1@thga.de',
            password='oldpass',
            comment='Test Device'
        )
        old_password = account.password
        
        response = self.client.post(
            reverse('eduroam:update', kwargs={'pk': account.pk})
        )
        
        account.refresh_from_db()
        self.assertNotEqual(account.password, old_password)

    def test_account_deletion(self):
        account = EduroamAccount.objects.create(
            owner=self.user,
            username='edu1@thga.de',
            password='test123',
            comment='Test Device'
        )
        
        # 4. Lösche Account
        response = self.client.post(
            reverse('eduroam:delete', kwargs={'pk': account.pk})
        )
        account.refresh_from_db()
        self.assertTrue(account.is_deleted)
        
