from core.validators import BaseValidator
from graphql import GraphQLError
from targeting.models import TargetStatus


class TargetValidator(BaseValidator):
    """Validator for Target Population."""

    @staticmethod
    def validate_is_finalized(target_status):
        if target_status == TargetStatus.FINALIZED.name:
            raise GraphQLError(
                "Target Population has been finalized. Cannot change."
            )
