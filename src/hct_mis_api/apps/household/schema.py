from typing import Any, Dict, List

from django.db.models import F, Func, OuterRef, Q, QuerySet, Subquery, Sum
from django.db.models.functions import Coalesce

import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_permission_decorator,
    get_program_id_from_headers,
    sum_lists_with_values,
)
from hct_mis_api.apps.household.filters import HouseholdFilter
from hct_mis_api.apps.household.models import (
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    Household,
    Individual,
)
from hct_mis_api.apps.household.services.household_programs_with_delivered_quantity import (
    delivered_quantity_service,
)
from hct_mis_api.apps.payment.models import Account
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.graphql import does_path_exist_in_query
from hct_mis_api.apps.utils.schema import (
    ChartDatasetNode,
    ChartDetailedDatasetsNode,
    SectionTotalNode,
)

INDIVIDUALS_CHART_LABELS = [
    "Females 0-5",
    "Females 6-11",
    "Females 12-17",
    "Females 18-59",
    "Females 60+",
    "Males 0-5",
    "Males 6-11",
    "Males 12-17",
    "Males 18-59",
    "Males 60+",
]


class ExtendedHouseHoldConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    individuals_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info: Any, **kwargs: Any) -> int:
        return root.length

    def resolve_edge_count(root, info: Any, **kwargs: Any) -> int:
        return len(root.edges)

    def resolve_individuals_count(root, info: Any, **kwargs: Any) -> int:
        return root.iterable.aggregate(sum=Sum("size")).get("sum")


class DeliveredQuantityNode(graphene.ObjectType):
    total_delivered_quantity = graphene.Decimal()
    currency = graphene.String()


class AccountsNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (hopePermissionClass(Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION),)

    name = graphene.String(required=False)
    individual_tab_data = graphene.JSONString()

    def resolve_name(self, info: Any) -> str:
        return self.account_type.label

    def resolve_individual_tab_data(self, info: Any) -> dict:
        data = dict(sorted(self.data.items()))
        if self.number:
            data["number"] = self.number
        if self.financial_institution:
            data["financial_institution"] = str(self.financial_institution.id)
        return data

    class Meta:
        model = Account
        exclude = ("unique_key", "signature_hash")
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class HouseholdNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_CREATOR),
        hopePermissionClass(Permissions.GRIEVANCES_VIEW_HOUSEHOLD_DETAILS_AS_OWNER),
        hopePermissionClass(Permissions.RDI_VIEW_DETAILS),
    )
    has_duplicates_for_rdi = graphene.Boolean(
        description="Mark household if any of individuals has Duplicate or Duplicate In Batch or Needs Adjudication"
    )
    consent_sharing = graphene.List(graphene.String)
    delivered_quantities = graphene.List(DeliveredQuantityNode)
    geopoint = graphene.String()

    @staticmethod
    def resolve_delivered_quantities(parent: Household, info: Any) -> List[Dict[str, Any]]:
        return delivered_quantity_service(parent)

    @staticmethod
    def resolve_has_duplicates_for_rdi(parent: Household, info: Any) -> bool:
        return parent.individuals.filter(
            Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            | Q(deduplication_golden_record_status__in=(DUPLICATE, NEEDS_ADJUDICATION))
        ).exists()

    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedHouseHoldConnection


