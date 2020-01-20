import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from targeting.models import TargetPopulation


class TargetPopulationNode(DjangoObjectType):
    class Meta:
        model = TargetPopulation
        filter_fields = []
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
