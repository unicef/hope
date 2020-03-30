import functools
import json
import operator
from pprint import pprint

import django_filters
import graphene
import targeting.models as target_models
from core.models import FlexibleAttribute
from core.schema import ExtendedConnection
from core.filters import IntegerFilter
from django.db.models import Q
from graphene import relay, String, Scalar
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField

from core.utils import decode_id_string
from household import models as household_models
from household.models import Household
from household.schema import HouseholdNode
from core import utils

# TODO(codecakes): see if later the format can be kept consistent in FilterAttrType model.
# by using FlexFieldNode and CoreFieldNode to return target filter rules.


class TargetPopulationFilter(django_filters.FilterSet):
    """Query target population records.

    Loads associated entries for Households and TargetRules.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_by_name = django_filters.CharFilter(
        field_name="created_by", method="filter_created_by_name"
    )
    num_individuals_min = IntegerFilter(
        field_name="target_rules__core_rules__num_individuals_min",
        lookup_expr="gte",
        method="filter_num_individuals_min",
    )
    num_individuals_max = IntegerFilter(
        field_name="target_rules__core_rules__num_individuals_max",
        lookup_expr="lte",
        method="filter_num_individuals_max",
    )

    @staticmethod
    def filter_num_individuals_min(queryset, _model, _value):
        return queryset.distinct("id")

    @staticmethod
    def filter_num_individuals_max(queryset, _model, _value):
        return queryset.distinct("id")

    @staticmethod
    def filter_created_by_name(queryset, model_field, value):
        """Gets full name of the associated user from query."""
        fname_query_key = f"{model_field}__first_name__icontains"
        lname_query_key = f"{model_field}__last_name__icontains"
        for name in value.strip().split():
            queryset = queryset.filter(
                Q(**{fname_query_key: name,}) | Q(**{lname_query_key: name,})
            )
        return queryset

    class Meta:
        model = target_models.TargetPopulation
        fields = (
            "name",
            "created_by_name",
            "created_at",
            "updated_at",
            "status",
            "households",
        )

        filter_overrides = {
            target_models.IntegerRangeField: {
                "filter_class": django_filters.NumericRangeFilter,
            },
            target_models.models.DateTimeField: {
                "filter_class": django_filters.DateTimeFilter,
            },
        }

    # TODO(codecakes): how to order?
    order_by = django_filters.OrderingFilter(
        fields=(
            "name",
            "created_at",
            "created_by",
            "updated_at",
            "status",
            "total_households",
            "total_family_size",
        )
    )


class Arg(Scalar):
    """
    Allows use of a JSON String for input / output from the GraphQL schema.

    Use of this type is *not recommended* as you lose the benefits of having a defined, static
    schema (one of the key benefits of GraphQL).
    """

    @staticmethod
    def serialize(dt):
        return dt

    @staticmethod
    def parse_literal(node):
        return node

    @staticmethod
    def parse_value(value):
        return value


class TargetingCriteriaRuleFilterNode(DjangoObjectType):
    arguments = graphene.List(Arg)

    def resolve_arguments(self, info):
        return self.arguments

    class Meta:
        model = target_models.TargetingCriteriaRuleFilter


class TargetingCriteriaRuleNode(DjangoObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterNode)

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


class TargetPopulationNode(DjangoObjectType):
    """Defines an individual target population record."""

    total_households = graphene.Int(source="total_households")
    total_family_size = graphene.Int(source="total_family_size")
    candidate_list_targeting_criteria = TargetingCriteriaRuleFilterNode()
    final_list_targeting_criteria = TargetingCriteriaRuleFilterNode()

    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class TargetingCriteriaRuleFilterObjectType(graphene.InputObjectType):
    comparision_method = graphene.String()
    is_flex_field = graphene.Boolean()
    field_name = graphene.String()
    arguments = graphene.List(Arg)


class TargetingCriteriaRuleObjectType(graphene.InputObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterObjectType)


class TargetingCriteriaObjectType(graphene.InputObjectType):
    rules = graphene.List(TargetingCriteriaRuleObjectType)


def targeting_criteria_object_type_to_query(targeting_criteria_object_type):
    targeting_criteria_querying = target_models.TargetingCriteriaQueryingMixin([])
    for rule in targeting_criteria_object_type.get("rules", []):
        targeting_criteria_rule_querying = (
            target_models.TargetingCriteriaRuleQueryingMixin([])
        )
        for filter_dict in rule.get("filters", []):
            targeting_criteria_rule_querying.filters.append(
                target_models.TargetingCriteriaRuleFilter(**filter_dict)
            )
        targeting_criteria_querying.rules.append(
            targeting_criteria_rule_querying
        )
    return targeting_criteria_querying.get_query()


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
    golden_record_by_targeting_criteria = DjangoConnectionField(
        HouseholdNode, targeting_criteria=TargetingCriteriaObjectType()
    )
    candidate_households_list_by_targeting_criteria = DjangoFilterConnectionField(
        HouseholdNode, target_population=graphene.Argument(graphene.ID)
    )
    final_households_list_by_targeting_criteria = DjangoFilterConnectionField(
        HouseholdNode,
        target_population=graphene.Argument(graphene.ID),
        targeting_criteria=TargetingCriteriaObjectType(),
    )

    def resolve_candidate_households_list_by_targeting_criteria(
        parent, info, target_population
    ):
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(
            pk=target_population_id
        )
        if target_population_model.status == "DRAFT":
            return Household.objects.filter(
                target_population_model.candidate_list_targeting_criteria.get_query()
            )
        return target_population_model.households.all()

    def resolve_final_list_by_targeting_criteria(
        parent, info, target_population, targeting_criteria=None
    ):
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(
            pk=target_population_id
        )
        if target_population_model.status == "DRAFT":
            return []
        if target_population_model.status == "APPROVED":
            if targeting_criteria is None:
                return target_population_model.households.filter(
                    target_population_model.candidate_list_targeting_criteria.get_query()
                )
            return target_population_model.households.filter(
                targeting_criteria_object_type_to_query(targeting_criteria)
            ).all()
        return target_population_model.households.filter(final=True).all()

    def resolve_golden_record_by_targeting_criteria(
        parent, info, targeting_criteria
    ):
        return Household.objects.filter(
            targeting_criteria_object_type_to_query(targeting_criteria)
        )