class Query(graphene.ObjectType):
    all_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        filterset_class=HouseholdFilter,
        permission_classes=(
            hopeOneOfPermissionClass(
                Permissions.RDI_VIEW_DETAILS, Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST, *ALL_GRIEVANCES_CREATE_MODIFY
            ),
        ),
    )
    section_households_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_individuals_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_people_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    section_child_reached = graphene.Field(
        SectionTotalNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_people_reached_by_age_and_gender = graphene.Field(
        ChartDatasetNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_individuals_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_people_with_disability_reached_by_age = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )

    def resolve_all_households(self, info: Any, **kwargs: Any) -> QuerySet:
        user = info.context.user
        program_id = get_program_id_from_headers(info.context.headers)
        business_area_slug = info.context.headers.get("Business-Area")

        if program_id:
            program = Program.objects.filter(id=program_id).first()
            if program and program.status == Program.DRAFT:
                return Household.objects.none()

        queryset = Household.all_merge_status_objects.all()

        business_area_id = BusinessArea.objects.get(slug=business_area_slug).id
        programs_for_business_area = []

        if program_id:
            programs_for_business_area = [program_id]
        elif not program_id:
            programs_for_business_area = user.get_program_ids_for_permissions_in_business_area(
                business_area_id,
                [
                    Permissions.RDI_VIEW_DETAILS,
                    Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,
                    *ALL_GRIEVANCES_CREATE_MODIFY,
                ],
            )
        if not programs_for_business_area:
            return Household.objects.none()

        filter_q = Q()
        for program_id in programs_for_business_area:
            program_q = Q(program_id=program_id)
            areas_null_and_program_q = program_q & Q(admin1__isnull=True)
            # apply admin area limits if partner has restrictions
            area_limits = user.partner.get_area_limits_for_program(program_id)
            areas_query = (
                Q(Q(admin1__in=area_limits) | Q(admin2__in=area_limits) | Q(admin3__in=area_limits))
                if area_limits.exists()
                else Q()
            )

            filter_q |= Q(areas_null_and_program_q | Q(program_q & areas_query))

        queryset = queryset.filter(filter_q)

        if does_path_exist_in_query("edges.node.headOfHousehold", info):
            queryset = queryset.select_related("head_of_household")
        if does_path_exist_in_query("edges.node.program", info):
            queryset = queryset.select_related("program")

        if does_path_exist_in_query("edges.node.hasDuplicates", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), deduplication_golden_record_status="DUPLICATE")
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(has_duplicates_annotated=subquery)

        if does_path_exist_in_query("edges.node.sanctionListPossibleMatch", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), sanction_list_possible_match=True)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(sanction_list_possible_match_annotated=subquery)
        if does_path_exist_in_query("edges.node.sanctionListConfirmedMatch", info):
            subquery = Subquery(
                Individual.objects.filter(household_id=OuterRef("pk"), sanction_list_confirmed_match=True)
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            )
            queryset = queryset.annotate(sanction_list_confirmed_match_annotated=subquery)
        return queryset

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_households_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        return {"total": payment_items_qs.values_list("household", flat=True).distinct().count()}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_individuals_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        return Household.objects.filter(pk__in=households_ids).aggregate(total=Sum(Coalesce("size", 0)))

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_people_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        people_count = payment_items_qs.values("household").distinct().count()
        return {"total": people_count}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_section_child_reached(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict[str, int]:
        households_child_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_child_params)
        return {"total": sum(sum_lists_with_values(household_child_counts, len(households_child_params)))}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_reached_by_age_and_gender(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params)

        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_people_reached_by_age_and_gender(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]
        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()
        household_child_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params)

        return {
            "labels": INDIVIDUALS_CHART_LABELS,
            "datasets": [{"data": sum_lists_with_values(household_child_counts, len(households_params))}],
        }

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_individuals_with_disability_reached_by_age(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params_with_disability = [
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
        ]
        households_params_total = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]

        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.STANDARD.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()

        households_with_disability_counts = Household.objects.filter(pk__in=households_ids).values_list(
            *households_params_with_disability
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params_total)
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_people_with_disability_reached_by_age(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        households_params_with_disability = [
            "female_age_group_0_5_disabled_count",
            "female_age_group_6_11_disabled_count",
            "female_age_group_12_17_disabled_count",
            "female_age_group_18_59_disabled_count",
            "female_age_group_60_disabled_count",
            "male_age_group_0_5_disabled_count",
            "male_age_group_6_11_disabled_count",
            "male_age_group_12_17_disabled_count",
            "male_age_group_18_59_disabled_count",
            "male_age_group_60_disabled_count",
        ]
        households_params_total = [
            "female_age_group_0_5_count",
            "female_age_group_6_11_count",
            "female_age_group_12_17_count",
            "female_age_group_18_59_count",
            "female_age_group_60_count",
            "male_age_group_0_5_count",
            "male_age_group_6_11_count",
            "male_age_group_12_17_count",
            "male_age_group_18_59_count",
            "male_age_group_60_count",
        ]

        payment_items_qs: "QuerySet" = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        ).filter(household__collect_type=Household.CollectType.SINGLE.value)
        households_ids = payment_items_qs.values_list("household", flat=True).distinct()

        households_with_disability_counts = Household.objects.filter(pk__in=households_ids).values_list(
            *households_params_with_disability
        )
        sum_of_with_disability = sum_lists_with_values(
            households_with_disability_counts, len(households_params_with_disability)
        )

        households_totals_counts = Household.objects.filter(pk__in=households_ids).values_list(*households_params_total)
        sum_of_totals = sum_lists_with_values(households_totals_counts, len(households_params_total))

        sum_of_without_disability = []

        for i, total in enumerate(sum_of_totals):
            if not total:
                sum_of_without_disability.append(0)
            elif not sum_of_with_disability[i]:
                sum_of_without_disability.append(total)
            else:
                sum_of_without_disability.append(total - sum_of_with_disability[i])

        datasets = [
            {"label": "with disability", "data": sum_of_with_disability},
            {"label": "without disability", "data": sum_of_without_disability},
            {"label": "total", "data": sum_of_totals},
        ]
        return {"labels": INDIVIDUALS_CHART_LABELS, "datasets": datasets}
