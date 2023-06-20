import logging
from typing import Any

from django.core.management import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction

from hct_mis_api.apps.activity_log.models import LogEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        activity_log_assign_program()


@transaction.atomic
def activity_log_assign_program() -> None:
    log_qs = LogEntry.objects.all().exclude(program__isnull=False)

    print(f"Found {log_qs.count()} Logs for assign to program")

    paginator = Paginator(log_qs, 1000)
    number_of_pages = paginator.num_pages

    for page in paginator.page_range:
        to_update = []
        print(f"Loading page {page} of {number_of_pages}")

        for log in paginator.page(page).object_list:
            # TODO: add more logic here
            # log.program_id = "UUID_here"
            to_update.append(log)

        LogEntry.objects.bulk_update(to_update, ["program_id"])

    print("Finished Updating Activity Logs")
