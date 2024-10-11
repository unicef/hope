import logging
from typing import TYPE_CHECKING, Any, List, Union

from django.conf import settings
from django.contrib.postgres.fields import CICharField
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import JSONField, Q
from django.db.models.constraints import UniqueConstraint
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from model_utils.models import SoftDeletableModel

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import StorageFile
from hct_mis_api.apps.core.utils import map_unicef_ids_to_households_unicef_ids
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.steficon.models import Rule, RuleCommit
from hct_mis_api.apps.targeting.choices import FlexFieldClassification
from hct_mis_api.apps.targeting.services.targeting_service import (
    TargetingCriteriaFilterBase,
    TargetingCriteriaQueryingBase,
    TargetingCriteriaRuleQueryingBase,
    TargetingIndividualRuleFilterBlockBase,
)
from hct_mis_api.apps.utils.models import (
    AdminUrlMixin,
    ConcurrencyModel,
    RepresentationManager,
    TimeStampedUUIDModel,
)
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)

if TYPE_CHECKING:
    from uuid import UUID

    from django.db.models.query import QuerySet

logger = logging.getLogger(__name__)


class TargetPopulation(SoftDeletableModel, TimeStampedUUIDModel, ConcurrencyModel, AdminUrlMixin):
    """Model for target populations.

    Has N:N association with households.
    """

    ACTIVITY_LOG_MAPPING = create_mapping_dict(
        [
            "name",
            "ca_id",
            "ca_hash_id",
            "created_by",
            "change_date",
            "changed_by",
            "finalized_at",
            "finalized_by",
            "status",
            "child_male_count",
            "child_female_count",
            "adult_male_count",
            "adult_female_count",
            "total_households_count",
            "total_individuals_count",
            "program",
            "targeting_criteria_string",
            "sent_to_datahub",
            "steficon_rule",
            "exclusion_reason",
            "excluded_ids",
        ],
        {
            "steficon_rule": "additional_formula",
            "steficon_applied_date": "additional_formula_applied_date",
            "vulnerability_score_min": "score_min",
            "vulnerability_score_max": "score_max",
        },
    )

    STATUS_OPEN = "OPEN"
    STATUS_LOCKED = "LOCKED"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_STEFICON_WAIT = "STEFICON_WAIT"
    STATUS_STEFICON_RUN = "STEFICON_RUN"
    STATUS_STEFICON_COMPLETED = "STEFICON_COMPLETED"
    STATUS_STEFICON_ERROR = "STEFICON_ERROR"
    STATUS_SENDING_TO_CASH_ASSIST = "SENDING_TO_CASH_ASSIST"
    STATUS_READY_FOR_CASH_ASSIST = "READY_FOR_CASH_ASSIST"
    STATUS_READY_FOR_PAYMENT_MODULE = "READY_FOR_PAYMENT_MODULE"
    STATUS_ASSIGNED = "ASSIGNED"

    STATUS_CHOICES = (
        (STATUS_OPEN, _("Open")),
        (STATUS_LOCKED, _("Locked")),
        (STATUS_STEFICON_WAIT, _("Waiting for Rule Engine")),
        (STATUS_STEFICON_RUN, _("Rule Engine Running")),
        (STATUS_STEFICON_COMPLETED, _("Rule Engine Completed")),
        (STATUS_STEFICON_ERROR, _("Rule Engine Errored")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_SENDING_TO_CASH_ASSIST, _("Sending to Cash Assist")),
        (STATUS_READY_FOR_CASH_ASSIST, _("Ready for cash assist")),
        (STATUS_READY_FOR_PAYMENT_MODULE, _("Ready for payment module")),
        (STATUS_ASSIGNED, _("Assigned")),
    )

    BUILD_STATUS_PENDING = "PENDING"
    BUILD_STATUS_BUILDING = "BUILDING"
    BUILD_STATUS_FAILED = "FAILED"
    BUILD_STATUS_OK = "OK"

    BUILD_STATUS_CHOICES = (
        (BUILD_STATUS_PENDING, _("Pending")),
        (BUILD_STATUS_BUILDING, _("Building")),
        (BUILD_STATUS_FAILED, _("Failed")),
        (BUILD_STATUS_OK, _("Ok")),
    )

    name = CICharField(
        db_index=True,
        max_length=255,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(255),
            DoubleSpaceValidator,
            StartEndSpaceValidator,
            ProhibitNullCharactersValidator(),
        ],
    )
    ca_id = CICharField(max_length=255, null=True, blank=True)
    ca_hash_id = CICharField(max_length=255, null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="target_populations",
        null=True,
    )
    change_date = models.DateTimeField(null=True, blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="changed_target_populations",
        null=True,
        blank=True,
    )
    finalized_at = models.DateTimeField(null=True, blank=True)
    finalized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="finalized_target_populations",
        null=True,
        blank=True,
    )
    business_area = models.ForeignKey("core.BusinessArea", null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=256, choices=STATUS_CHOICES, default=STATUS_OPEN, db_index=True)
    build_status = models.CharField(
        max_length=256, choices=BUILD_STATUS_CHOICES, default=BUILD_STATUS_PENDING, db_index=True
    )
    built_at = models.DateTimeField(null=True, blank=True)
    households = models.ManyToManyField(
        "household.Household",
        related_name="target_populations",
        through="HouseholdSelection",
    )
    program = models.ForeignKey(
        "program.Program",
        blank=True,
        null=True,
        help_text="""Set only when the target population moves from draft to
            candidate list frozen state (approved)""",
        on_delete=models.SET_NULL,
    )
    program_cycle = models.ForeignKey(
        "program.ProgramCycle", on_delete=models.CASCADE, related_name="target_populations"
    )
    targeting_criteria = models.OneToOneField(
        "TargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="target_population",
    )
    sent_to_datahub = models.BooleanField(
        default=False,
        help_text="""
            Flag set when TP is processed by celery task
            """,
        db_index=True,
    )
    steficon_rule = models.ForeignKey(
        RuleCommit,
        null=True,
        on_delete=models.PROTECT,
        related_name="target_populations",
        blank=True,
    )
    steficon_applied_date = models.DateTimeField(blank=True, null=True)
    vulnerability_score_min = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
        blank=True,
    )
    vulnerability_score_max = models.DecimalField(
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
        blank=True,
    )
    excluded_ids = models.TextField(blank=True)
    exclusion_reason = models.TextField(blank=True)

    total_households_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    total_individuals_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    child_male_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    child_female_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    adult_male_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    adult_female_count = models.PositiveIntegerField(
        blank=True,
        null=True,
    )

    # TODO: move to StorageFile
    storage_file = models.OneToOneField(StorageFile, blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def excluded_household_ids(self) -> List:
        return map_unicef_ids_to_households_unicef_ids(self.excluded_ids)

    @property
    def household_list(self) -> "QuerySet":
        if self.status == TargetPopulation.STATUS_OPEN:
            return self.households.all()
        params = {
            "target_population": self,
        }
        if self.vulnerability_score_max is not None:
            params["vulnerability_score__lte"] = self.vulnerability_score_max
        if self.vulnerability_score_min is not None:
            params["vulnerability_score__gte"] = self.vulnerability_score_min
        return Household.objects.filter(selections__in=HouseholdSelection.objects.filter(**params))

    def get_criteria_string(self) -> str:
        try:
            return self.targeting_criteria.get_criteria_string()
        except Exception:
            return ""

    @property
    def targeting_criteria_string(self) -> str:
        return Truncator(self.get_criteria_string()).chars(390, "...")

    @property
    def has_empty_criteria(self) -> bool:
        return self.targeting_criteria is None or self.targeting_criteria.rules.count() == 0

    @property
    def has_empty_ids_criteria(self) -> bool:
        return not bool(self.targeting_criteria.household_ids) and not bool(self.targeting_criteria.individual_ids)

    @property
    def allowed_steficon_rule(self) -> Union[Rule, None]:
        if not self.program:
            return None
        tp = (
            TargetPopulation.objects.filter(
                program=self.program,
                steficon_rule__isnull=False,
            )
            .filter(status__in=(TargetPopulation.STATUS_PROCESSING, TargetPopulation.STATUS_READY_FOR_CASH_ASSIST))
            .order_by("-created_at")
            .distinct()
            .first()
        )
        if tp is None:
            return None
        return tp.steficon_rule.rule

    def set_to_ready_for_cash_assist(self) -> None:
        self.status = self.STATUS_READY_FOR_CASH_ASSIST
        self.sent_to_datahub = True

    def is_finalized(self) -> bool:
        return self.status in (self.STATUS_PROCESSING, self.STATUS_READY_FOR_CASH_ASSIST)

    def is_locked(self) -> bool:
        return self.status in (
            self.STATUS_LOCKED,
            self.STATUS_STEFICON_COMPLETED,
            self.STATUS_STEFICON_ERROR,
            self.STATUS_STEFICON_RUN,
        )

    def is_open(self) -> bool:
        return self.status in (self.STATUS_OPEN,)

    def __str__(self) -> str:
        return self.name

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["name", "business_area", "program", "is_removed"],
                condition=Q(is_removed=False),
                name="target_population_unique_if_not_removed",
            )
        ]
        verbose_name = "Target Population"


