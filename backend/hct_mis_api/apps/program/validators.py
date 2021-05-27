import logging

from django.core.exceptions import ValidationError

from hct_mis_api.apps.core.validators import BaseValidator
from hct_mis_api.apps.program.models import Program

logger = logging.getLogger(__name__)


class ProgramValidator(BaseValidator):
    @classmethod
    def validate_status_change(cls, *args, **kwargs):
        status_to_set = kwargs.get("program_data").get("status")
        program = kwargs.get("program")
        current_status = program.status
        if status_to_set is None or status_to_set == current_status:
            return
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
    def validate_is_deletable(cls, program, *args, **kwargs):
        if program.status != Program.DRAFT:
            logger.error("Only Draft Program can be deleted.")
            raise ValidationError("Only Draft Program can be deleted.")


class CashPlanValidator(BaseValidator):
    pass
