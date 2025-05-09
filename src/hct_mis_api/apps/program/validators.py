import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program, ProgramCycle

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType

logger = logging.getLogger(__name__)


class ProgramValidator(BaseValidator):
    @classmethod
    def validate_status_change(cls, *args: Any, **kwargs: Any) -> None | None:
        status_to_set = kwargs.get("program_data").get("status")
        program = kwargs.get("program")
        current_status = program.status
        if status_to_set is None or status_to_set == current_status:
            return None
        if status_to_set not in dict(Program.STATUS_CHOICE):
            logger.error(f"Wrong status: {status_to_set}")
            raise ValidationError("Wrong status")
        if current_status == Program.DRAFT and status_to_set != Program.ACTIVE:
            logger.error("Draft status can only be changed to Active")
            raise ValidationError("Draft status can only be changed to Active")
        if current_status == Program.ACTIVE and status_to_set != Program.FINISHED:
            logger.error("Active status can only be changed to Finished")
            raise ValidationError("Active status can only be changed to Finished")
        if current_status == Program.FINISHED and status_to_set != Program.ACTIVE:
            logger.error("Finished status can only be changed to Active")
            raise ValidationError("Finished status can only be changed to Active")

        # Finish Program -> check all Payment Plans
        if status_to_set == Program.FINISHED and current_status == Program.ACTIVE:
            if (
                PaymentPlan.objects.filter(program_cycle__in=program.cycles.all())
                .exclude(
                    status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
                )
                .exists()
            ):
                raise ValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")

            # check if any ACTIVE cycles there
            if program.cycles.filter(status=ProgramCycle.ACTIVE).exists():
                raise ValidationError("Cannot finish programme with active cycles")

            if program.end_date is None:
                raise ValidationError("Cannot finish programme without end date")

    @classmethod
    def validate_end_date(cls, *args: Any, **kwargs: Any) -> None | None:
        program = kwargs.get("program")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")

        if ((start_date and end_date) and (end_date < start_date)) or (end_date and end_date < program.start_date):
            raise ValidationError("End date cannot be before start date.")

        if end_date and program.cycles.filter(end_date__gt=end_date).exists():
            raise ValidationError("End date must be equal or after the latest cycle.")

        if start_date and program.cycles.filter(start_date__lt=start_date).exists():
            raise ValidationError("Start date must be equal or before the earliest cycle.")


class ProgramDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.DRAFT:
            logger.error("Only Draft Program can be deleted.")
            raise ValidationError("Only Draft Program can be deleted.")


class ProgrammeCodeValidator(BaseValidator):
    @classmethod
    def validate_programme_code(
        cls,
        programme_code: str,
        business_area: "BusinessArea",
        program: Program | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        if programme_code:
            programme_code = programme_code.upper()
            if not re.match(r"^[A-Z0-9\-/.]{4}$", programme_code):
                raise ValidationError(
                    "Programme code should be exactly 4 characters long and may only contain letters, digits "
                    "and characters: - . /"
                )

            qs = Program.objects.filter(business_area=business_area, programme_code=programme_code)

            if program:
                qs = qs.exclude(id=program.id)

            if qs.exists():
                raise ValidationError("Programme code is already used.")


def validate_data_collecting_type(
    business_area: "BusinessArea",
    original_program_data_collecting_type: Optional["DataCollectingType"] = None,
    data_collecting_type: Optional["DataCollectingType"] = None,
) -> None:
    if data_collecting_type.limit_to.exists() and business_area not in data_collecting_type.limit_to.all():
        raise ValidationError("This Data Collection Type is not assigned to the Program's Business Area")

    if not original_program_data_collecting_type:
        raise ValidationError("The original Programme must have a Data Collection Type.")
    if (
        data_collecting_type.code != original_program_data_collecting_type.code
        and data_collecting_type not in original_program_data_collecting_type.compatible_types.all()
    ):
        raise ValidationError("The Data Collection Type must be compatible with the original Programme.")
