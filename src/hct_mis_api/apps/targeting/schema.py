import graphene
from graphene import relay

from hct_mis_api.apps.account.permissions import (
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.targeting.filters import TargetPopulationFilter
from hct_mis_api.apps.targeting.graphql_types import TargetPopulationNode


class Query(graphene.ObjectType):
    # TODO: deprecated will remove after data migrations
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoPermissionFilterConnectionField(
        TargetPopulationNode,
        filterset_class=TargetPopulationFilter,
        permission_classes=(hopePermissionClass(Permissions.TARGETING_VIEW_LIST),),
    )
