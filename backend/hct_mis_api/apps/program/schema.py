import graphene
from django.db.models import Case, When, Value, IntegerField, Q, Sum
from django.db.models.functions import Coalesce
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
    MultipleChoiceFilter,
    ModelMultipleChoiceFilter,
    DateFilter,
)
from graphene import relay, ConnectionField
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
)
from account.schema import LogEntryObjectConnection
from core.extended_connection import ExtendedConnection
from core.filters import IntegerRangeFilter, DecimalRangeFilter
from core.schema import ChoiceObject
from core.utils import to_choice_object
from payment.models import CashPlanPaymentVerification
from program.models import Program, CashPlan


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

    order_by = OrderingFilter(
        fields=("name", "status", "start_date", "end_date", "sector", "households_count", "budget")
    )

    def search_filter(self, qs, name, value):
        values = value.split(" ")
        q_obj = Q()
        for value in values:
            q_obj |= Q(name__icontains=value)
        return qs.filter(q_obj)


class ProgramNode(BaseNodePermissionMixin, DjangoObjectType):
    # TODO Enable permissions below
    # permission_classes = (hopePermissionClass(f"{PERMISSION_PROGRAM}.{PERMISSION_READ}"),)
    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    history = ConnectionField(LogEntryObjectConnection)
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

    class Meta:
        fields = {
            "program": ["exact"],
            "verification_status": ["exact"],
            "assistance_through": ["exact", "icontains"],
            "delivery_type": ["exact"],
            "start_date": ["exact", "lte", "gte"],
            "end_date": ["exact", "lte", "gte"],
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


class CashPlanNode(DjangoObjectType):
    bank_reconciliation_success = graphene.Int()
    bank_reconciliation_error = graphene.Int()

    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoPermissionFilterConnectionField(
        ProgramNode,
        filterset_class=ProgramFilter,
        # TODO Enable permissions below
        # permission_classes=(hopePermissionClass("PERMISSION_PROGRAM.LIST"),)
    )
    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoFilterConnectionField(CashPlanNode, filterset_class=CashPlanFilter)
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
        ).order_by("custom_order")
