from django.utils import timezone
import logging

from django.conf import settings
from django.contrib.postgres.fields import CICharField, IntegerRangeField
from django.contrib.postgres.search import CombinedSearchQuery, SearchQuery
from django.contrib.postgres.validators import (
    RangeMaxValueValidator,
    RangeMinValueValidator,
)
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
    ProhibitNullCharactersValidator,
)
from django.db import models
from django.db.models import Case, Count, JSONField, Q, Value, When
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from dateutil.relativedelta import relativedelta
from model_utils import Choices
from model_utils.managers import SoftDeletableManager
from model_utils.models import SoftDeletableModel
from psycopg2.extras import NumericRange

from hct_mis_api.apps.activity_log.utils import create_mapping_dict
from hct_mis_api.apps.core.core_fields_attributes import (
    _HOUSEHOLD,
    _INDIVIDUAL,
    TYPE_DECIMAL,
    TYPE_INTEGER,
    TYPE_SELECT_MANY,
    FieldFactory,
    Scope,
)
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.utils import (
    get_attr_value,
    map_unicef_ids_to_households_unicef_ids,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    MALE,
    Household,
    Individual,
)
from hct_mis_api.apps.steficon.models import RuleCommit
from hct_mis_api.apps.targeting.services.targeting_service import (
    TargetingCriteriaQueryingMixin,
    TargetingCriteriaRuleQueryingMixin,
    TargetingIndividualRuleFilterBlockMixin,
    TargetingCriteriaFilterMixin,
)
from hct_mis_api.apps.utils.models import ConcurrencyModel, TimeStampedUUIDModel
from hct_mis_api.apps.utils.validators import (
    DoubleSpaceValidator,
    StartEndSpaceValidator,
)

logger = logging.getLogger(__name__)

_MAX_LEN = 256
_MIN_RANGE = 1
_MAX_RANGE = 200


def get_serialized_range(min_range=None, max_range=None):
    return NumericRange(min_range or _MIN_RANGE, max_range or _MAX_RANGE)


def get_integer_range(min_range=None, max_range=None):
    """Numeric Range support for saving as InterRangeField."""
    min_range = min_range or _MIN_RANGE
    max_range = max_range or _MAX_RANGE
    return IntegerRangeField(
        default=get_serialized_range,
        blank=True,
        validators=[
            RangeMinValueValidator(min_range),
            RangeMaxValueValidator(max_range),
        ],
    )


class TargetPopulationManager(SoftDeletableManager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                number_of_households=Case(
                    When(
                        status=TargetPopulation.STATUS_LOCKED,
                        then="candidate_list_total_households",
                    ),
                    When(
                        status=TargetPopulation.STATUS_READY_FOR_CASH_ASSIST,
                        then="final_list_total_households",
                    ),
                    default=Value(0),
                )
            )
        )


