import graphene
from django.db.models import Case, When, Value, IntegerField, Q
from graphene import relay, ConnectionField
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ChoiceObject, LogEntryObjectConnection
from core.extended_connection import ExtendedConnection
from core.utils import to_choice_object
from program.models import Program, CashPlan
from django_filters import FilterSet, OrderingFilter, CharFilter


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = ("id", "status")
        model = Program


class ProgramNode(DjangoObjectType):
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
    all_programs = DjangoFilterConnectionField(ProgramNode, filterset_class=ProgramFilter)
    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoFilterConnectionField(CashPlanNode, filterset_class=CashPlanFilter)
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)

    def resolve_all_programs(self, info, **kwargs):
        return Program.objects.annotate(
            custom_order=Case(
                When(status=Program.DRAFT, then=Value(1)),
                When(status=Program.ACTIVE, then=Value(2)),
                When(status=Program.FINISHED, then=Value(3)),
                output_field=IntegerField(),
            )
        ).order_by("custom_order")

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
