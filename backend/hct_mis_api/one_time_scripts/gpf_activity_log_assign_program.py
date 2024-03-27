"""
This migration has to be run after migration all Individuals and Households 'migrate_data_to_representations' and after migrate Grievances
"""

import abc
import logging
from typing import TYPE_CHECKING, Any, Union

from django.core.paginator import Paginator
from django.db import transaction

from hct_mis_api.apps.activity_log.models import LogEntry

if TYPE_CHECKING:
    from uuid import UUID

logger = logging.getLogger(__name__)


class GetProgramId(abc.ABC):
    obj: Any
    class_name: str
    nested_field: str

    def __init__(self, obj: Any) -> None:
        self.class_name: str = obj.__class__.__name__

        if self.class_name == "GrievanceTicket":
            self.obj = obj.programs.all()
            self.nested_field = "pk"

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

        elif self.class_name == "Household":
            self.obj = obj.programs.all()
            self.nested_field = "pk"

        elif self.class_name == "Individual":
            self.obj = obj.household.programs.all()
            self.nested_field = "pk"
        else:
            raise ValueError(f"Can not found 'class_name' and 'nested_field' for class {self.class_name}")

    @property
    def get_id(self) -> Union["UUID", list, None]:
        if self.class_name in ("GrievanceTicket", "Household", "Individual"):
            return list(self.obj.values_list(self.nested_field, flat=True))

        return getattr(self.obj, self.nested_field, None)


@transaction.atomic
def activity_log_assign_program() -> None:
    log_qs = LogEntry.objects.all().exclude(programs__isnull=False)

    logger.info(f"Found {log_qs.count()} Logs for assign to program")

    paginator = Paginator(log_qs, 1000)
    number_of_pages = paginator.num_pages

    for page in paginator.page_range:
        logger.info(f"Loading page {page} of {number_of_pages}")

        for log in paginator.page(page).object_list:
            program_id = GetProgramId(log.content_object).get_id
            if isinstance(program_id, list):
                for program in program_id:
                    log.programs.add(program)
            elif program_id:
                log.programs.add(program_id)

    logger.info("Finished Updating Activity Logs")
