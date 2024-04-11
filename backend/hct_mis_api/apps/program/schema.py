from typing import Any, Dict, List, Tuple, Type

from django.db.models import (
    Case,
    Count,
    DecimalField,
    Exists,
    F,
    IntegerField,
    OuterRef,
    Q,
    QuerySet,
    Sum,
    Value,
    When,
)

import graphene
from graphene import Int, relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    AdminUrlNodeMixin,
    BaseNodePermissionMixin,
    BasePermission,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopeOneOfPermissionClass,
    hopePermissionClass,
)
from hct_mis_api.apps.account.schema import (
    ProgramPartnerThroughNode,
)
from hct_mis_api.apps.core.decorators import cached_in_django_cache
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.models import DataCollectingType
from hct_mis_api.apps.core.schema import ChoiceObject, DataCollectingTypeNode
from hct_mis_api.apps.core.utils import (
    chart_filters_decoder,
    chart_map_choices,
    chart_permission_decorator,
    to_choice_object,
)
from hct_mis_api.apps.payment.filters import (
    CashPlanFilter,
    PaymentVerificationPlanFilter,
)
from hct_mis_api.apps.payment.models import (
    CashPlan,
    GenericPayment,
    PaymentVerificationPlan,
    PaymentVerificationSummary,
)
from hct_mis_api.apps.payment.schema import (
    PaymentVerificationPlanNode,
    PaymentVerificationSummaryNode,
)
from hct_mis_api.apps.payment.utils import get_payment_items_for_dashboard
from hct_mis_api.apps.program.filters import ProgramFilter
from hct_mis_api.apps.program.models import Program, ProgramPartnerThrough
from hct_mis_api.apps.utils.schema import ChartDetailedDatasetsNode


