from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q

from hope.apps.targeting.services.targeting_service import TargetingCriteriaRuleQueryingBase
from hope.models.utils import TimeStampedUUIDModel

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TargetingCriteriaRule(TimeStampedUUIDModel, TargetingCriteriaRuleQueryingBase):
    """Set of ANDed Filters."""

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        related_name="rules",
        on_delete=models.CASCADE,
    )
    household_ids = models.TextField(blank=True)
    individual_ids = models.TextField(blank=True)

    class Meta:
        app_label = "targeting"

    def get_filters(self) -> "QuerySet":
        return self.filters.all()

    def get_individuals_filters_blocks(self) -> "QuerySet":
        return self.individuals_filters_blocks.all()

    def get_collectors_filters_blocks(self) -> "QuerySet":
        return self.collectors_filters_blocks.all()

    def get_query(self) -> Q:
        query = super().get_query()

        q_hh_ids = Q(unicef_id__in=self.household_ids.split(", "))
        q_ind_ids = Q(individuals__unicef_id__in=self.individual_ids.split(", "))

        if self.household_ids and self.individual_ids:
            query &= Q(q_hh_ids | q_ind_ids)
            return query

        if self.household_ids:
            query &= q_hh_ids
        if self.individual_ids:
            query &= q_ind_ids

        return query
