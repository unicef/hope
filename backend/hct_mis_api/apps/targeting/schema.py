from typing import Any, Dict, List, Optional

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
from hct_mis_api.apps.core.utils import decode_id_string, to_choice_object
from hct_mis_api.apps.household.schema import HouseholdNode
from hct_mis_api.apps.targeting.filters import HouseholdFilter
from hct_mis_api.apps.targeting.graphql_types import TargetPopulationNode


def prefetch_selections(qs: QuerySet, target_population: Optional[target_models.TargetPopulation] = None) -> QuerySet:
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
    target_population_households = DjangoPermissionFilterConnectionField(
        HouseholdNode,
        target_population=graphene.Argument(graphene.ID, required=True),
        filterset_class=HouseholdFilter,
        permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_DETAILS),),
    )
    target_population_status_choices = graphene.List(ChoiceObject)
    all_active_target_populations = DjangoPermissionFilterConnectionField(
        TargetPopulationNode,
        permission_classes=(hopePermissionClass(Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST),),
    )

    def resolve_target_population_status_choices(self, info: Any, **kwargs: Any) -> List[Dict[str, Any]]:
        return to_choice_object(target_models.TargetPopulation.STATUS_CHOICES)

    def resolve_target_population_households(
        parent, info: Any, target_population: target_models.TargetPopulation, **kwargs: Any
    ) -> QuerySet:
        target_population_id = decode_id_string(target_population)
        target_population_model = target_models.TargetPopulation.objects.get(pk=target_population_id)
        return prefetch_selections(target_population_model.household_list, target_population_model)