class TargetPopulation(SoftDeletableModel, TimeStampedUUIDModel, ConcurrencyModel):
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
            "candidate_list_total_households",
            "candidate_list_total_individuals",
            "final_list_total_households",
            "final_list_total_individuals",
            "selection_computation_metadata",
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

    STATUS_DRAFT = "DRAFT"
    STATUS_LOCKED = "LOCKED"
    STATUS_PROCESSING = "PROCESSING"
    STATUS_STEFICON_WAIT = "STEFICON_WAIT"
    STATUS_STEFICON_RUN = "STEFICON_RUN"
    STATUS_STEFICON_COMPLETED = "STEFICON_COMPLETED"
    STATUS_STEFICON_ERROR = "STEFICON_ERROR"
    STATUS_READY_FOR_CASH_ASSIST = "READY_FOR_CASH_ASSIST"

    STATUS_CHOICES = (
        (STATUS_DRAFT, _("Open")),
        (STATUS_LOCKED, _("Locked")),
        (STATUS_STEFICON_WAIT, _("Waiting for Rule Engine")),
        (STATUS_STEFICON_RUN, _("Rule Engine Running")),
        (STATUS_STEFICON_COMPLETED, _("Rule Engine Completed")),
        (STATUS_STEFICON_ERROR, _("Rule Engine Errored")),
        (STATUS_PROCESSING, _("Processing")),
        (STATUS_READY_FOR_CASH_ASSIST, _("Ready for cash assist")),
    )

    objects = TargetPopulationManager()

    name = CICharField(
        unique=True,
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
        related_name="locked_target_populations",
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
    status = models.CharField(max_length=_MAX_LEN, choices=STATUS_CHOICES, default=STATUS_DRAFT, db_index=True)
    households = models.ManyToManyField(
        "household.Household",
        related_name="target_populations",
        through="HouseholdSelection",
    )
    candidate_list_total_households = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    candidate_list_total_individuals = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    final_list_total_households = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    final_list_total_individuals = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    selection_computation_metadata = models.TextField(
        blank=True,
        null=True,
        help_text="""This would be the metadata written to by say Corticon on how
        it arrived at the selection it made.""",
    )
    program = models.ForeignKey(
        "program.Program",
        blank=True,
        null=True,
        help_text="""Set only when the target population moves from draft to
            candidate list frozen state (approved)""",
        on_delete=models.SET_NULL,
    )
    candidate_list_targeting_criteria = models.OneToOneField(
        "TargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="target_population_candidate",
    )
    final_list_targeting_criteria = models.OneToOneField(
        "TargetingCriteria",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="target_population_final",
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

    @property
    def excluded_household_ids(self):
        excluded_household_ids_array = map_unicef_ids_to_households_unicef_ids(self.excluded_ids)
        return excluded_household_ids_array

    @property
    def vulnerability_score_filtered_households(self):
        queryset = self.households
        if self.vulnerability_score_max is not None:
            queryset = queryset.filter(selections__vulnerability_score__lte=self.vulnerability_score_max)
        if self.vulnerability_score_min is not None:
            queryset = queryset.filter(selections__vulnerability_score__gte=self.vulnerability_score_min)

        queryset = queryset.filter(~Q(unicef_id__in=self.excluded_household_ids))
        return queryset.distinct()

    @property
    def candidate_list(self):
        if self.status != TargetPopulation.STATUS_DRAFT:
            return []
        household_queryset = Household.objects
        return household_queryset.filter(self.candidate_list_targeting_criteria.get_query()).filter(
            business_area=self.business_area
        )

    @property
    def final_list(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            return []
        return (
            self.vulnerability_score_filtered_households.filter(selections__final=True)
            .order_by("created_at")
            .distinct()
        )

    @property
    def candidate_stats(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            households_ids = list(self.candidate_list.values_list("id", flat=True))
        else:
            # TODO nie lamić
            households_ids = self.vulnerability_score_filtered_households.values_list("id")
        delta18 = relativedelta(years=+18)
        date18ago = timezone.now() - delta18
        targeted_individuals = Individual.objects.filter(household__id__in=households_ids).aggregate(
            child_male=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
            child_female=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
            adult_male=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
            adult_female=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
        )
        return {
            "child_male": targeted_individuals.get("child_male"),
            "child_female": targeted_individuals.get("child_female"),
            "adult_male": targeted_individuals.get("adult_male"),
            "adult_female": targeted_individuals.get("adult_female"),
            "all_households": len(households_ids),
            "all_individuals": targeted_individuals.get("child_male")
            + targeted_individuals.get("child_female")
            + targeted_individuals.get("adult_male")
            + targeted_individuals.get("adult_female"),
        }

    def get_criteria_string(self):
        try:
            return self.candidate_list_targeting_criteria.get_criteria_string()
        except:
            return ""

    @property
    def targeting_criteria_string(self):
        return Truncator(self.get_criteria_string()).chars(390, "...")

    @property
    def final_stats(self):
        if self.status == TargetPopulation.STATUS_DRAFT:
            return None
        elif self.status == TargetPopulation.STATUS_LOCKED:
            households_ids = (
                self.vulnerability_score_filtered_households.filter(self.final_list_targeting_criteria.get_query())
                .filter(business_area=self.business_area)
                .values_list("id")
                .distinct()
            )
        else:
            households_ids = self.final_list.values_list("id").distinct()
        delta18 = relativedelta(years=+18)
        date18ago = timezone.now() - delta18

        targeted_individuals = Individual.objects.filter(household__id__in=households_ids).aggregate(
            child_male=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=MALE)),
            child_female=Count("id", distinct=True, filter=Q(birth_date__gt=date18ago, sex=FEMALE)),
            adult_male=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=MALE)),
            adult_female=Count("id", distinct=True, filter=Q(birth_date__lte=date18ago, sex=FEMALE)),
        )

        return {
            "child_male": targeted_individuals.get("child_male"),
            "child_female": targeted_individuals.get("child_female"),
            "adult_male": targeted_individuals.get("adult_male"),
            "adult_female": targeted_individuals.get("adult_female"),
        }

    @property
    def allowed_steficon_rule(self):
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

    def set_to_ready_for_cash_assist(self):
        self.status = self.STATUS_READY_FOR_CASH_ASSIST
        self.sent_to_datahub = True

    def is_finalized(self):
        return self.status in (self.STATUS_PROCESSING, self.STATUS_READY_FOR_CASH_ASSIST)

    def is_locked(self):
        return self.status == self.STATUS_LOCKED

    def is_approved(self):
        return self.status in (self.STATUS_LOCKED, self.STATUS_STEFICON_COMPLETED)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "business_area")
        verbose_name = "Target Population"


