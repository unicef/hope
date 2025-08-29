from django.db import models
from django.db.models import JSONField

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.services.targeting_service import TargetingCriteriaFilterBase
from hope.models.utils import TimeStampedUUIDModel


class TargetingCriteriaRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterBase):
    """Explicit filter.

    :Age <> 10-20
    :Residential Status = Refugee
    :Residential Status != Refugee
    """

    comparison_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterBase.COMPARISON_CHOICES,
    )
    targeting_criteria_rule = models.ForeignKey(
        "targeting.TargetingCriteriaRule",
        related_name="filters",
        on_delete=models.CASCADE,
    )
    flex_field_classification = models.CharField(
        max_length=20,
        choices=FlexFieldClassification.choices,
        default=FlexFieldClassification.NOT_FLEX_FIELD,
    )
    field_name = models.CharField(max_length=50)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )
    round_number = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        app_label = "targeting"

    @property
    def is_social_worker_program(self) -> bool:
        try:
            return self.targeting_criteria_rule.payment_plan.program_cycle.program.is_social_worker_program
        except (
            AttributeError,
            TargetingCriteriaRuleFilter.targeting_criteria_rule.RelatedObjectDoesNotExist,
        ):
            return False

    def get_core_fields(self) -> list:
        if self.is_social_worker_program:
            return FieldFactory.from_only_scopes([Scope.TARGETING, Scope.XLSX_PEOPLE])
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_household()
