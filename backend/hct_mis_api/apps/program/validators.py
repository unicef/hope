import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator
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


class ProgramCycleValidator(BaseValidator):
    """
    -The program is in Active status.
    - Upon creation, a Program Cycle is in the Draft status.
    - All cycles in the Program have to have an end date for a user to create a new Cycle.
    """

    @classmethod
    def validate_start_end_dates(cls, *args: Any, **kwargs: Any) -> None:
        """
        - Program cycles' timeframes mustn't overlap.
        """
        pass


class UpdateProgramCycleValidator(BaseValidator):
    """ """

    @classmethod
    def validate_start_end_dates(cls, *args: Any, **kwargs: Any) -> None:
        """
        - Program cycles' timeframes mustn't overlap.
        """
        pass


class ProgramCycleDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program: Program, program_cycle: ProgramCycle, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.ACTIVE:
            logger.error("Only Program Cycle for Active Program can be deleted.")
            raise ValidationError("Only Program Cycle for Active Program can be deleted.")
        if program_cycle.status != ProgramCycle.DRAFT:
            logger.error("Only Draft Program Cycle can be deleted.")
            raise ValidationError("Only Draft Program Cycle can be deleted.")
