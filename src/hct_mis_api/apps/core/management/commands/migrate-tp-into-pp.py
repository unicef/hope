import logging
from typing import Any

from django.core.management import BaseCommand
from django.utils import timezone

from hct_mis_api.one_time_scripts.migrate_tp_into_pp import migrate_tp_into_pp

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate all TargetPopulation objects into PaymentPlan"

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = timezone.now()
        self.stdout.write("Starting processing... TP...>...PP")

        # run script
        migrate_tp_into_pp()

        self.stdout.write(self.style.SUCCESS(f"Done in {timezone.now() - start_time}"))
