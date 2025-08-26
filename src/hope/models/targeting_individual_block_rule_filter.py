from typing import Any

from hope.apps.targeting.services.targeting_service import TargetingCriteriaFilterBase
from django.db import models

from hope.apps.targeting.choices import FlexFieldClassification
from django.db.models import JSONField

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory

from hope.apps.core.field_attributes.fields_types import Scope
from hope.models.utils import TimeStampedUUIDModel


class TargetingIndividualBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterBase):
    """Explicit filter like.

    :Age <> 10-20
    :Residential Status = Refugee
    :Residential Status != Refugee
    """

    comparison_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterBase.COMPARISON_CHOICES,
    )
    individuals_filters_block = models.ForeignKey(
        "models.targeting_individual_rule_filter_block.TargetingIndividualRuleFilterBlock",
        related_name="individual_block_filters",
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
        return False

    def get_core_fields(self) -> list:
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_individual()

    def get_lookup_prefix(self, associated_with: Any) -> str:
        return ""
