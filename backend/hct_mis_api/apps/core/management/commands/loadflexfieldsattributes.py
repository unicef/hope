import logging

from django.core.management import BaseCommand

from core.admin import FlexibleAttributeImporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "load flex fields attributes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            action="store",
            nargs="?",
            default="./data/FlexibleAttributesInit.xls",
            type=str,
            help="file",
        )

    def handle(self, *args, **options):
        file = options["file"]
        importer = FlexibleAttributeImporter()
        importer.import_xls(file)
        logger.debug(f"Imported flex field attributes from {file}")
