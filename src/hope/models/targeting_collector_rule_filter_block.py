from typing import TYPE_CHECKING

from django.db import models

from hope.apps.targeting.services.targeting_service import TargetingCollectorRuleFilterBlockBase
from hope.models.utils import TimeStampedUUIDModel

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TargetingCollectorRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingCollectorRuleFilterBlockBase,
):
    targeting_criteria_rule = models.ForeignKey(
        "targeting.TargetingCriteriaRule",
        on_delete=models.CASCADE,
        related_name="collectors_filters_blocks",
    )

    class Meta:
        app_label = "targeting"

    def get_collector_block_filters(self) -> "QuerySet":
        return self.collector_block_filters.all()
