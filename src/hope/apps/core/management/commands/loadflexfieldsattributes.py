from argparse import ArgumentParser
import logging

from django.conf import settings
from django.core.management import BaseCommand

from hope.apps.core.flex_fields_importer import FlexibleAttributeImporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "load flex fields attributes"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--file",
            dest="file",
            action="store",
            nargs="?",
            default=f"{settings.PROJECT_ROOT}/../data/FlexibleAttributesInit.xlsx",
            type=str,
            help="file",
        )

    def handle(self, *args: object, **options: object) -> None:
        file = options["file"]
        importer = FlexibleAttributeImporter()
        importer.import_xls(file)
        logger.debug(f"Imported flex field attributes from {file}")
