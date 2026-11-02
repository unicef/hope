from typing import TYPE_CHECKING

from django.db import models

from hope.apps.targeting.services.targeting_service import TargetingIndividualRuleFilterBlockBase
from hope.models.utils import LongNameIndex, TimeStampedUUIDModel

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TargetingIndividualRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingIndividualRuleFilterBlockBase,
):
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule",
        on_delete=models.CASCADE,
        related_name="individuals_filters_blocks",
    )
    target_only_hoh = models.BooleanField(default=False)

    class Meta:
        app_label = "targeting"
        ordering = ("id",)
        indexes = [
            LongNameIndex(fields=["created_at"], name="targeting_targetingindivid_created_at_d8642e03"),
            LongNameIndex(fields=["updated_at"], name="targeting_targetingindivid_updated_at_7593c42a"),
        ]

    def get_individual_block_filters(self) -> "QuerySet":
        return self.individual_block_filters.all()
