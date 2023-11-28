from typing import Any, List

import graphene
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.geo.filters import AreaFilter
from hct_mis_api.apps.geo.models import Area, AreaType


class AreaNode(DjangoObjectType):
    class Meta:
        model = Area
        exclude = ["geom", "point"]
        filter_fields = ["name"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTypeNode(DjangoObjectType):
    class Meta:
        model = AreaType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTreeNode(ObjectType):
    id = graphene.ID()
    name = graphene.String()
    p_code = graphene.String()
    areas = graphene.List(lambda: AreaTreeNode)

    @staticmethod
    def resolve_areas(parent: Area, info: Any, **kwargs: Any) -> List[Area]:
        return parent.get_children()


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
    all_areas_tree = graphene.List(
        AreaTreeNode,
        business_area=graphene.String(required=True),
    )

    def resolve_all_areas_tree(self, info: Any, business_area: str, **kwargs: Any) -> List[Area]:
        return (
            Area.objects.filter(area_type__country__business_areas__slug=business_area)
            .order_by("name", "p_code")
            .get_cached_trees()
        )