class HouseholdSelection(TimeStampedUUIDModel):
    """
    M2M table between Households and TargetPopulations
    """

    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="selections",
    )
    target_population = models.ForeignKey("TargetPopulation", on_delete=models.CASCADE, related_name="selections")
    vulnerability_score = models.DecimalField(
        blank=True, null=True, decimal_places=3, max_digits=6, help_text="Written by Steficon", db_index=True
    )
    is_original = models.BooleanField(db_index=True, default=False)
    is_migration_handled = models.BooleanField(default=False)

    objects = RepresentationManager()
    original_and_repr_objects = models.Manager()

    class Meta:
        unique_together = ("household", "target_population")
        verbose_name = "Household Selection"


class TargetingCriteria(TimeStampedUUIDModel, TargetingCriteriaQueryingBase):
    """
    Class with filtering criteria flags and a set of ORed Rules. Rules are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate list).
    If flag is applied, target population needs to be filtered by it as an AND condition to the existing set of rules.
    """

    flag_exclude_if_active_adjudication_ticket = models.BooleanField(
        default=False,
        help_text=_(
            "Exclude households with individuals (members or collectors) that have active adjudication ticket(s)."
        ),
    )
    flag_exclude_if_on_sanction_list = models.BooleanField(
        default=False,
        help_text=_("Exclude households with individuals (members or collectors) on sanction list."),
    )
    household_ids = models.TextField(blank=True)
    individual_ids = models.TextField(blank=True)

    def get_rules(self) -> "QuerySet":
        return self.rules.all()

    def get_excluded_household_ids(self) -> List["UUID"]:
        return self.target_population.excluded_household_ids

    def get_query(self) -> Q:
        query = super().get_query()
        if (
            self.target_population
            and self.target_population.status != TargetPopulation.STATUS_OPEN
            and self.target_population.program is not None
        ):
            query &= Q(size__gt=0)

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


class TargetingCriteriaRule(TimeStampedUUIDModel, TargetingCriteriaRuleQueryingBase):
    """
    This is a set of ANDed Filters.
    """

    targeting_criteria = models.ForeignKey(
        "TargetingCriteria",
        related_name="rules",
        on_delete=models.CASCADE,
    )

    def get_filters(self) -> "QuerySet":
        return self.filters.all()

    def get_individuals_filters_blocks(self) -> "QuerySet":
        return self.individuals_filters_blocks.all()


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
    """
    This is one explicit filter like:
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
            return self.targeting_criteria_rule.targeting_criteria.target_population.program.is_social_worker_program
        except (
            AttributeError,
            TargetingCriteriaRuleFilter.targeting_criteria_rule.RelatedObjectDoesNotExist,
        ):
            return False

    def get_core_fields(self) -> List:
        if self.is_social_worker_program:
            return FieldFactory.from_only_scopes([Scope.TARGETING, Scope.XLSX_PEOPLE])
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_household()


class TargetingIndividualBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterBase):
    """
    This is one explicit filter like:
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

    def get_core_fields(self) -> List:
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_individual()

    def get_lookup_prefix(self, associated_with: Any) -> str:
        return ""
