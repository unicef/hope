import logging

from django.db import models
from django.db.models import JSONField, Q
from django.utils.translation import gettext_lazy as _
from model_utils import Choices

from hope.apps.targeting.choices import FlexFieldClassification
from hope.apps.targeting.services.targeting_service import (
    TargetingCriteriaFilterBase,
)
from hope.models.household import (
    ROLE_PRIMARY,
)
from hope.models.individual import Individual
from hope.models.individual_role_in_household import IndividualRoleInHousehold
from hope.models.utils import TimeStampedUUIDModel

logger = logging.getLogger(__name__)


class TargetingCollectorBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterBase):
    collector_block_filters = models.ForeignKey(
        "targeting.TargetingCollectorRuleFilterBlock",
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

    class Meta:
        app_label = "targeting"

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
