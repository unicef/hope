import logging
from typing import Any

from django.core.management import BaseCommand

from extras.test_utils.factories.core import (
    generate_business_areas,
    generate_country_codes,
    generate_data_collecting_types,
)
from flags.models import FlagState

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        initialize_core_fixtures()


def initialize_core_fixtures() -> None:
    generate_country_codes()
    generate_business_areas()
    generate_data_collecting_types()

    FlagState.objects.get_or_create(
        **{"name": "ALLOW_ACCOUNTABILITY_MODULE", "condition": "boolean", "value": "True", "required": False}
    )
