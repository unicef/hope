import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator, CommonValidator
from hct_mis_api.apps.program.models import Program, ProgramCycle

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


class ProgramDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.DRAFT:
            logger.error("Only Draft Program can be deleted.")
            raise ValidationError("Only Draft Program can be deleted.")


class CashPlanValidator(BaseValidator):
    pass


class ProgramCycleValidator(CommonValidator):
    # TODO: add kwargs.get("start_date") and kwargs.get("end_date") and kwargs["name"]

    @classmethod
    def validate_program(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.ACTIVE:
            raise ValidationError("Create/Update Program Cycle is possible only for Active Program.")

    @classmethod
    def validate_program_start_end_dates(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if kwargs.get("start_date") < program.start_date:
            raise ValidationError("Program Cycle start date can't be earlier then Program start date")
        if end_date := kwargs.get("end_date"):
            if end_date > program.end_date:
                raise ValidationError("Program Cycle end date can't be later then Program end date")

    @classmethod
    def validate_cycles_has_end_date(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.cycles.filter(end_date__isnull=True).exists():
            raise ValidationError("All Program Cycles should have end date for creation new one.")

    @classmethod
    def validate_timeframes_overlaping(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        # A user can leave the Program Cycle end date empty if it was empty upon starting the edit.
        cycles = program.cycles.all().order_by("iteration")
        for i in range(1, len(cycles)):
            if cycles[i].start_date < cycles[i - 1].end_date:
                raise ValidationError("Program Cycles' timeframes mustn't overlap.")

    @classmethod
    def validate_program_cycle_name(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        # A user can’t leave the Program Cycle name empty.
        if program.cycles.filter(name=kwargs["name"]).exists():
            raise ValidationError("Program Cycles' name should be unique.")


class ProgramCycleDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program_cycle: ProgramCycle, *args: Any, **kwargs: Any) -> None:
        if program_cycle.program.status != Program.ACTIVE:
            raise ValidationError("Only Program Cycle for Active Program can be deleted.")

        if program_cycle.status != ProgramCycle.DRAFT:
            raise ValidationError("Only Draft Program Cycle can be deleted.")
