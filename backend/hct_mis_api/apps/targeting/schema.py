from typing import Union

from django.db.models import Prefetch

import graphene
from graphene import relay
from graphene_django import DjangoConnectionField, DjangoObjectType

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.core_fields_attributes import FieldFactory, Scope
from hct_mis_api.apps.core.models import FlexibleAttribute
from hct_mis_api.apps.core.schema import (
    ChoiceObject,
    ExtendedConnection,
    FieldAttributeNode,
)
from hct_mis_api.apps.core.utils import (
    decode_and_get_object,
    decode_id_string,
    map_unicef_ids_to_households_unicef_ids,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.filters import HouseholdFilter, TargetPopulationFilter
from hct_mis_api.apps.targeting.validators import TargetingCriteriaInputValidator
from hct_mis_api.apps.utils.schema import Arg


def get_field_by_name(field_name: str):
    field = FieldFactory.from_scope(Scope.TARGETING).to_dict_by("name").get(field_name)
    choices = field.get("choices")
    if choices and callable(choices):
        field["choices"] = choices()
    return field


def filter_choices(field, args):
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

    total_households = graphene.Int(source="total_households")
    total_family_size = graphene.Int(source="total_family_size")
    candidate_list_targeting_criteria = TargetingCriteriaRuleFilterNode()
    final_list_targeting_criteria = TargetingCriteriaRuleFilterNode()
    final_list = DjangoConnectionField(HouseholdNode)
    candidate_stats = graphene.Field(StatsObjectType)
    final_stats = graphene.Field(StatsObjectType)

    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class TargetingCriteriaRuleFilterObjectType(graphene.InputObjectType):
    comparision_method = graphene.String(required=True)
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


def targeting_criteria_object_type_to_query(
    targeting_criteria_object_type, program: Union[str, Program], excluded_ids=""
):
    TargetingCriteriaInputValidator.validate(targeting_criteria_object_type)
    if not isinstance(program, Program):
        program = decode_and_get_object(program, Program, True)
    targeting_criteria_querying = target_models.TargetingCriteriaQueryingMixin(
        [], excluded_household_ids=map_unicef_ids_to_households_unicef_ids(excluded_ids)
    )
    for rule in targeting_criteria_object_type.get("rules", []):
        targeting_criteria_rule_querying = target_models.TargetingCriteriaRuleQueryingMixin(
            filters=[], individuals_filters_blocks=[]
        )
        for filter_dict in rule.get("filters", []):
            targeting_criteria_rule_querying.filters.append(target_models.TargetingCriteriaRuleFilter(**filter_dict))
        for individuals_filters_block_dict in rule.get("individuals_filters_blocks", []):
            individuals_filters_block = target_models.TargetingIndividualRuleFilterBlockMixin(
                [], not program.individual_data_needed
            )
            targeting_criteria_rule_querying.individuals_filters_blocks.append(individuals_filters_block)
            for individual_block_filter_dict in individuals_filters_block_dict.get("individual_block_filters", []):
                individuals_filters_block.individual_block_filters.append(
                    target_models.TargetingIndividualBlockRuleFilter(**individual_block_filter_dict)
                )
        targeting_criteria_querying.rules.append(targeting_criteria_rule_querying)
    return targeting_criteria_querying.get_query()


def prefetch_selections(qs, target_population=None):
    return qs.prefetch_related(
        Prefetch(
            "selections",
            queryset=target_models.HouseholdSelection.objects.filter(target_population=target_population),
        )
    )


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoPermissionFilterConnectionField(
        TargetPopulationNode, permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_LIST),)
    )
    golden_record_by_targeting_criteria = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        targeting_criteria=TargetingCriteriaObjectType(required=True),
        program=graphene.Argument(graphene.ID, required=True),
        excluded_ids=graphene.Argument(graphene.String, required=True),
        filterset_class=HouseholdFilter,
        permission_classes=(
            hopePermissionClass(Permissions.TARGETING_UPDATE),
            hopePermissionClass(Permissions.TARGETING_CREATE),
            hopePermissionClass(Permissions.TARGETING_VIEW_DETAILS),
        ),
    )
    candidate_households_list_by_targeting_criteria = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        target_population=graphene.Argument(graphene.ID, required=True),
        filterset_class=HouseholdFilter,
        permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_DETAILS),),
    )
    final_households_list_by_targeting_criteria = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        target_population=graphene.Argument(graphene.ID, required=True),
        targeting_criteria=TargetingCriteriaObjectType(),
        excluded_ids=graphene.Argument(graphene.String, required=True),
        filterset_class=HouseholdFilter,
        permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_DETAILS),),
    )
    target_population_status_choices = graphene.List(ChoiceObject)

    def resolve_target_population_status_choices(self, info, **kwargs):
        return [{"name": name, "value": value} for value, name in target_models.TargetPopulation.STATUS_CHOICES]

    def resolve_candidate_households_list_by_targeting_criteria(parent, info, target_population, **kwargs):
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(pk=target_population_id)
        if target_population_model.status == target_models.TargetPopulation.STATUS_DRAFT:
            household_queryset = Household.objects
            return prefetch_selections(
                household_queryset.filter(target_population_model.candidate_list_targeting_criteria.get_query()),
            ).distinct()
        return (
            prefetch_selections(
                target_population_model.vulnerability_score_filtered_households, target_population_model
            )
            .distinct()
            .all()
        )

    def resolve_final_households_list_by_targeting_criteria(
        parent, info, target_population, targeting_criteria=None, **kwargs
    ):
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(pk=target_population_id)
        if target_population_model.status == target_models.TargetPopulation.STATUS_DRAFT:
            return []
        if target_population_model.status == target_models.TargetPopulation.STATUS_LOCKED:
            if targeting_criteria is None:
                if target_population_model.final_list_targeting_criteria:
                    return (
                        prefetch_selections(
                            target_population_model.households.filter(
                                target_population_model.final_list_targeting_criteria.get_query()
                            ),
                            target_population_model,
                        )
                        .order_by("created_at")
                        .distinct()
                    )
                else:
                    return (
                        prefetch_selections(
                            target_population_model.households,
                            target_population_model,
                        )
                        .order_by("created_at")
                        .all()
                    )
            return (
                prefetch_selections(
                    target_population_model.households.filter(
                        targeting_criteria_object_type_to_query(targeting_criteria, target_population_model.program)
                    ),
                    target_population_model,
                )
                .order_by("created_at")
                .all()
                .distinct()
            )
        return (
            target_population_model.final_list.order_by("created_at")
            .prefetch_related(
                Prefetch(
                    "selections",
                    queryset=target_models.HouseholdSelection.objects.filter(target_population=target_population_model),
                )
            )
            .all()
        )

    def resolve_golden_record_by_targeting_criteria(parent, info, targeting_criteria, program, excluded_ids, **kwargs):
        household_queryset = Household.objects
        return prefetch_selections(
            household_queryset.filter(
                targeting_criteria_object_type_to_query(targeting_criteria, program, excluded_ids)
            )
        ).distinct()
