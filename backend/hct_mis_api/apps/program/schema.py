import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from program.models import Program, CashPlan


class ProgramNode(DjangoObjectType):
    total_number_of_households = graphene.Int()

    class Meta:
        model = Program
        filter_fields = []
        interfaces = (relay.Node,)

    def resolve_total_number_of_households(self, info, **kwargs):
        return self.total_number_of_households


class CashPlanNode(DjangoObjectType):
    class Meta:
        model = CashPlan
        filter_fields = ['program']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoFilterConnectionField(ProgramNode)
    cash_plan = relay.Node.Field(CashPlanNode)
    all_cash_plans = DjangoFilterConnectionField(CashPlanNode)
    program_status_choices = graphene.List(graphene.List(graphene.String))
    program_frequency_of_payments_choices = graphene.List(
        graphene.List(graphene.String)
    )
    program_sector_choices = graphene.List(graphene.List(graphene.String))
    program_scope_choices = graphene.List(graphene.List(graphene.String))
    cash_plan_status_choices = graphene.List(graphene.List(graphene.String))

    def resolve_program_status_choices(self, info, **kwargs):
        return Program.STATUS_CHOICE

    def resolve_program_frequency_of_payments_choices(self, info, **kwargs):
        return Program.FREQUENCY_OF_PAYMENTS_CHOICE

    def resolve_program_sector_choices(self, info, **kwargs):
        return Program.SECTOR_CHOICE

    def resolve_program_scope_choices(self, info, **kwargs):
        return Program.SCOPE_CHOICE

    def resolve_cash_plan_status_choices(self, info, **kwargs):
        return CashPlan.STATUS_CHOICE
