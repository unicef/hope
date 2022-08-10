import logging
from pathlib import Path

from django.core.management import BaseCommand

from hct_mis_api.apps.core.models import CountryCodeMap
from hct_mis_api.apps.geo.models import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "load_business_areas"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            action="store",
            nargs="?",
            default="./data/country_code_mapping.txt",
            type=str,
            help="file",
        )

    def handle(self, *args, **options):
        with Path(options["file"]).open() as f:
            for line in f.readlines():
                iso_code, ca_code = line.split()
                country = Country.objects.get(iso_code3=iso_code)
                CountryCodeMap.objects.get_or_create(country=country, defaults={"ca_code": ca_code})
