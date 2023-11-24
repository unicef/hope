from typing import Any, Optional

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
        exclude = ["geom", "point"]
        filter_fields = ["name"]
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaTypeNode(DjangoObjectType):
    class Meta:
        model = AreaType
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class AreaSimpleNode(graphene.ObjectType):
    id = graphene.String()
    name = graphene.String()
    level = graphene.Int()
    tree_id = graphene.Int()
    children = graphene.List(lambda: AreaSimpleNode)


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
    all_admin_areas_tree = graphene.List(AreaSimpleNode, business_area=graphene.String(required=True))

    def resolve_all_admin_areas_tree(self, info: Any, business_area: str) -> Any:
        # add filters
        filters = {}
        if business_area:
            filters.update({"area_type__country__business_areas__slug": business_area})

        qs = Area.objects.filter(**filters).only("id", "tree_id", "name", "level")

        def _get_sub_tree(area: Area) -> Optional[dict]:
            return (
                {
                    "id": str(area.id),
                    "level": area.level,
                    "tree_id": area.tree_id,
                    "name": area.name,
                    "children": [_get_sub_tree(child) for child in list(area.get_children())],
                }
                if isinstance(area, Area)
                else None
            )

        def _get_area_with_children(area_obj: Area) -> dict:
            return {
                "id": str(area_obj.id),
                "level": area_obj.level,
                "tree_id": area_obj.tree_id,
                "name": area_obj.name,
                "children": [_get_sub_tree(child) for child in list(area_obj.get_children())],
            }

        trees = [
            _get_area_with_children(parent_area)
            for tree_id in qs.values_list("tree_id", flat=True).distinct("tree_id")
            for parent_area in qs.filter(tree_id=tree_id, parent=None)
        ]

        return trees
