import logging
from typing import TYPE_CHECKING, Any

from django.db import models
from django.db.models import JSONField, Q
from django.utils.translation import gettext_lazy as _

from model_utils import Choices

from hope.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hope.apps.core.field_attributes.fields_types import Scope
from hope.apps.household.models import (
    ROLE_PRIMARY,
    Individual,
    IndividualRoleInHousehold,
)
from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.services.targeting_service import (
    TargetingCollectorRuleFilterBlockBase,
    TargetingCriteriaFilterBase,
    TargetingCriteriaRuleQueryingBase,
    TargetingIndividualRuleFilterBlockBase,
)
from hope.apps.utils.models import TimeStampedUUIDModel

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class TargetingCriteriaRule(TimeStampedUUIDModel, TargetingCriteriaRuleQueryingBase):
    """Set of ANDed Filters."""

    payment_plan = models.ForeignKey(
        "payment.PaymentPlan",
        related_name="rules",
        on_delete=models.CASCADE,
    )
    household_ids = models.TextField(blank=True)
    individual_ids = models.TextField(blank=True)

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

    def get_individual_block_filters(self) -> "QuerySet":
        return self.individual_block_filters.all()


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
        "TargetingCriteriaRule",
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
        "TargetingIndividualRuleFilterBlock",
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

    @property
    def is_social_worker_program(self) -> bool:
        return False

    def get_core_fields(self) -> list:
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_individual()

    def get_lookup_prefix(self, associated_with: Any) -> str:
        return ""


class TargetingCollectorRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingCollectorRuleFilterBlockBase,
):
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule",
        on_delete=models.CASCADE,
        related_name="collectors_filters_blocks",
    )

    def get_collector_block_filters(self) -> "QuerySet":
        return self.collector_block_filters.all()


class TargetingCollectorBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterBase):
    collector_block_filters = models.ForeignKey(
        "TargetingCollectorRuleFilterBlock",
        related_name="collector_block_filters",
        on_delete=models.CASCADE,
    )
    field_name = models.CharField(max_length=120)
    comparison_method = models.CharField(
        max_length=20,
        choices=Choices(("EQUALS", _("Equals"))),
    )
    flex_field_classification = models.CharField(
        max_length=20,
        choices=FlexFieldClassification.choices,
        default=FlexFieldClassification.NOT_FLEX_FIELD,
    )
    arguments = JSONField(
        help_text="""
                Array of arguments
                """
    )

    def get_query(self) -> Q:
        program = self.collector_block_filters.targeting_criteria_rule.payment_plan.program_cycle.program
        argument = self.arguments[0] if len(self.arguments) else None
        if argument is None:
            return Q()

        collector_primary_qs = IndividualRoleInHousehold.objects.filter(
            household__program=program, role=ROLE_PRIMARY
        ).values_list("individual", flat=True)

        collectors_ind_query = Individual.objects.filter(
            pk__in=list(collector_primary_qs),
        )

        account_type, field_name = self.field_name.split("__")
        query_method = collectors_ind_query.filter if argument is True else collectors_ind_query.exclude
        individuals_with_field_query = query_method(
            accounts__data__has_key=field_name,
            accounts__account_type__key=account_type,
        )
        return Q(pk__in=list(individuals_with_field_query.values_list("household_id", flat=True)))
