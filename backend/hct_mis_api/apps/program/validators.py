import logging
import re
from typing import TYPE_CHECKING, Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator, CommonValidator
from hct_mis_api.apps.payment.models import PaymentPlan
from hct_mis_api.apps.program.models import Program, ProgramCycle

if TYPE_CHECKING:
    from hct_mis_api.apps.core.models import BusinessArea, DataCollectingType

logger = logging.getLogger(__name__)


class ProgramValidator(BaseValidator):
    @classmethod
    def validate_status_change(cls, *args: Any, **kwargs: Any) -> Optional[None]:
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
        elif current_status == Program.ACTIVE and status_to_set != Program.FINISHED:
            logger.error("Active status can only be changed to Finished")
            raise ValidationError("Active status can only be changed to Finished")
        elif current_status == Program.FINISHED and status_to_set != Program.ACTIVE:
            logger.error("Finished status can only be changed to Active")
            raise ValidationError("Finished status can only be changed to Active")

        # Finish Program -> check all Payment Plans
        if status_to_set == Program.FINISHED:
            if PaymentPlan.objects.filter(
                program_cycle__in=program.cycles.all(),
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED],
            ).exists():
                raise ValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")


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
        program: Optional[Program] = None,
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
    elif (
        data_collecting_type.code != original_program_data_collecting_type.code
        and data_collecting_type not in original_program_data_collecting_type.compatible_types.all()
    ):
        raise ValidationError("The Data Collection Type must be compatible with the original Programme.")


class ProgramCycleValidator(CommonValidator):
    @classmethod
    def validate_program(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if program.status != Program.ACTIVE:
            raise ValidationError("Create/Update Programme Cycle is possible only for Active Programme.")

    @classmethod
    def validate_program_start_end_dates(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if start_date := kwargs.get("start_date"):
            if start_date < program.start_date:
                raise ValidationError("Programme Cycle start date cannot be earlier than programme start date")
        if end_date := kwargs.get("end_date"):
            if end_date > program.end_date:
                raise ValidationError("Programme Cycle end date cannot be earlier than programme end date")

    @classmethod
    def validate_cycles_has_end_date(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if kwargs.get("is_create_action") and program.cycles.filter(end_date__isnull=True).exists():
            raise ValidationError("All Programme Cycles should have end date for creation new one.")

    @classmethod
    def validate_timeframes_overlapping(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        program_cycle = kwargs.get("program_cycle")
        start_date = kwargs.get("start_date")
        end_date = kwargs.get("end_date")
        raise_error = False

        existing_cycles = program.cycles.exclude(id=program_cycle.pk) if program_cycle else program.cycles.all()

        if start_date:
            if existing_cycles.filter(start_date__lte=start_date, end_date__gte=start_date).exists():
                raise_error = True
        if end_date:
            if existing_cycles.filter(start_date__lte=end_date, end_date__gte=end_date).exists():
                raise_error = True

        if raise_error:
            raise ValidationError("Programme Cycles' timeframes must not overlap.")

    @classmethod
    def validate_program_cycle_name(cls, *args: Any, **kwargs: Any) -> None:
        # A user can’t leave the Program Cycle name empty.
        program = kwargs.get("program")
        program_cycle = kwargs.get("program_cycle")
        cycles = program.cycles.exclude(id=program_cycle.pk) if program_cycle else program.cycles.all()
        if cycles.filter(name=kwargs["name"]).exists():
            raise ValidationError("Programme Cycles' name should be unique.")

    @classmethod
    def validate_program_cycle_update_name_and_dates(cls, *args: Any, **kwargs: Any) -> None:
        if (program_cycle := kwargs.get("program_cycle")) and not kwargs.get("is_create_action"):
            if program_cycle.start_date and "start_date" in kwargs and kwargs.get("start_date") is None:
                raise ValidationError("Not possible leave the Programme Cycle start date empty.")

            if program_cycle.end_date and "end_date" in kwargs and kwargs.get("end_date") is None:
                raise ValidationError(
                    "Not possible leave the Programme Cycle end date empty if it was empty upon starting the edit."
                )

            if program_cycle.name and "name" in kwargs and kwargs.get("name") is None:
                raise ValidationError("Not possible leave the Programme Cycle name empty.")


class ProgramCycleDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, *args: Any, **kwargs: Any) -> None:
        program_cycle = kwargs.get("program_cycle")
        if program_cycle.program.status != Program.ACTIVE:
            raise ValidationError("Only Programme Cycle for Active Programme can be deleted.")

        if program_cycle.status != ProgramCycle.DRAFT:
            raise ValidationError("Only Draft Programme Cycle can be deleted.")
