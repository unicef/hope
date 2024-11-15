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
    help = "Remove pre-GPF data, with is_original=True"

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = timezone.now()
        self.stdout.write("Starting to remove pre-GPF data.")

        # get statistics
        get_statistic_is_original()
        # run script
        remove_migrated_data_is_original()
        # get statistics after
        get_statistic_is_original()

        self.stdout.write(self.style.SUCCESS(f"Done in {timezone.now() - start_time}"))
