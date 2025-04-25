from typing import Any, List

import graphene
from graphene import ObjectType, relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.geo.filters import AreaFilter
from hct_mis_api.apps.geo.models import Area, AreaType
from hct_mis_api.apps.utils.graphql import does_path_exist_in_query


class AreaNode(DjangoObjectType):
    class Meta:
        model = Area
        exclude = ["geom",]
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
    level = graphene.Int()

    @staticmethod
    def resolve_areas(parent: Area, info: Any, **kwargs: Any) -> List[Area]:
        return parent.get_children()

    @staticmethod
    def resolve_level(parent: Area, info: Any, **kwargs: Any) -> int:
        return parent.area_type.area_level


class AreaGroupNode(ObjectType):
    ids = graphene.List(graphene.ID)
    level = graphene.Int()
    total_count = graphene.Int()


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
    all_areas_tree = graphene.List(
        AreaTreeNode,
        business_area=graphene.String(required=True),
    )

    def resolve_all_admin_areas(self, info: Any, **kwargs: Any) -> List[Area]:
        return Area.objects.all().order_by("area_type__area_level", "name")

    def resolve_all_areas_tree(self, info: Any, business_area: str, **kwargs: Any) -> List[Area]:
        # get Area max level 3
        queryset = (
            Area.objects.filter(area_type__country__business_areas__slug=business_area, area_type__area_level__lte=3)
            .select_related("area_type__country")
            .prefetch_related("area_type__country__business_areas")
        )
        if does_path_exist_in_query("edges.node.level", info):
            queryset = queryset.select_related("area_type")
        return queryset.get_cached_trees()
