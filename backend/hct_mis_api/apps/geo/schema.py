import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.geo.filters import AreaFilter
from hct_mis_api.apps.geo.models import Area, AreaType


class AreaNode(DjangoObjectType):
    class Meta:
        model = Area
        exclude_fields = ["geom", "point"]
        filter_fields = ["name"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTypeNode(DjangoObjectType):
    class Meta:
        model = AreaType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
