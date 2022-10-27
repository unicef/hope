from typing import List

import graphene
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.core_fields_attributes import FieldFactory, Scope
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.schema import ExtendedConnection, FieldAttributeNode
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.targeting.filters import TargetPopulationFilter
from hct_mis_api.apps.utils.schema import Arg


def get_field_by_name(field_name: str):
    field = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name").get(field_name)
    choices = field.get("choices")
    if choices and callable(choices):
        field["choices"] = choices()
    return field


def filter_choices(field, args) -> List:
    choices = field.get("choices")
    if args and choices:
        field["choices"] = list(filter(lambda choice: str(choice["value"]) in args, choices))
    return field


class TargetingCriteriaRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info):
        return self.arguments

    def resolve_field_attribute(parent, info):
        if parent.is_flex_field:
            return FlexibleAttribute.objects.get(name=parent.field_name)
        else:
            field_attribute = get_field_by_name(parent.field_name)
            return filter_choices(field_attribute, parent.arguments)

    class Meta:
        model = target_models.TargetingCriteriaRuleFilter


class TargetingIndividualBlockRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)
    field_attribute = graphene.Field(FieldAttributeNode)

    def resolve_arguments(self, info):
        return self.arguments

    def resolve_field_attribute(parent, info):
        if parent.is_flex_field:
            return FlexibleAttribute.objects.get(name=parent.field_name)
        else:
            field_attribute = get_field_by_name(parent.field_name)
            return filter_choices(field_attribute, parent.arguments)

    class Meta:
        model = target_models.TargetingIndividualBlockRuleFilter


class TargetingIndividualRuleFilterBlockNode(DjangoObjectType):
    individual_block_filters = graphene.List(TargetingIndividualBlockRuleFilterNode)

    def resolve_individual_block_filters(self, info):
        return self.individual_block_filters.all()

    class Meta:
        model = target_models.TargetingIndividualRuleFilterBlock


class TargetingCriteriaRuleNode(DjangoObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterNode)
    individuals_filters_blocks = graphene.List(TargetingIndividualRuleFilterBlockNode)

    def resolve_individuals_filters_blocks(self, info):
        return self.individuals_filters_blocks.all()

    def resolve_filters(self, info):
        return self.filters.all()

    class Meta:
        model = target_models.TargetingCriteriaRule


class TargetingCriteriaNode(DjangoObjectType):
    rules = graphene.List(TargetingCriteriaRuleNode)

    def resolve_rules(self, info):
        return self.rules.all()

    class Meta:
        model = target_models.TargetingCriteria


class StatsObjectType(graphene.ObjectType):
    child_male = graphene.Int()
    child_female = graphene.Int()
    adult_male = graphene.Int()
    adult_female = graphene.Int()
    all_households = graphene.Int()
    all_individuals = graphene.Int()


class TargetPopulationNode(BaseNodePermissionMixin, DjangoObjectType):
    """Defines an individual target population record."""

    permission_classes = (
        hopePermissionClass(
            Permissions.TARGETING_VIEW_DETAILS,
        ),
    )

    total_family_size = graphene.Int(source="total_family_size")
    targeting_criteria = TargetingCriteriaRuleFilterNode()
    householdList = DjangoConnectionField(HouseholdNode)

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
