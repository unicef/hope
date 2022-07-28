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
    Document,
    Household,
    Individual,
)
from hct_mis_api.apps.steficon.models import RuleCommit
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
            households_ids = self.candidate_list.values_list("id")
        else:
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
            "all_households": households_ids.count(),
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
                status=TargetPopulation.STATUS_PROCESSING,
            )
            .order_by("-created_at")
            .first()
        )
        if tp is None:
            return None
        return tp.steficon_rule

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


class TargetingCriteriaQueryingMixin:
    def __init__(self, rules=None, excluded_household_ids=None):
        if rules is None:
            return
        self.rules = rules
        if excluded_household_ids is None:
            self._excluded_household_ids = []
        else:
            self._excluded_household_ids = excluded_household_ids

    @property
    def excluded_household_ids(self):
        if not isinstance(self, models.Model):
            return self._excluded_household_ids
        try:
            return self.target_population_candidate.excluded_household_ids
        except TargetPopulation.DoesNotExist:
            pass

        try:
            return self.target_population_final.excluded_household_ids
        except TargetPopulation.DoesNotExist:
            pass
        return []

    def get_criteria_string(self):
        rules = self.rules if isinstance(self.rules, list) else self.rules.all()
        rules_string = [x.get_criteria_string() for x in rules]
        return " OR ".join(rules_string).strip()

    def get_basic_query(self):
        return Q(size__gt=0) & Q(withdrawn=False) & ~Q(unicef_id__in=self.excluded_household_ids)

    def get_query(self):
        query = Q()
        rules = self.rules if isinstance(self.rules, list) else self.rules.all()
        for rule in rules:
            query |= rule.get_query()
        return self.get_basic_query() & Q(query)


class TargetingCriteria(TimeStampedUUIDModel, TargetingCriteriaQueryingMixin):
    """
    This is a set of ORed Rules. These are either applied for a candidate list
    (against Golden Record) or for a final list (against the approved candidate
    list).
    """

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


class TargetingCriteriaRuleQueryingMixin:
    def __init__(self, filters=None, individuals_filters_blocks=None):
        if filters is not None:
            self.filters = filters
        if individuals_filters_blocks is not None:
            self.individuals_filters_blocks = individuals_filters_blocks

    def get_criteria_string(self):
        filters = self.filters if isinstance(self.filters, list) else self.filters.all()
        filters_strings = [x.get_criteria_string() for x in filters]
        individuals_filters_blocks = (
            self.individuals_filters_blocks
            if isinstance(self.individuals_filters_blocks, list)
            else self.individuals_filters_blocks.all()
        )
        individuals_filters_blocks_strings = [x.get_criteria_string() for x in individuals_filters_blocks]
        all_strings = []
        if len(filters_strings):
            all_strings.append(f"H({' AND '.join(filters_strings).strip()})")
        if len(individuals_filters_blocks_strings):
            all_strings.append(f"I({' AND '.join(individuals_filters_blocks_strings).strip()})")
        return " AND ".join(all_strings).strip()

    def get_query(self):
        query = Q()
        filters = self.filters if isinstance(self.filters, list) else self.filters.all()
        individuals_filters_blocks = (
            self.individuals_filters_blocks
            if isinstance(self.individuals_filters_blocks, list)
            else self.individuals_filters_blocks.all()
        )
        # Thats household filters
        for ruleFilter in filters:
            query &= ruleFilter.get_query()
        # filter individual block
        for individuals_filters_block in individuals_filters_blocks:
            query &= individuals_filters_block.get_query()
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


class TargetingIndividualRuleFilterBlockMixin:
    def __init__(self, individual_block_filters=None, target_only_hoh=None):
        if individual_block_filters is not None:
            self.individual_block_filters = individual_block_filters
        if target_only_hoh is not None:
            self.target_only_hoh = target_only_hoh

    def get_criteria_string(self):
        filters = (
            self.individual_block_filters
            if isinstance(self.individual_block_filters, list)
            else self.individual_block_filters.all()
        )
        filters_string = [x.get_criteria_string() for x in filters]
        return f"({' AND '.join(filters_string).strip()})"

    def get_basic_individual_query(self):
        return Q(household__withdrawn=False) & Q(duplicate=False) & Q(withdrawn=False)

    def get_query(self):
        individuals_query = self.get_basic_individual_query()
        filters = (
            self.individual_block_filters
            if isinstance(self.individual_block_filters, list)
            else self.individual_block_filters.all()
        )
        filtered = False
        search_query = SearchQuery("")

        for ruleFilter in filters:
            filtered = True
            if ruleFilter.field_name in ("observed_disability", "full_name"):
                for arg in ruleFilter.arguments:
                    search_query &= SearchQuery(arg)
            else:
                individuals_query &= ruleFilter.get_query()
        if not filtered:
            return Q()
        if self.target_only_hoh:
            # only filtering against heads of household
            individuals_query &= Q(heading_household__isnull=False)

        individual_query = Individual.objects
        if isinstance(search_query, CombinedSearchQuery):
            q = individual_query.filter(vector_column=search_query).filter(individuals_query)
        else:
            q = individual_query.filter(individuals_query)

        households_id = q.values_list("household_id", flat=True)
        return Q(id__in=households_id)


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


