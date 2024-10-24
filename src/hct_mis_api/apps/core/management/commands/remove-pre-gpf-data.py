import logging
from typing import Any

from django.core.management import BaseCommand
from django.utils import timezone

from hct_mis_api.one_time_scripts.remove_migrated_data_is_original import (
    get_statistic_is_original,
    remove_migrated_data_is_original,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Remove data with 'is_origin=True'."

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = timezone.now()

        self.stdout.write("... Getting some statistics ...")

        get_statistic_is_original()

        self.stdout.write(self.style.SUCCESS("Starting remove data..."))

        remove_migrated_data_is_original()

        self.stdout.write(self.style.SUCCESS(f"Done in {timezone.now() - start_time}"))
