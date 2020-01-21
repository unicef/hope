from django.core.exceptions import ValidationError

from core.validators import BaseValidator


class ProgramValidator(BaseValidator):
    def validate_status_change(self, *args, **kwargs):
        status_to_set = kwargs.get("program_data").get("status")
        program = kwargs.get("program")
        current_status = program.status

        if current_status == "DRAFT" and status_to_set != "ACTIVE":
            raise ValidationError("Draft status can only be changed to Active")
        elif current_status == "ACTIVE" and status_to_set != "FINISHED":
            raise ValidationError(
                "Active status can only be changed to Finished"
            )
        elif current_status == "FINISHED" and status_to_set != "ACTIVE":
            raise ValidationError(
                "Finished status can only be changed to Active"
            )


class CashPlanValidator(BaseValidator):
    pass
