from django.conf import settings
from ldap3 import Server, Connection, MODIFY_REPLACE
import logging

logger = logging.getLogger(__name__)

class LdapService:
    def __init__(self):
        self.server = Server(settings.LDAP_MAIL_LOGIN_CONFIG['SERVER_URI'])
        self.conn = Connection(
            self.server,
            settings.LDAP_MAIL_LOGIN_CONFIG['BIND_DN'],
            settings.LDAP_MAIL_LOGIN_CONFIG['BIND_PASSWORD'],
            auto_bind=True
        )

    def set_mail_login(self, username, value):
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['distinguishedName'])
        
        if not self.conn.entries:
            return False
        user_dn = self.conn.entries[0].entry_dn
        self.conn.modify(user_dn,
            {'mailLoginByLdap': [(MODIFY_REPLACE, [str(value).lower()])]})
        return self.conn.result['description'] == 'success'
    
    def get_mail_login(self, username):
        self.conn.search(settings.LDAP_MAIL_LOGIN_CONFIG['USER_BASE_DN'],
                        f'(userPrincipalName={username})',
                        attributes=['mailLoginByLdap'])

        if not self.conn.entries:
            return False
        return bool(self.conn.entries[0].mailLoginByLdap.value)