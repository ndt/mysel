import pytest
import requests
from bs4 import BeautifulSoup
import imaplib
import subprocess

class TestKeycloakAuthenticationAndMailLogin:
    def setup_method(self):
        self.mailserver = "mailserver"
        self.base_url = "http://myselfservice:8000"
        self.keycloak_url = "http://keycloak:8080"
        self.test_username = "testuser2@example.org"
        self.test_password = "testuser2"
        self.session = requests.Session()
        self._login()  # Führe Login für jeden Test durch

    def test_initial_imap_login(self):
        # Try IMAP login with test credentials - should work
        imap = imaplib.IMAP4(host=self.mailserver, port=143)
        imap.starttls()
        imap.login(self.test_username, self.test_password)
        imap.logout()

    def _login(self):
        # 1. Initiiere Login-Flow durch Aufruf der Django App
        response = self.session.get(
            f"{self.base_url}/accounts/oidc/keycloak/login/",
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # 2. Folge der Redirect URL zu Keycloak
        keycloak_url = response.headers['Location']
        response = self.session.get(keycloak_url, allow_redirects=True)
        assert response.status_code == 200
        
        # 3. Extrahiere notwendige Formulardaten von Keycloak
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', id='kc-form-login')
        
        # Extrahiere versteckte Formularfelder
        hidden_inputs = {}
        for hidden in form.find_all("input", type="hidden"):
            hidden_inputs[hidden.get('name')] = hidden.get('value')
        
        login_form_url = form.get('action')
        
        # 4. Führe Login durch mit allen notwendigen Formularfeldern
        login_data = {
            'username': self.test_username,
            'password': self.test_password,
            **hidden_inputs
        }
        
        headers = {
            'Origin': self.keycloak_url,
            'Referer': keycloak_url
        }
        
        response = self.session.post(
            login_form_url,
            data=login_data,
            headers=headers,
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # 5. Folge den Redirects zurück zur Django App
        final_response = self.session.get(
            response.headers['Location'],
            allow_redirects=True
        )
        assert final_response.status_code == 200
        
        # Verifiziere Login-Status
        response = self.session.get(f"{self.base_url}/emaildevice")
        assert response.status_code == 200

    def test_create_email_device(self):
        # Ensure we're logged and get form data
        response = self.session.get(f"{self.base_url}/emaildevice")
        assert response.status_code == 200
        
        # Parse the CSRF token from the response
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        # Make POST request with CSRF token
        response = self.session.post(
            f"{self.base_url}/emaildevice/create/",
            data={
                'csrfmiddlewaretoken': csrf_token
            },
            headers={
                'Referer': f"{self.base_url}/emaildevice/create"
            },
            allow_redirects=True
        )
        
        assert response.status_code == 200
        
        import re
        
        # Extract username
        username_pattern = r"modalUsername'\).value\s*=\s*[\"']([^\"']+)[\"']"
        username_match = re.search(username_pattern, response.text)
        username = username_match.group(1) if username_match else None

        # Extract password
        password_pattern = r"modalPassword'\).value\s*=\s*[\"']([^\"']+)[\"']"
        password_match = re.search(password_pattern, response.text)
        password = password_match.group(1) if password_match else None

        
        print(f"\nCreated email device credentials:")
        print(f"Username: {response.text}")
        print(f"Password: {password}")
        
        assert username is not None and username != ""
        assert password is not None and password != ""

        #time.sleep(1) # Give mailserver time to update
        # Try IMAP login with old credentials - should fail
        with pytest.raises(imaplib.IMAP4.error):
            imap = imaplib.IMAP4(self.mailserver)
            imap.starttls()
            imap.login(self.test_username, self.test_password)
            imap.logout()

        # Try IMAP login with new credentials - should work
        #time.sleep(1) # Give mailserver time to update

        imap = imaplib.IMAP4(self.mailserver)
        imap.starttls() 
        imap.login(username, password)
        imap.logout()

class TestKeycloakAuthenticationAndEduroamAccount:
    def setup_method(self):
        self.base_url = "http://myselfservice:8000"
        self.keycloak_url = "http://keycloak:8080"
        self.test_username = "testuser3@example.org"
        self.test_password = "testuser3"
        self.session = requests.Session()
        self._login()  # Führe Login für jeden Test durch

    def _login(self):
        # 1. Initiiere Login-Flow durch Aufruf der Django App
        response = self.session.get(
            f"{self.base_url}/accounts/oidc/keycloak/login/",
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # 2. Folge der Redirect URL zu Keycloak
        keycloak_url = response.headers['Location']
        response = self.session.get(keycloak_url, allow_redirects=True)
        assert response.status_code == 200
        
        # 3. Extrahiere notwendige Formulardaten von Keycloak
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', id='kc-form-login')
        
        # Extrahiere versteckte Formularfelder
        hidden_inputs = {}
        for hidden in form.find_all("input", type="hidden"):
            hidden_inputs[hidden.get('name')] = hidden.get('value')
        
        login_form_url = form.get('action')
        
        # 4. Führe Login durch mit allen notwendigen Formularfeldern
        login_data = {
            'username': self.test_username,
            'password': self.test_password,
            **hidden_inputs
        }
        
        headers = {
            'Origin': self.keycloak_url,
            'Referer': keycloak_url
        }
        
        response = self.session.post(
            login_form_url,
            data=login_data,
            headers=headers,
            allow_redirects=False
        )
        assert response.status_code == 302
        
        # 5. Folge den Redirects zurück zur Django App
        final_response = self.session.get(
            response.headers['Location'],
            allow_redirects=True
        )
        assert final_response.status_code == 200
        
        # Verifiziere Login-Status
        response = self.session.get(f"{self.base_url}/eduroam")
        assert response.status_code == 200


    def test_eduroam_account_creation_usage(self):
        # Ensure we're logged and get form data
        response = self.session.get(f"{self.base_url}/eduroam")
        assert response.status_code == 200
        
        # Parse the CSRF token from the response
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})['value']
        
        # Make POST request with CSRF token
        response = self.session.post(
            f"{self.base_url}/eduroam/create/",
            data={
                'csrfmiddlewaretoken': csrf_token
            },
            headers={
                'Referer': f"{self.base_url}/eduroam/create"
            },
            allow_redirects=True
        )
        
        assert response.status_code == 200
        
        import re
        
        # Extract username
        username_pattern = r"modalUsername'\).value\s*=\s*[\"']([^\"']+)[\"']"
        username_match = re.search(username_pattern, response.text)
        username = username_match.group(1) if username_match else None

        # Extract password
        password_pattern = r"modalPassword'\).value\s*=\s*[\"']([^\"']+)[\"']"
        password_match = re.search(password_pattern, response.text)
        password = password_match.group(1) if password_match else None

        
        print(f"\nCreated eduroam credentials:")
        print(f"Username: {username}")
        print(f"Password: {password}")
        
        assert username is not None and username != ""
        assert password is not None and password != ""

        cmd = f"radtest {username} {password} freeradius 0 testing123"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        assert result.returncode == 0
    