class HouseholdSelection(TimeStampedUUIDModel):
    """
    This model contains metadata associated with the relation between a target
    population and a household. Its understood that once the candidate list of
    households has been frozen, some external system (eg. Corticon) will run
    to calculate vulnerability score. The user (may) filter again then against
    the approved candidate list and mark the households as having been
    'selected' or not (final=True/False). By default a draft list or frozen
    candidate list  will have final set to True.
    """

    household = models.ForeignKey(
        "household.Household",
        on_delete=models.CASCADE,
        related_name="selections",
    )
    target_population = models.ForeignKey("TargetPopulation", on_delete=models.CASCADE, related_name="selections")
    vulnerability_score = models.DecimalField(
        blank=True,
        null=True,
        decimal_places=3,
        max_digits=6,
        help_text="Written by a tool such as Corticon.",
    )
    final = models.BooleanField(
        default=True,
        help_text="""
            When set to True, this means the household has been selected from
            the candidate list. Only these households will be sent to
            CashAssist when a sync is run for the associated target population.
            """,
    )


class TargetingCriteria(TimeStampedUUIDModel, TargetingCriteriaQueryingMixin):
    """
    This is a set of ORed Rules. These are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate
    list).
    """

    def get_rules(self):
        return self.rules.all()

    def get_excluded_household_ids(self):
        try:
            return self.target_population_candidate.excluded_household_ids
        except TargetPopulation.DoesNotExist:
            pass

        try:
            return self.target_population_final.excluded_household_ids
        except TargetPopulation.DoesNotExist:
            pass
        return []

    def get_query(self):
        query = super().get_query()
        try:
            if (
                self.target_population_final
                and self.target_population_final.status != TargetPopulation.STATUS_DRAFT
                and self.target_population_final.program is not None
                and self.target_population_final.program.individual_data_needed
            ):
                query &= Q(size__gt=0)
        except TargetPopulation.DoesNotExist:
            pass
        return query


class TargetingCriteriaRule(TimeStampedUUIDModel, TargetingCriteriaRuleQueryingMixin):
    """
    This is a set of ANDed Filters.
    """

    targeting_criteria = models.ForeignKey(
        "TargetingCriteria",
        related_name="rules",
        on_delete=models.CASCADE,
    )

    def get_filters(self):
        return self.filters.all()

    def get_individuals_filters_blocks(self):
        return self.individuals_filters_blocks.all()


class TargetingIndividualRuleFilterBlock(
    TimeStampedUUIDModel,
    TargetingIndividualRuleFilterBlockMixin,
):
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule",
        on_delete=models.CASCADE,
        related_name="individuals_filters_blocks",
    )
    target_only_hoh = models.BooleanField(default=False)

    def get_individual_block_filters(self):
        return self.individual_block_filters.all()


class TargetingCriteriaRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterMixin):
    """
    This is one explicit filter like:
        :Age <> 10-20
        :Residential Status = Refugee
        :Residential Status != Refugee
    """

    def get_core_fields(self):
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_household()

    comparision_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterMixin.COMPARISON_CHOICES,
    )
    targeting_criteria_rule = models.ForeignKey(
        "TargetingCriteriaRule",
        related_name="filters",
        on_delete=models.CASCADE,
    )
    is_flex_field = models.BooleanField(default=False)
    field_name = models.CharField(max_length=50)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )


class TargetingIndividualBlockRuleFilter(TimeStampedUUIDModel, TargetingCriteriaFilterMixin):
    """
    This is one explicit filter like:
        :Age <> 10-20
        :Residential Status = Refugee
        :Residential Status != Refugee
    """

    def get_core_fields(self):
        return FieldFactory.from_scope(Scope.TARGETING).associated_with_individual()

    comparision_method = models.CharField(
        max_length=20,
        choices=TargetingCriteriaFilterMixin.COMPARISON_CHOICES,
    )
    individuals_filters_block = models.ForeignKey(
        "TargetingIndividualRuleFilterBlock",
        related_name="individual_block_filters",
        on_delete=models.CASCADE,
    )
    is_flex_field = models.BooleanField(default=False)
    field_name = models.CharField(max_length=50)
    arguments = JSONField(
        help_text="""
            Array of arguments
            """
    )

    def get_lookup_prefix(self, associated_with):
        return ""
