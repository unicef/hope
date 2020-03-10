import functools
import json
import operator
from decimal import Decimal

import django_filters
import graphene
import targeting.models as target_models
from core.schema import ExtendedConnection
from django.db.models import Q
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from household.models import Household
from household.schema import HouseholdNode


class TargetPopulationFilter(django_filters.FilterSet):
    """Query target population records.

    Loads associated entries for Households and TargetRules.
    """

    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    created_by_name = django_filters.CharFilter(
        field_name="created_by", method="filter_created_by_name"
    )
    num_individuals_min = django_filters.NumberFilter(
        field_name="target_rules", method="filter_num_individuals_min"
    )
    num_individuals_max = django_filters.NumberFilter(
        field_name="target_rules", method="filter_num_individuals_max"
    )

    # TODO(codecakes): waiting on dist to school and adminlevel clarification.
    @staticmethod
    def filter_created_by_name(queryset, model_field, value):
        """Gets full name of the associated user from query."""
        first_name_query = {
            f"{model_field}__first_name__icontains": value,
        }
        last_name_query = {
            f"{model_field}__last_name__icontains": value,
        }
        return queryset.filter(Q(**first_name_query) | Q(**last_name_query))

    @staticmethod
    def filter_num_individuals_min(queryset, model_field, value):
        field_name = f"{model_field}__core_rules__num_individuals_min__gte"
        if isinstance(value, Decimal):
            value = int(value)
        return queryset.filter(**{field_name: value})

    @staticmethod
    def filter_num_individuals_max(queryset, model_field, value):
        field_name = f"{model_field}__core_rules__num_individuals_max__lte"
        if isinstance(value, Decimal):
            value = int(value)
        return queryset.filter(**{field_name: value})

    class Meta:
        model = target_models.TargetPopulation
        fields = (
            "name",
            "created_by_name",
            "created_at",
            "last_edited_at",
            "status",
            "total_households",
            "total_family_size",
            "households",
            "target_rules",
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
            "last_edited_at",
            "status",
            "total_households",
            "total_family_size",
        )
    )


class TargetPopulationNode(DjangoObjectType):
    """Defines an individual target population record."""

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
                # 'extra': lambda f: {'lookup_expr': ['icontains']},
            },
        }


class SavedTargetRuleNode(DjangoObjectType):
    """Fetches the saved filters."""

    class Meta:
        model = target_models.TargetRule
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = SavedTargetRuleFilter


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
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
            # TODO(codecakes): decouple to core and flex functions.
            # many dynamic fields here will depend on the info
            #  from FilterAttrType class falls back on that method.
            for functor in target_models.FilterAttrType.apply_filters(rules):
                search_rules.update(functor())
            yield Household.objects.filter(**search_rules)
