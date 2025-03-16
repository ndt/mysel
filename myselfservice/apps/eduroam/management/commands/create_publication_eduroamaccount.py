# eduroam/management/commands/create_publication_eduroamaccount.py
from django.core.management.base import BaseCommand
from django.db import connection
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Creates the replication publication for table eduroam_eduroamaccount'

    def handle(self, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                # Check if publication exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM pg_publication WHERE pubname = 'eduroam_pub'
                    );
                """)
                exists = cursor.fetchone()[0]
                
                if not exists:
                    cursor.execute("""
                        CREATE PUBLICATION eduroam_pub FOR TABLE eduroam_eduroamaccount;
                        GRANT ALL ON eduroam_eduroamaccount TO replicator;
                        GRANT USAGE ON SCHEMA public TO replicator;
                    """)
                    logger.info('Successfully created publication eduroam_pub')
                else:
                    logger.info('Publication eduroam_pub already exists')
        except Exception as e:
            logger.error(f'Failed to create/check publication: {str(e)}')
            raise