import logging
from typing import Any, Optional

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator, CommonValidator
from hct_mis_api.apps.payment.models import PaymentPlan
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

        # Finish Program -> check all Payment Plans
        if status_to_set == Program.FINISHED:
            # TODO: update after PaymentPlan status update
            # status=PaymentPlan.Status.RECONCILED
            if program.paymentplan_set.exclude(
                status__in=[PaymentPlan.Status.ACCEPTED, PaymentPlan.Status.FINISHED]
            ).exists():
                raise ValidationError("All Payment Plans and Follow-Up Payment Plans have to be Reconciled.")


class ProgramDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, program: Program, *args: Any, **kwargs: Any) -> None:
        if program.status != Program.DRAFT:
            logger.error("Only Draft Program can be deleted.")
            raise ValidationError("Only Draft Program can be deleted.")


class CashPlanValidator(BaseValidator):
    pass


class ProgramCycleValidator(CommonValidator):
    @classmethod
    def validate_program(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if program.status != Program.ACTIVE:
            raise ValidationError("Create/Update Program Cycle is possible only for Active Program.")

    @classmethod
    def validate_program_start_end_dates(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if start_date := kwargs.get("start_date"):
            if start_date < program.start_date:
                raise ValidationError("Program Cycle start date can't be earlier then Program start date")
        if end_date := kwargs.get("end_date"):
            if end_date > program.end_date:
                raise ValidationError("Program Cycle end date can't be later then Program end date")

    @classmethod
    def validate_cycles_has_end_date(cls, *args: Any, **kwargs: Any) -> None:
        program = kwargs.get("program")
        if kwargs.get("is_create_action"):
            if program.cycles.filter(end_date__isnull=True).exists():
                raise ValidationError("All Program Cycles should have end date for creation new one.")

    @classmethod
    def validate_timeframes_overlaping(cls, *args: Any, **kwargs: Any) -> None:
        # A user can leave the Program Cycle end date empty if it was empty upon starting the edit.
        program = kwargs.get("program")
        cycles = program.cycles.all().order_by("iteration")
        for i in range(1, len(cycles)):
            if cycles[i].start_date < cycles[i - 1].end_date:
                raise ValidationError("Program Cycles' timeframes mustn't overlap.")

    @classmethod
    def validate_program_cycle_name(cls, *args: Any, **kwargs: Any) -> None:
        # A user can’t leave the Program Cycle name empty.
        program = kwargs.get("program")
        if program.cycles.filter(name=kwargs["name"]).exists():
            raise ValidationError("Program Cycles' name should be unique.")


class ProgramCycleDeletionValidator(BaseValidator):
    @classmethod
    def validate_is_deletable(cls, *args: Any, **kwargs: Any) -> None:
        program_cycle = kwargs.get("program_cycle")
        if program_cycle.program.status != Program.ACTIVE:
            raise ValidationError("Only Program Cycle for Active Program can be deleted.")

        if program_cycle.status != ProgramCycle.DRAFT:
            raise ValidationError("Only Draft Program Cycle can be deleted.")
