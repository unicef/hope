from typing import TYPE_CHECKING

from hct_mis_api.apps.targeting.services.targeting_service import (
    TargetingCriteriaQueryingBase,
)
from hct_mis_api.apps.utils.models import TimeStampedUUIDModel

if TYPE_CHECKING:
    from django.db.models.query import QuerySet


class TargetingCriteria(TimeStampedUUIDModel, TargetingCriteriaQueryingBase):
    """
    This is a set of ORed Rules. These are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate
    list).
    """

    def get_rules(self) -> "QuerySet":
        return self.rules.all()
