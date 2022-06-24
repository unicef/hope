from django.core.management import BaseCommand

from hct_mis_api.apps.geo.utils import initialise_countries


class Command(BaseCommand):
    def handle(self, *args, **options):
        initialise_countries()
