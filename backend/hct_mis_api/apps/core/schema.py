import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Location


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        filter_fields = ['country']
        interfaces = (relay.Node,)


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
