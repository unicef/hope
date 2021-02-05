import graphene
from django.db.models import Case, IntegerField, Q, Sum, Value, When, Count
from django.db.models.functions import Coalesce, Lower
from django_filters import (
    CharFilter,
    DateFilter,
    FilterSet,
    MultipleChoiceFilter,
    OrderingFilter,
)
from graphene import ConnectionField, relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    hopePermissionClass,
    Permissions,
)

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import DecimalRangeFilter, IntegerRangeFilter
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object, CustomOrderingFilter, chart_map_choices, chart_get_filtered_qs, chart_permission_decorator
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentRecord
from hct_mis_api.apps.program.models import CashPlan, Program
from hct_mis_api.apps.utils.schema import ChartDetailedDatasetsNode


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)
    search = CharFilter(method="search_filter")
    status = MultipleChoiceFilter(field_name="status", choices=Program.STATUS_CHOICE)
    sector = MultipleChoiceFilter(field_name="sector", choices=Program.SECTOR_CHOICE)
    number_of_households = IntegerRangeFilter(field_name="households_count")
    budget = DecimalRangeFilter(field_name="budget")
    start_date = DateFilter(field_name="start_date", lookup_expr="gte")
    end_date = DateFilter(field_name="end_date", lookup_expr="lte")

    class Meta:
        fields = (
            "business_area",
            "search",
            "status",
            "sector",
            "number_of_households",
            "budget",
            "start_date",
            "end_date",
        )
        model = Program

    order_by = CustomOrderingFilter(
        fields=(Lower("name"), "status", "start_date", "end_date", "sector", "households_count", "budget")
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__icontains=value)
        return qs.filter(q_obj)


class ProgramNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
        ),
    )

    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    individual_data_needed = graphene.Boolean()

    class Meta:
        model = Program
        filter_fields = [
            "name",
        ]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_history(self, info):
        return self.history.all()

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households


class CashPlanFilter(FilterSet):
    search = CharFilter(method="search_filter")
    delivery_type = MultipleChoiceFilter(field_name="delivery_type", choices=PaymentRecord.DELIVERY_TYPE_CHOICE)
    verification_status = MultipleChoiceFilter(
        field_name="verification_status", choices=CashPlanPaymentVerification.STATUS_CHOICES
    )
    business_area = CharFilter(
        field_name="business_area__slug",
    )

    class Meta:
        fields = {
            "program": ["exact"],
            "assistance_through": ["exact", "icontains"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
            "business_area": ["exact"],
        }
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "ca_id",
            "status",
            "verification_status",
            "total_persons_covered",
            "total_delivered_quantity",
            "assistance_measurement",
            "assistance_through",
            "delivery_type",
            "start_date",
            "end_date",
            "program__name",
            "id",
        )
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__icontains=value)
            q_obj |= Q(ca_id__icontains=value)
        return qs.filter(q_obj)


class CashPlanNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    )

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ChartProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)

    class Meta:
        fields = (
            "business_area",
        )
        model = Program

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__icontains=value)
            q_obj |= Q(last_name__icontains=value)
            q_obj |= Q(email__icontains=value)
        return qs.filter(q_obj)


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopePermissionClass(
                Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
            ),
        ),
    )
    chart_programmes_by_sector = graphene.Field(
        ChartDetailedDatasetsNode,
        # ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )
    chart_planned_budget = graphene.Field(
        ChartDetailedDatasetsNode,
        business_area_slug=graphene.String(required=True),
        year=graphene.Int(required=True)
    )

    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoPermissionFilterConnectionField(
        CashPlanNode,
        filterset_class=CashPlanFilter,
        permission_classes=(
            hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_LIST),
            hopePermissionClass(
                Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS,
            ),
        ),
    )
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)

    def resolve_all_programs(self, info, **kwargs):
        return (
            Program.objects.annotate(
                custom_order=Case(
                    When(status=Program.DRAFT, then=Value(1)),
                    When(status=Program.ACTIVE, then=Value(2)),
                    When(status=Program.FINISHED, then=Value(3)),
                    output_field=IntegerField(),
                )
            )
            .annotate(households_count=Coalesce(Sum("cash_plans__total_persons_covered"), 0))
            .order_by("custom_order", "start_date")
        )

    def resolve_program_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_program_frequency_of_payments_choices(self, info, **kwargs):
        return to_choice_object(Program.FREQUENCY_OF_PAYMENTS_CHOICE)

    def resolve_program_sector_choices(self, info, **kwargs):
        return to_choice_object(Program.SECTOR_CHOICE)

    def resolve_program_scope_choices(self, info, **kwargs):
        return to_choice_object(Program.SCOPE_CHOICE)

    def resolve_cash_plan_status_choices(self, info, **kwargs):
        return to_choice_object(Program.STATUS_CHOICE)

    def resolve_all_cash_plans(self, info, **kwargs):
        return CashPlan.objects.annotate(
            custom_order=Case(
                When(verification_status=CashPlanPaymentVerification.STATUS_ACTIVE, then=Value(1)),
                When(verification_status=CashPlanPaymentVerification.STATUS_PENDING, then=Value(2)),
                When(verification_status=CashPlanPaymentVerification.STATUS_FINISHED, then=Value(3)),
                output_field=IntegerField(),
            )
        ).order_by("-updated_at", "custom_order")

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_programmes_by_sector(self, info, business_area_slug, year, **kwargs):
        sector_choice_mapping = chart_map_choices(Program.SECTOR_CHOICE)
        programs = chart_get_filtered_qs(
            Program,
            year,
            business_area_slug_filter={'business_area__slug': business_area_slug}
        )
        datasets = [
            {
                "label": "Programmes",
                "data": [programs.filter(sector=sector, cash_plus=False).count()
                         for sector in sector_choice_mapping.keys()]
            },
            {
                "label": "Programmes with Cash+",
                "data": [programs.filter(sector=sector, cash_plus=True).count()
                         for sector in sector_choice_mapping.keys()]
            },
        ]
        return {"labels": sector_choice_mapping.values(), "datasets": datasets}

    @chart_permission_decorator(permissions=[Permissions.DASHBOARD_VIEW_COUNTRY])
    def resolve_chart_planned_budget(self, info, business_area_slug, year, **kwargs):
        programs = chart_get_filtered_qs(
            Program,
            year,
            business_area_slug_filter={'business_area__slug': business_area_slug},
            additional_filters={'start_date__year': year, "end_date__year": year}
        ).prefetch_related('cash_plans__payment_records')

        previous_transfers_data = [0] * 12
        cash_transfers_data = [0] * 12
        previous_sum = 0
        for month in range(1, 13):
            payment_records_by_delivery_month = programs.filter(
                cash_plans__payment_records__status=PaymentRecord.STATUS_SUCCESS,
                cash_plans__payment_records__delivery_date__year=year,
                cash_plans__payment_records__delivery_date__month=month
            ).values_list(
                "cash_plans__payment_records__delivered_quantity",
                flat=True
            ).distinct()
            for quantity_delivered in payment_records_by_delivery_month:
                cash_transfers_data[month - 1] += quantity_delivered
                previous_sum += quantity_delivered
            previous_transfers_data[month - 1] = previous_sum
        labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        datasets = [
            {
                "label": "Previous Transfers",
                "data": previous_transfers_data
            },
            {
                "label": "Cash Assistance",
                "data": cash_transfers_data
            },
        ]

        return {"labels": labels, "datasets": datasets}
