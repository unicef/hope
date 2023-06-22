import abc
import logging
from typing import TYPE_CHECKING, Any, Optional

from django.core.management import BaseCommand
from django.core.paginator import Paginator
from django.db import transaction

from hct_mis_api.apps.activity_log.models import LogEntry

if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any) -> None:
        activity_log_assign_program()


class GetProgramId(abc.ABC):
    obj: Any
    class_name: str
    nested_field: str

    def __init__(self, obj: Any) -> None:
        self.class_name: str = obj.__class__.__name__

        if self.class_name == "GrievanceTicket":
            self.obj = obj
            self.nested_field = "programme_id"

        elif self.class_name == "PaymentPlan":
            self.obj = obj.get_program
            self.nested_field = "pk"

        elif self.class_name == "CashPlan":
            self.obj = obj
            self.nested_field = "program_id"

        elif self.class_name == "PaymentVerificationPlan":
            self.obj = obj.get_program
            self.nested_field = "pk"

        elif self.class_name == "PaymentVerification":
            self.obj = obj.payment_verification_plan.get_program
            self.nested_field = "pk"

        elif self.class_name == "Program":
            self.obj = obj
            self.nested_field = "pk"

        elif self.class_name == "TargetPopulation":
            self.obj = obj.program
            self.nested_field = "pk"

        elif self.class_name == "RegistrationDataImport":
            self.obj = obj
            self.nested_field = "program_id"

        # TODO: update after changes for Ind and HH collections/representations
        # elif class_name == "Household":
        #     self.obj = obj
        #     self.nested_field = "program_id"
        #
        # elif class_name == "Individual":
        #     self.obj = obj
        #     self.nested_field = "program_id"
        else:
            raise ValueError(f"Can not found 'class_name' and 'nested_field' for class {self.class_name}")

    @property
    def get_id(self) -> Optional["UUID"]:
        return getattr(self.obj, self.nested_field, None)


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
            program_id = GetProgramId(log.content_object)
            log.program_id = program_id.get_id
            to_update.append(log)

        LogEntry.objects.bulk_update(to_update, ["program_id"])

    print("Finished Updating Activity Logs")