class TargetingCriteriaFilterMixin:
    COMPARISION_ATTRIBUTES = {
        "EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": False,
            "supported_types": ["INTEGER", "SELECT_ONE", "STRING", "BOOL"],
        },
        "NOT_EQUALS": {
            "arguments": 1,
            "lookup": "",
            "negative": True,
            "supported_types": ["INTEGER", "SELECT_ONE"],
        },
        "CONTAINS": {
            "min_arguments": 1,
            "arguments": 1,
            "lookup": "__icontains",
            "negative": False,
            "supported_types": ["SELECT_MANY", "STRING"],
        },
        "NOT_CONTAINS": {
            "arguments": 1,
            "lookup": "__icontains",
            "negative": True,
            "supported_types": ["STRING"],
        },
        "RANGE": {
            "arguments": 2,
            "lookup": "__range",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL", "DATE"],
        },
        "NOT_IN_RANGE": {
            "arguments": 2,
            "lookup": "__range",
            "negative": True,
            "supported_types": ["INTEGER", "DECIMAL"],
        },
        "GREATER_THAN": {
            "arguments": 1,
            "lookup": "__gte",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL"],
        },
        "LESS_THAN": {
            "arguments": 1,
            "lookup": "__lte",
            "negative": False,
            "supported_types": ["INTEGER", "DECIMAL"],
        },
    }

    COMPARISON_CHOICES = Choices(
        ("EQUALS", _("Equals")),
        ("NOT_EQUALS", _("Not Equals")),
        ("CONTAINS", _("Contains")),
        ("NOT_CONTAINS", _("Does not contain")),
        ("RANGE", _("In between <>")),
        ("NOT_IN_RANGE", _("Not in between <>")),
        ("GREATER_THAN", _("Greater than")),
        ("LESS_THAN", _("Less than")),
    )

    def get_criteria_string(self):
        return f"{{{self.field_name} {self.comparision_method} ({','.join([str(x) for x in self.arguments])})}}"

    def get_lookup_prefix(self, associated_with):
        return "individuals__" if associated_with == _INDIVIDUAL else ""

    def prepare_arguments(self, arguments, field_attr):
        is_flex_field = get_attr_value("is_flex_field", field_attr, False)
        if not is_flex_field:
            return arguments
        type = get_attr_value("type", field_attr, None)
        if type == TYPE_DECIMAL:
            return [float(arg) for arg in arguments]
        if type == TYPE_INTEGER:
            return [int(arg) for arg in arguments]
        return arguments

    def get_query_for_lookup(
        self,
        lookup,
        field_attr,
    ):
        select_many = get_attr_value("type", field_attr, None) == TYPE_SELECT_MANY
        comparision_attribute = TargetingCriteriaRuleFilter.COMPARISION_ATTRIBUTES.get(self.comparision_method)
        args_count = comparision_attribute.get("arguments")
        if self.arguments is None:
            logger.error(f"{self.field_name} {self.comparision_method} filter query expect {args_count} " f"arguments")
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} " f"arguments"
            )
        args_input_count = len(self.arguments)
        if select_many:
            if args_input_count < 1:
                logger.error(f"{self.field_name} SELECT MULTIPLE CONTAINS filter query expect at least 1 argument")
                raise ValidationError(
                    f"{self.field_name} SELECT MULTIPLE CONTAINS filter query expect at least 1 argument"
                )
        elif args_count != args_input_count:
            logger.error(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
            raise ValidationError(
                f"{self.field_name} {self.comparision_method} filter query expect {args_count} "
                f"arguments gets {args_input_count}"
            )
        arguments = self.prepare_arguments(self.arguments, field_attr)
        argument = arguments if args_input_count > 1 else arguments[0]
        if select_many:
            if isinstance(argument, list):
                query = Q()
                for arg in argument:
                    # This regular expression can found the only exact word
                    query &= Q(**{f"{lookup}__icontains": arg})
            else:
                query = Q(**{f"{lookup}__contains": argument})
        else:
            query = Q(**{f"{lookup}{comparision_attribute.get('lookup')}": argument})
        if comparision_attribute.get("negative"):
            return ~query
        return query

    def get_query_for_core_field(self):
        core_fields = self.get_core_fields()
        core_field_attrs = [attr for attr in core_fields if attr.get("name") == self.field_name]
        if len(core_field_attrs) != 1:
            logger.error(f"There are no Core Field Attributes associated with this fieldName {self.field_name}")
            raise ValidationError(
                f"There are no Core Field Attributes associated with this fieldName {self.field_name}"
            )
        core_field_attr = core_field_attrs[0]
        get_query = core_field_attr.get("get_query")
        if get_query:
            return get_query(self.comparision_method, self.arguments)
        lookup = core_field_attr.get("lookup")
        if not lookup:
            logger.error(
                f"Core Field Attributes associated with this fieldName {self.field_name}"
                " doesn't have get_query method or lookup field"
            )
            raise ValidationError(
                f"Core Field Attributes associated with this fieldName {self.field_name}"
                " doesn't have get_query method or lookup field"
            )
        lookup_prefix = self.get_lookup_prefix(core_field_attr["associated_with"])
        return self.get_query_for_lookup(f"{lookup_prefix}{lookup}", core_field_attr)

    def get_query_for_flex_field(self):
        flex_field_attr = FlexibleAttribute.objects.get(name=self.field_name)
        if not flex_field_attr:
            logger.error(f"There are no Flex Field Attributes associated with this fieldName {self.field_name}")
            raise ValidationError(
                f"There are no Flex Field Attributes associated with this fieldName {self.field_name}"
            )
        lookup_prefix = self.get_lookup_prefix(_INDIVIDUAL if flex_field_attr.associated_with == 1 else _HOUSEHOLD)
        lookup = f"{lookup_prefix}flex_fields__{flex_field_attr.name}"
        return self.get_query_for_lookup(lookup, flex_field_attr)

    def get_query(self):
        if not self.is_flex_field:
            return self.get_query_for_core_field()
        return self.get_query_for_flex_field()

    def __str__(self):
        return f"{self.field_name} {self.comparision_method} {self.arguments}"


# TODO It should be household only
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
