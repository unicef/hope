from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

import graphene
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    BasePermission,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.field_attributes.core_fields_attributes import FieldFactory
from hct_mis_api.apps.core.field_attributes.fields_types import Scope
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.schema import ExtendedConnection, FieldAttributeNode
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.targeting.filters import HouseholdFilter, TargetPopulationFilter
from hct_mis_api.apps.utils.schema import Arg

if TYPE_CHECKING:
    from django.db.models.query import QuerySet

    from graphene.types.structures import List as GrapheneList

    from hct_mis_api.apps.targeting.models import TargetingIndividualBlockRuleFilter


def get_field_by_name(field_name: str, business_area) -> Dict:
    factory = FieldFactory.from_scope(Scope.TARGETING)
    factory.apply_business_area(business_area.slug)
    field = factory.to_dict_by("name")[field_name]
    choices = field.get("choices")
    if choices and callable(choices):
        field["choices"] = choices()
    return field


def filter_choices(field: Optional[Dict], args: List) -> Optional[Dict]:
    if not field:
        return None
    choices = field.get("choices")
    if args and choices:
        field["choices"] = list(filter(lambda choice: str(choice["value"]) in args, choices))
    return field


class TargetingCriteriaRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info: Any) -> "GrapheneList":
        return self.arguments

    def resolve_field_attribute(parent, info: Any) -> Optional[Dict]:
        if parent.is_flex_field:
            return FlexibleAttribute.objects.get(name=parent.field_name)
        else:
            field_attribute = get_field_by_name(
                parent.field_name, parent.targeting_criteria_rule.targeting_criteria.target_population.business_area
            )
            return filter_choices(field_attribute, parent.arguments)  # type: ignore # can't convert graphene list to list

    class Meta:
        model = target_models.TargetingCriteriaRuleFilter


class TargetingIndividualBlockRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info: Any) -> "GrapheneList":
        return self.arguments

    def resolve_field_attribute(parent, info: Any) -> Any:
        if parent.is_flex_field:
            return FlexibleAttribute.objects.get(name=parent.field_name)

        field_attribute = get_field_by_name(
            parent.field_name,
            parent.individuals_filters_block.targeting_criteria_rule.targeting_criteria.target_population.business_area,
        )
        return filter_choices(field_attribute, parent.arguments)  # type: ignore # can't convert graphene list to list

    class Meta:
        model = target_models.TargetingIndividualBlockRuleFilter


class TargetingIndividualRuleFilterBlockNode(DjangoObjectType):
    individual_block_filters = graphene.List(TargetingIndividualBlockRuleFilterNode)

    def resolve_individual_block_filters(self, info: Any) -> "QuerySet":
        return self.individual_block_filters.all()

    class Meta:
        model = target_models.TargetingIndividualRuleFilterBlock


class TargetingCriteriaRuleNode(DjangoObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterNode)
    individuals_filters_blocks = graphene.List(TargetingIndividualRuleFilterBlockNode)

    def resolve_individuals_filters_blocks(self, info: Any) -> "QuerySet[TargetingIndividualBlockRuleFilter]":
        return self.individuals_filters_blocks.all()

    def resolve_filters(self, info: Any) -> "QuerySet[TargetPopulationFilter]":
        return self.filters.all()

    class Meta:
        model = target_models.TargetingCriteriaRule


class TargetingCriteriaNode(DjangoObjectType):
    rules = graphene.List(TargetingCriteriaRuleNode)

    def resolve_rules(self, info: Any) -> "QuerySet":
        return self.rules.all()

    class Meta:
        model = target_models.TargetingCriteria


class TargetPopulationNode(BaseNodePermissionMixin, DjangoObjectType):
    """Defines an individual target population record."""

    permission_classes: Tuple[Type[BasePermission]] = (
        hopePermissionClass(
            Permissions.TARGETING_VIEW_DETAILS,
        ),
    )

    total_family_size = graphene.Int(source="total_family_size")
    targeting_criteria = TargetingCriteriaRuleFilterNode()
    household_list = DjangoFilterConnectionField(HouseholdNode, filterset_class=HouseholdFilter)
    households = DjangoFilterConnectionField(HouseholdNode, filterset_class=HouseholdFilter)

    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class TargetingCriteriaRuleFilterObjectType(graphene.InputObjectType):
    comparison_method = graphene.String(required=True)
    is_flex_field = graphene.Boolean(required=True)
    field_name = graphene.String(required=True)
    arguments = graphene.List(Arg, required=True)


class TargetingIndividualRuleFilterBlockObjectType(graphene.InputObjectType):
    individual_block_filters = graphene.List(TargetingCriteriaRuleFilterObjectType)


class TargetingCriteriaRuleObjectType(graphene.InputObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterObjectType)
    individuals_filters_blocks = graphene.List(TargetingIndividualRuleFilterBlockObjectType)


class TargetingCriteriaObjectType(graphene.InputObjectType):
    rules = graphene.List(TargetingCriteriaRuleObjectType)
