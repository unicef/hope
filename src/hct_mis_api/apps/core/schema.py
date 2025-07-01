from typing import Any

import graphene
from constance import config

# from hct_mis_api.apps.core.models import FlexibleAttributeGroup
#
# from graphene_django import DjangoObjectType
#
# if TYPE_CHECKING:
#     from django.db.models.query import QuerySet

# class GroupAttributeNode(DjangoObjectType):
#     label_en = graphene.String()
#     flex_attributes = graphene.List(
#         FieldAttributeNode,
#         flex_field=graphene.Boolean(),
#         description="All field datatype meta.",
#     )
#
#     class Meta:
#         model = FlexibleAttributeGroup
#         fields = ["id", "name", "label", "flex_attributes", "label_en"]
#
#     @staticmethod
#     def resolve_label_en(parent: FlexibleAttributeGroup, info: Any) -> Any:
#         return _custom_dict_or_attr_resolver("label", None, parent, info)["English(EN)"]
#
#     @staticmethod
#     def resolve_flex_attributes(parent: FlexibleAttributeGroup, info: Any) -> "QuerySet":
#         return parent.flex_attributes.all()


class Query(graphene.ObjectType):
    # all_groups_with_fields = graphene.List(
    #     GroupAttributeNode,
    #     description="Get all groups that contains flex fields",
    # )
    cash_assist_url_prefix = graphene.String()

    def resolve_cash_assist_url_prefix(parent, info: Any) -> str:
        return config.CASH_ASSIST_URL_PREFIX

    # def resolve_all_groups_with_fields(self, info: Any, **kwargs: Any) -> "QuerySet[FlexibleAttributeGroup]":
    #     return FlexibleAttributeGroup.objects.distinct().filter(flex_attributes__isnull=False)
