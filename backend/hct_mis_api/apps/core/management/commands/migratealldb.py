import logging

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migrate all databases specified in settings'

    def handle(self, *args, **options):
        for db in settings.DATABASES:
            logger.info(f'Migrating {db} database')
            call_command('migrate', database=db)
