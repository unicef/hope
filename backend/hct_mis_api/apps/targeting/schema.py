import functools
import json
import operator

import django_filters
import graphene
import targeting.models as target_models
from core.models import FlexibleAttribute
from core.schema import ExtendedConnection
from core.filters import IntegerFilter
from django.db.models import Q
from graphene import relay, String
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphene_django.filter import DjangoFilterConnectionField
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


class TargetPopulationNode(DjangoObjectType):
    """Defines an individual target population record."""

    total_households = graphene.Int(source="total_households")
    total_family_size = graphene.Int(source="total_family_size")

    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class TargetingCriteriaRuleFilterNode(graphene.InputObjectType):
    comparision_method = graphene.String()
    is_flex_field = graphene.Boolean()
    field_name = graphene.String()
    arguments = graphene.JSONString()


class TargetingCriteriaRuleNode(graphene.InputObjectType):
    filters = graphene.List(TargetingCriteriaRuleFilterNode)


class TargetingCriteriaObjectType(graphene.InputObjectType):
    rules = graphene.List(TargetingCriteriaRuleNode)


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
    golden_record_by_targeting_criteria = DjangoConnectionField(
        HouseholdNode, targeting_criteria=TargetingCriteriaObjectType()
    )

    def resolve_golden_record_by_targeting_criteria(
        parent, info, targeting_criteria
    ):
        targeting_criteria_querying = (
            target_models.TargetingCriteriaQueryingMixin()
        )
        for rule in targeting_criteria.get("rules", []):
            targeting_criteria_rule_querying = (
                target_models.TargetingCriteriaRuleQueryingMixin()
            )
            for filter_dict in rule.get("filters", []):
                targeting_criteria_rule_querying.filters.append(
                    target_models.TargetingCriteriaRuleFilter(**filter_dict)
                )
            targeting_criteria_querying.rules.append(targeting_criteria_rule_querying)
        return Household.objects.filter(targeting_criteria_querying.get_query())

