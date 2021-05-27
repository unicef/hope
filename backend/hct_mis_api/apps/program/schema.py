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
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    hopePermissionClass,
    Permissions,
    hopeOneOfPermissionClass,
    ALL_GRIEVANCES_CREATE_MODIFY,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.filters import DecimalRangeFilter, IntegerRangeFilter
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    to_choice_object,
    CustomOrderingFilter,
    chart_map_choices,
    chart_permission_decorator,
    chart_filters_decoder,
)
from hct_mis_api.apps.payment.models import CashPlanPaymentVerification, PaymentRecord
from hct_mis_api.apps.payment.utils import get_payment_records_for_dashboard
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
        fields = ("id",)
        model = Program

    order_by = CustomOrderingFilter(
        fields=(Lower("name"), "status", "start_date", "end_date", "sector", "total_hh_count", "budget")
    )

    @property
    def qs(self):
        return super().qs.annotate(
            total_hh_count=Count(
                "cash_plans__payment_records__household",
                filter=Q(cash_plans__payment_records__delivered_quantity__gte=0),
                distinct=True,
            )
        )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__startswith=value)
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
            "assistance_through": ["exact", "startswith"],
            "service_provider__full_name": ["exact", "startswith"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
        }
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "ca_id",
            "status",
            "total_number_of_hh",
            "total_entitled_quantity",
            "verification_status",
            "total_persons_covered",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_date",
            "assistance_measurement",
            "assistance_through",
            "delivery_type",
            "start_date",
            "end_date",
            "program__name",
            "id",
            "updated_at",
            "service_provider__full_name",
        )
    )

    @property
    def qs(self):
        return super().qs.annotate(total_number_of_hh=Count("payment_records"))

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(id__startswith=value)
            q_obj |= Q(ca_id__startswith=value)
        return qs.filter(q_obj)


class CashPlanNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(Permissions.PAYMENT_VERIFICATION_VIEW_DETAILS),
        hopePermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS),
    )

    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()
    delivery_type = graphene.String()
    total_number_of_households = graphene.Int()
    currency = graphene.String(source="currency")

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households


class ChartProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug", required=True)

    class Meta:
        fields = ("id",)
        model = Program

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(first_name__startswith=value)
            q_obj |= Q(last_name__startswith=value)
            q_obj |= Q(email__startswith=value)
        return qs.filter(q_obj)


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        permission_classes=(
            hopeOneOfPermissionClass(Permissions.PRORGRAMME_VIEW_LIST_AND_DETAILS, *ALL_GRIEVANCES_CREATE_MODIFY),
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
        filters = chart_filters_decoder(kwargs)
        sector_choice_mapping = chart_map_choices(Program.SECTOR_CHOICE)
        valid_payment_records = get_payment_records_for_dashboard(year, business_area_slug, filters, True)
        programs = Program.objects.filter(cash_plans__payment_records__in=valid_payment_records).distinct()

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
    def resolve_chart_total_transferred_by_month(self, info, business_area_slug, year, **kwargs):
        payment_records = get_payment_records_for_dashboard(
            year, business_area_slug, chart_filters_decoder(kwargs), True
        )

        months_and_amounts = (
            payment_records.values("delivery_date__month")
            .order_by("delivery_date__month")
            .annotate(
                total_delivered_cash=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_CASH)
                )
            )
            .annotate(
                total_delivered_voucher=Sum(
                    "delivered_quantity_usd", filter=Q(delivery_type__in=PaymentRecord.DELIVERY_TYPES_IN_VOUCHER)
                )
            )
        )
        months_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        previous_transfers = [0] * 12
        cash_transfers = [0] * 12
        voucher_transfers = [0] * 12

        for data_dict in months_and_amounts:
            month_index = data_dict.get("delivery_date__month") - 1
            cash_transfers[month_index] = data_dict.get("total_delivered_cash") or 0
            voucher_transfers[month_index] = data_dict.get("total_delivered_voucher") or 0

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
