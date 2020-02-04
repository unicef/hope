import graphene
from graphene import relay, String
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.models import Location, BusinessArea


class ChoiceObject(graphene.ObjectType):
    name = String()
    value = String()


class ExtendedConnection(graphene.Connection):
    class Meta:
        abstract = True

    total_count = graphene.Int()
    edge_count = graphene.Int()

    def resolve_total_count(root, info, **kwargs):
        return root.length

    def resolve_edge_count(root, info, **kwargs):
        return len(root.edges)


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        exclude_fields = [
            "geom",
            "point"
        ]
        filter_fields = ['title']
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

class BusinessAreaNode(DjangoObjectType):
    class Meta:
        model = BusinessArea
        filter_fields = ["id"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
    all_business_areas = DjangoFilterConnectionField(BusinessAreaNode)
