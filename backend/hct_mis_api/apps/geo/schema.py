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


class Query(graphene.ObjectType):
    admin_area = relay.Node.Field(AreaNode)
    all_admin_areas = DjangoFilterConnectionField(AreaNode, filterset_class=AreaFilter)
    all_admin_areas_tree = graphene.List(AreaNode)

    def resolve_all_admin_areas_tree(self, info: Any) -> Any:  # business_area: Optional[str]
        # TODO: update this one
        """
        [{
                "id": "2",
                "name": "Child - 2",
                "children": [
                    {
                        "id": "22",
                        "name": "Child - 22",
                        "selected": True,
                    },
                ],
            }]
        """
        filters = {}
        resp = []
        # if business_area:
        #     filters.update({"business_area": business_area})

        qs = Area.objects.filter(area_type__country__business_areas__slug="afghanistan").only("id", "tree_id", "name", "level")

        # def _get_area_with_children(area_obj) -> dict:
        #     area_with_children = {"id": area_obj.id, "name": area_obj.name, "children": [area_obj.get_children()]}
        #
        #     for children_list in area_with_children.get("children", []):
        #         update_children_with_recursive_check(children_list)
        #
        #
        #
        #     return area_with_children
        #
        # def update_children_with_recursive_check(children_list):
        #     for child in children_list:
        #         child_obj =  {"id": child.id, "name": child.name, "children": [child.get_children()]}
        #         child_obj["children"] = update_children_with_recursive_check(child.get_children())
        #
        #     return children_list
        #
        # for tree_id in qs.values_list("tree_id", flat=True):
        #     qs_tree = qs.filter(tree_id=tree_id)
        #     parent_area = qs_tree.filter(parent=None).first()
        #     if parent_area:
        #         tree = _get_area_with_children(parent_area)
        #         # for children in children_list["children"]:
        #         #     children["children"] = children
        #         resp.append(tree)

        return resp



