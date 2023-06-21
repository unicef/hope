import logging
from typing import Any, Optional

from django.core.management import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction

from hct_mis_api.apps.activity_log.models import LogEntry

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        activity_log_assign_program()


def get_program_id(log: "LogEntry") -> Optional[Any]:
    obj = log.content_object
    class_name = obj.__class__.__name__

    # TODO: update after changes for Ind and HH collections/representations
    class_name_to_program_id_mapping = {
        "GrievanceTicket": (obj, "programme_id"),
        # "Household": (obj, "programme_id"),
        # "Individual": (obj, "programme_id"),
        "PaymentPlan": (obj.get_program, "pk"),
        "CashPlan": (obj, "program_id"),
        "PaymentVerificationPlan": (obj.get_program, "pk"),
        "PaymentVerification": (obj.payment_verification_plan.get_program, "pk"),
        "Program": (obj, "pk"),
        "TargetPopulation": (obj.program, "pk"),
        "RegistrationDataImport": (obj, "program_id"),
    }
    obj, nested_field = class_name_to_program_id_mapping[class_name]
    return getattr(obj, nested_field, None)


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
            log.program_id = get_program_id(log)
            to_update.append(log)

        LogEntry.objects.bulk_update(to_update, ["program_id"])

    print("Finished Updating Activity Logs")
