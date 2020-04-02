from django.core.exceptions import ValidationError

from core.validators import BaseValidator


class TargetValidator(BaseValidator):
    """Validator for Target Population."""

    @staticmethod
    def validate_is_finalized(target_status):
        if target_status == "FINALIZED":
            raise ValidationError(
                "Target Population has been finalized. Cannot change."
            )


class ApproveTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "DRAFT":
            raise ValidationError(
                "Only Target Population with status DRAFT can be approved"
            )


class UnapproveTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "APPROVED":
            raise ValidationError(
                "Only Target Population with status APPROVED can be unapproved"
            )


class FinalizeTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "APPROVED":
            raise ValidationError(
                "Only Target Population with status APPROVED can be finalized"
            )
