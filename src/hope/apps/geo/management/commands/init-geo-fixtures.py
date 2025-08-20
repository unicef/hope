import logging
from typing import Any

from django.core.management import BaseCommand, call_command
from extras.test_utils.factories.geo import generate_area_types, generate_areas

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        initialize_geo_fixtures()


def initialize_geo_fixtures() -> None:
    call_command("loadcountries")
    generate_area_types()
    generate_areas()
