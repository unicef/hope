import functools
import json
import operator

import django_filters
import graphene
import targeting.models as target_models
from core.filters import IntegerFilter
from core.schema import ExtendedConnection
from django.db.models import Q
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from household.models import Household
from household.schema import HouseholdNode


# TODO(codecakes): see if later the format can be kept consistent in FilterAttrType model.
# by using FlexFieldNode and CoreFieldNode to return target filter rules.


class TargetPopulationFilter(django_filters.FilterSet):
    """Query target population records.

    Loads associated entries for Households and TargetRules.
    """

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", distinct=True
    )
    created_by_name = django_filters.CharFilter(
        field_name="created_by", method="filter_created_by_name"
    )
    # TODO(codecakes): Fix allTargetPopulationFilters query response by fixing the below two.
    num_individuals_min = IntegerFilter(
        field_name="target_rules__core_rules__num_individuals_min",
        lookup_expr="gte",
        distinct=True,
    )
    num_individuals_max = IntegerFilter(
        field_name="target_rules__core_rules__num_individuals_max",
        lookup_expr="lte",
        distinct=True,
    )

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
        fields = "__all__"

        filter_overrides = {
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
            "last_edited_at",
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


class SavedTargetRuleFilter(django_filters.FilterSet):
    """Filters for saved TargetRules."""

    class Meta:
        model = target_models.TargetRule
        fields = (
            "flex_rules",
            "core_rules",
            "target_population",
        )

        filter_overrides = {
            target_models.JSONField: {
                "filter_class": django_filters.LookupChoiceFilter,
            },
        }


class SavedTargetRuleNode(DjangoObjectType):
    """Fetches the saved filters."""

    class Meta:
        model = target_models.TargetRule
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = SavedTargetRuleFilter


class StatusNode(graphene.ObjectType):
    # show list of status available
    key = graphene.String()
    value = graphene.String()


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode, distinct=True)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
    # Saved snapshots of target rules from a target population.
    saved_target_rule = relay.Node.Field(SavedTargetRuleNode)
    all_saved_target_rule = DjangoFilterConnectionField(SavedTargetRuleNode)
    # Realtime Queries from golden records.
    # household and associated registration and individuals records.
    target_rules = graphene.List(
        HouseholdNode,
        serialized_list=graphene.String(),
        description="json dump of filters containing key value pairs.",
    )
    target_status_types = graphene.List(StatusNode)

    def resolve_target_status_types(self, info):
        return [
            StatusNode(key, value)
            for (key, value) in target_models.TargetPopulation.STATE_CHOICES
        ]

    def resolve_target_rules(self, info, serialized_list):
        """Resolver for target_rules. Queries from golden records.

        args:
            info: object, HTTPRequestObject.
            serialized_list: list, check below.

        Arguments in serialized_list are of type.
        """
        rule_lists = json.loads(serialized_list)
        return functools.reduce(
            operator.or_, Query.get_households_from_rule(rule_lists),
        )

    @staticmethod
    def get_households_from_rule(rule_lists: list):
        """Fetches live results from Household golden db."""
        for rule_obj in rule_lists:
            search_rules = {}
            rules = {}
            rules.update(rule_obj.get("core_rules", {}))
            rules.update(rule_obj.get("flex_rules", {}))
            # TODO(codecakes): make it more dynamic/generic later by just using query filters.
            for functor in target_models.FilterAttrType.apply_filters(rules):
                search_rules.update(functor())
            yield Household.objects.filter(**search_rules)
