import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from program.models import Program, CashPlan


class ProgramNode(DjangoObjectType):
    class Meta:
        model = Program
        filter_fields = []
        interfaces = (relay.Node,)


class CashPlan(DjangoObjectType):
    class Meta:
        model = CashPlan
        filter_fields = ['program']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    program = relay.Node.Field(ProgramNode)
    all_programs = DjangoFilterConnectionField(ProgramNode)
    cash_plan = relay.Node.Field(CashPlan)
    all_cash_plans = DjangoFilterConnectionField(CashPlan)