class ProgramNode(BaseNodePermissionMixin, AdminUrlNodeMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
        ),
    )

    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    total_number_of_households_with_tp_in_program = graphene.Int()
    data_collecting_type = graphene.Field(DataCollectingTypeNode, source="data_collecting_type")
    partners = graphene.List(ProgramPartnerThroughNode)

    class Meta:
        model = Program
        filter_fields = [
            "name",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_total_number_of_households(program: Program, info: Any, **kwargs: Any) -> int:
        return program.household_count

    @staticmethod
    def resolve_total_number_of_households_with_tp_in_program(program: Program, info: Any, **kwargs: Any) -> int:
        return program.households_with_tp_in_program.count()

    # @staticmethod
    # def resolve_partners(program: Program, info: Any, **kwargs: Any) -> List[Partner]:
    #     # filter Partners by program_id and program.business_area_id
    #     partners_list = []
    #     for partner in Partner.objects.all():
    #         partner.program = program
    #         if partner.get_permissions().areas_for(str(program.business_area_id), str(program.pk)) is not None:
    #             partners_list.append(partner)
    #     return partners_list
    @staticmethod
    def resolve_partners(program: Program, info: Any, **kwargs: Any) -> List[ProgramPartnerThrough]:
        return ProgramPartnerThrough.objects.filter(program=program)


class CashPlanNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes: Tuple[Type[BasePermission], ...] = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS),
    )

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    delivery_type = graphene.String()
    total_number_of_households = graphene.Int()
    currency = graphene.String(source="currency")
    total_delivered_quantity = graphene.Float()
    total_entitled_quantity = graphene.Float()
    total_undelivered_quantity = graphene.Float()
    can_create_payment_verification_plan = graphene.Boolean()
    available_payment_records_count = graphene.Int()
    verification_plans = DjangoPermissionFilterConnectionField(
        PaymentVerificationPlanNode,
        filterset_class=PaymentVerificationPlanFilter,
    )
    payment_verification_summary = graphene.Field(
        PaymentVerificationSummaryNode,
        source="get_payment_verification_summary",
    )
    unicef_id = graphene.String(source="ca_id")

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_available_payment_records_count(self, info: Any, **kwargs: Any) -> Int:
        return self.payment_items.filter(
            status__in=GenericPayment.ALLOW_CREATE_VERIFICATION, delivered_quantity__gt=0
        ).count()

    def resolve_verification_plans(self, info: Any, **kwargs: Any) -> QuerySet:
        return self.get_payment_verification_plans


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY),
        ),
    )
    chart_programmes_by_sector = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )
    chart_total_transferred_by_month = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True),
        program=graphene.String(required=False),
        administrative_area=graphene.String(required=False),
    )

    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoPermissionFilterConnectionField(
        CashPlanNode,
        filterset_class=CashPlanFilter,
        permission_classes=(
            hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_LIST),
            hopePermissionClass(
                Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS,
            ),
        ),
    )
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)
    data_collecting_type_choices = graphene.List(ChoiceObject)

    all_active_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST, Permissions.RDI_IMPORT_DATA),
        ),
    )

    def resolve_all_programs(self, info: Any, **kwargs: Any) -> QuerySet[Program]:
        if not info.context.user.is_authenticated:
            return Program.objects.none()
        filters = {
            "business_area__slug": info.context.headers.get("Business-Area").lower(),
            "data_collecting_type__deprecated": False,
            "data_collecting_type__isnull": False,
        }
        if not info.context.user.partner.is_unicef:
            filters.update({"id__in": info.context.user.partner.program_ids})
        return (
            Program.objects.filter(**filters)
            .exclude(data_collecting_type__code="unknown")
            .annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "start_date")
        )

    def resolve_program_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_program_frequency_of_payments_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE)

    def resolve_program_sector_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.SECTOR_CHOICE)

    def resolve_program_scope_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.SCOPE_CHOICE)

    def resolve_cash_plan_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_data_collecting_type_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return list(
            DataCollectingType.objects.filter(
                Q(
                    Q(
                        limit_to__slug=info.context.headers.get("Business-Area").lower(),
                    )
                    | Q(limit_to__isnull=True)
                ),
                active=True,
                deprecated=False,
            )
            .exclude(code__iexact="unknown")
            .annotate(name=F("label"))
            .annotate(value=F("code"))
            .values("name", "value")
            .order_by("name")
        )

    def resolve_all_cash_plans(self, info: Any, **kwargs: Any) -> QuerySet[CashPlan]:
        payment_verification_summary_qs = PaymentVerificationSummary.objects.filter(
            payment_plan_object_id=OuterRef("id")
        )

        return CashPlan.objects.annotate(
            custom_order=Case(
                When(
                    Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_ACTIVE)),
                    then=Value(1),
                ),
                When(
                    Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_PENDING)),
                    then=Value(2),
                ),
                When(
                    Exists(payment_verification_summary_qs.filter(status=PaymentVerificationPlan.STATUS_FINISHED)),
                    then=Value(3),
                ),
                output_field=IntegerField(),
                default=Value(0),
            ),
        ).order_by("-updated_at", "custom_order")

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_programmes_by_sector(self, info: Any, business_area_slug: str, year: int, **kwargs: Any) -> Dict:
        filters = chart_filters_decoder(kwargs)
        sector_choice_mapping = chart_map_choices(Program.SECTOR_CHOICE)
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(year, business_area_slug, filters, True)

        programs_ids = payment_items_qs.values_list("parent__program__id", flat=True)
        programs = Program.objects.filter(id__in=programs_ids).distinct()

        programmes_by_sector = (
            programs.values("sector")
            .order_by("sector")
            .annotate(total_count_without_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=False)))
            .annotate(total_count_with_cash_plus=Count("id", distinct=True, filter=Q(cash_plus=True)))
        )
        labels = []
        programmes_wo_cash_plus = []
        programmes_with_cash_plus = []
        programmes_total = []
        for programme in programmes_by_sector:
            labels.append(sector_choice_mapping.get(programme.get("sector")))
            programmes_wo_cash_plus.append(programme.get("total_count_without_cash_plus") or 0)
            programmes_with_cash_plus.append(programme.get("total_count_with_cash_plus") or 0)
            programmes_total.append(programmes_wo_cash_plus[-1] + programmes_with_cash_plus[-1])

        datasets = [
            {"label": "Programmes", "data": programmes_wo_cash_plus},
            {"label": "Programmes with Cash+", "data": programmes_with_cash_plus},
            {"label": "Total Programmes", "data": programmes_total},
        ]

        return {"labels": labels, "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    @cached_in_django_cache(24)
    def resolve_chart_total_transferred_by_month(
        self, info: Any, business_area_slug: str, year: int, **kwargs: Any
    ) -> Dict:
        payment_items_qs: QuerySet = get_payment_items_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        months_and_amounts = (
            payment_items_qs.annotate(
                delivery_month=F("delivery_date__month"),
                total_delivered_cash=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_CASH),
                    output_field=DecimalField(),
                ),
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd",
                    filter=Q(delivery_type__in=GenericPayment.DELIVERY_TYPES_IN_VOUCHER),
                    output_field=DecimalField(),
                ),
            )
            .values("delivery_month", "total_delivered_cash", "total_delivered_voucher")
            .order_by("delivery_month")
        )

        months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        previous_transfers = [0] * 12
        cash_transfers = [0] * 12
        voucher_transfers = [0] * 12

        for data_dict in months_and_amounts:
            month_index = data_dict["delivery_month"] - 1
            cash_transfers[month_index] += data_dict.get("total_delivered_cash") or 0
            voucher_transfers[month_index] += data_dict.get("total_delivered_voucher") or 0

        for index in range(1, len(months_labels)):
            previous_transfers[index] = (
                previous_transfers[index - 1] + cash_transfers[index - 1] + voucher_transfers[index - 1]
            )
        datasets = [
            {"label": "Previous Transfers", "data": previous_transfers},
            {"label": "Voucher Transferred", "data": voucher_transfers},
            {"label": "Cash Transferred", "data": cash_transfers},
        ]

        return {"labels": months_labels, "datasets": datasets}

    def resolve_all_active_programs(self, info: Any, **kwargs: Any) -> QuerySet[Program]:
        return Program.objects.filter(
            status=Program.ACTIVE,
            business_area__slug=info.context.headers.get("Business-Area").lower(),
            data_collecting_type__isnull=False,
            data_collecting_type__deprecated=False,
        ).exclude(data_collecting_type__code="unknown")
