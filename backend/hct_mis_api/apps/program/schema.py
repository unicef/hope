import graphene
from django.db.models import Case, When, Value, IntegerField
from graphene import relay, ConnectionField, Connection
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from core.schema import ExtendedConnection, ChoiceObject, LogEntryObject, LogEntryObjectConnection
from program.models import Program, CashPlan
from django_filters import FilterSet, OrderingFilter, CharFilter


class ProgramFilter(FilterSet):
    business_area = CharFilter(field_name="business_area__slug")

    class Meta:
        fields = ("id",)
        model = Program


class ProgramNode(DjangoObjectType):
    budget = graphene.Decimal()
    total_entitled_quantity = graphene.Decimal()
    total_delivered_quantity = graphene.Decimal()
    total_undelivered_quantity = graphene.Decimal()
    total_number_of_households = graphene.Int()
    history = ConnectionField(LogEntryObjectConnection)

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
    class Meta:
        fields = ("program",)
        model = CashPlan

    order_by = OrderingFilter(
        fields=(
            "cash_assist_id",
            "status",
            "number_of_households",
            "currency",
            "total_entitled_quantity",
            "total_delivered_quantity",
            "total_undelivered_quantity",
            "dispersion_date",
        )
    )


class CashPlanNode(DjangoObjectType):
    class Meta:
        model = CashPlan
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoFilterConnectionField(
        ProgramNode, filterset_class=ProgramFilter
    )
    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoFilterConnectionField(
        CashPlanNode, filterset_class=CashPlanFilter
    )
    program_status_choices = graphene.List(ChoiceObject)
    program_frequency_of_payments_choices = graphene.List(ChoiceObject)
    program_sector_choices = graphene.List(ChoiceObject)
    program_scope_choices = graphene.List(ChoiceObject)
    cash_plan_status_choices = graphene.List(ChoiceObject)

    def resolve_all_programs(self, info, **kwardgs):
        return Program.objects.annotate(
            custom_order=Case(
                When(status=Program.DRAFT, then=Value(1)),
                When(status=Program.ACTIVE, then=Value(2)),
                When(status=Program.FINISHED, then=Value(3)),
                output_field=IntegerField(),
            )
        ).order_by("custom_order")

    def resolve_program_status_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in Program.STATUS_CHOICE
        ]

    def resolve_program_frequency_of_payments_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in Program.FREQUENCY_OF_PAYMENTS_CHOICE
        ]

    def resolve_program_sector_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in Program.SECTOR_CHOICE
        ]

    def resolve_program_scope_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in Program.SCOPE_CHOICE
        ]

    def resolve_cash_plan_status_choices(self, info, **kwargs):
        return [
            {"name": name, "value": value}
            for value, name in Program.STATUS_CHOICE
        ]
