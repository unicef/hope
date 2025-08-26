from hope.apps.targeting.services.targeting_service import TargetingIndividualRuleFilterBlockBase
from django.db import models

from hope.models.utils import TimeStampedUUIDModel


class TargetingIndividualRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingIndividualRuleFilterBlockBase,
):
    targeting_criteria_rule = models.ForeignKey(
        "models.targeting_criteria_rule.TargetingCriteriaRule",
        on_delete=models.CASCADE,
        related_name="individuals_filters_blocks",
    )
    target_only_hoh = models.BooleanField(default=False)

    class Meta:
        app_label = "targeting"

    def get_individual_block_filters(self) -> "QuerySet":
        return self.individual_block_filters.all()
