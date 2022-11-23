from time import time
from typing import Any, TYPE_CHECKING

from django.core.management import BaseCommand

from hct_mis_api.apps.payment.services.handle_total_cash_in_households import (
    handle_total_cash_in_households,
)

if TYPE_CHECKING:
    from argparse import ArgumentParser


class Command(BaseCommand):
    help = "Fix total cash received in household"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--only-new",
            dest="only_new",
            default=False,
            action="store_true",
            help="If total_cash_received is null, will not parse these HHs",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        start_time = time()
        handle_total_cash_in_households(only_new=options["only_new"])
        print(f"time: {time()-start_time}")
