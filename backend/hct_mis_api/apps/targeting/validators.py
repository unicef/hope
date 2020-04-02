from core.validators import BaseValidator
from graphql import GraphQLError


class TargetValidator(BaseValidator):
    """Validator for Target Population."""

    @staticmethod
    def validate_is_finalized(target_status):
        if target_status == "FINALIZED":
            raise GraphQLError(
                "Target Population has been finalized. Cannot change."
            )


class ApproveTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "DRAFT":
            raise GraphQLError(
                "Only Target Population with status DRAFT can be approved"
            )


class UnapproveTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "APPROVED":
            raise GraphQLError(
                "Only Target Population with status APPROVED can be unapproved"
            )


class FinalizeTargetPopulationValidator:
    @staticmethod
    def validate(target_population):
        if target_population.status != "APPROVED":
            raise GraphQLError(
                "Only Target Population with status APPROVED can be finalized"
            )
