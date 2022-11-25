from django.core.management import BaseCommand

from hct_mis_api.apps.core.management.sql import drop_databases


class Command(BaseCommand):
    def handle(self, *args, **options):
        drop_databases()
