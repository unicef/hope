from typing import Any

import graphene
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType

from hope.apps.core.extended_connection import ExtendedConnection
from hope.apps.geo.models import Area, AreaType


class AreaNode(DjangoObjectType):
    class Meta:
        model = Area
        filter_fields = ["name"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTypeNode(DjangoObjectType):
    class Meta:
        model = AreaType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection

    @staticmethod
    def resolve_areas(parent: Area, info: Any, **kwargs: Any) -> list[Area]:
        return parent.get_children()

    @staticmethod
    def resolve_level(parent: Area, info: Any, **kwargs: Any) -> int:
        return parent.area_type.area_level


class AreaGroupNode(ObjectType):
    ids = graphene.List(graphene.ID)
    level = graphene.Int()
    total_count = graphene.Int()
