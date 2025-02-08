# yourapp/management/commands/create_dovecot_users_view.py
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Creates the dovecot_users view'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE OR REPLACE VIEW dovecot_users AS
                select
                    ed.username as login,
                    LEFT(SPLIT_PART(ed.username, '@', 1), -3) as username,
                    SPLIT_PART(ed.username, '@', 2) AS "domain",
                    LEFT(SPLIT_PART(ed.username, '@', 1), -3) || '@' || SPLIT_PART(ed.username, '@', 2) as fqdn,
                    '{CRYPT}' || ed.password as password,
                    ed.password as dbpassword,
                    ('/srv/vmail/' || 
                    SPLIT_PART(ed.username, '@', 2) || '/' || 
                    LEFT(SPLIT_PART(ed.username, '@', 1), -3)) as home,
                    5000 as uid,
                    5000 as gid,
                    'Y' as active
                FROM 
                    public.emaildevice_emaildevice ed where ed.status = 1;
                           
                GRANT SELECT ON dovecot_users TO dovecot_user;
            """)