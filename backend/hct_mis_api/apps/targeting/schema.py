from typing import Any, Dict, List, Union

from django.db.models import Prefetch, QuerySet

import graphene
from graphene import relay

import hct_mis_api.apps.targeting.models as target_models
from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    decode_and_get_object,
    decode_id_string,
    map_unicef_ids_to_households_unicef_ids,
)
from hct_mis_api.apps.household.models import Household
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.targeting.filters import HouseholdFilter
from hct_mis_api.apps.targeting.graphql_types import (
    TargetingCriteriaObjectType,
    TargetPopulationNode,
)
from hct_mis_api.apps.targeting.validators import TargetingCriteriaInputValidator


def targeting_criteria_object_type_to_query(
    targeting_criteria_object_type, program: Union[str, Program], excluded_ids=""
):
    TargetingCriteriaInputValidator.validate(targeting_criteria_object_type)
    given_program: str
    if not isinstance(program, Program):
        given_program = decode_and_get_object(program, Program, True)
    else:
        given_program = program
    targeting_criteria_querying = target_models.TargetingCriteriaQueryingBase(
        [], excluded_household_ids=map_unicef_ids_to_households_unicef_ids(excluded_ids)
    )
    for rule in targeting_criteria_object_type.get("rules", []):
        targeting_criteria_rule_querying = target_models.TargetingCriteriaRuleQueryingBase(
            filters=[], individuals_filters_blocks=[]
        )
        for filter_dict in rule.get("filters", []):
            targeting_criteria_rule_querying.filters.append(target_models.TargetingCriteriaRuleFilter(**filter_dict))
        for individuals_filters_block_dict in rule.get("individuals_filters_blocks", []):
            individuals_filters_block = target_models.TargetingIndividualRuleFilterBlockBase(
                [], not given_program.individual_data_needed
            )
            targeting_criteria_rule_querying.individuals_filters_blocks.append(individuals_filters_block)
            for individual_block_filter_dict in individuals_filters_block_dict.get("individual_block_filters", []):
                individuals_filters_block.individual_block_filters.append(
                    target_models.TargetingIndividualBlockRuleFilter(**individual_block_filter_dict)
                )
        targeting_criteria_querying.rules.append(targeting_criteria_rule_querying)
    return targeting_criteria_querying.get_query()


def prefetch_selections(qs, target_population=None) -> QuerySet:
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
    target_population_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        target_population=graphene.Argument(graphene.ID, required=True),
        filterset_class=HouseholdFilter,
        permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_DETAILS),),
    )
    target_population_status_choices = graphene.List(ChoiceObject)

    def resolve_target_population_status_choices(self, info, **kwargs) -> List[Dict[str, Any]]:
        return [{"name": name, "value": value} for value, name in target_models.TargetPopulation.STATUS_CHOICES]

    def resolve_target_population_households(parent, info, target_population, **kwargs) -> QuerySet:
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(pk=target_population_id)
        return prefetch_selections(target_population_model.household_list, target_population_model)

    def resolve_golden_record_by_targeting_criteria(
        parent, info, targeting_criteria, program, excluded_ids, **kwargs
    ) -> QuerySet:
        household_queryset = Household.objects
        return prefetch_selections(
            household_queryset.filter(
                targeting_criteria_object_type_to_query(targeting_criteria, program, excluded_ids)
            )
        ).distinct()
