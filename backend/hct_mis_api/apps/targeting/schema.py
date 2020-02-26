import django_filters
import graphene
import targeting.models as models
from core.schema import ExtendedConnection
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


class TargetPopulationFilter(django_filters.FilterSet):
    class Meta:
        model = models.TargetPopulation
        fields = (
            "created_by",
            "status",
            "num_individuals_household",
        )
        filter_overrides = {
            models.IntegerRangeField: {
                'filter_class': django_filters.NumericRangeFilter,
            }
        }

    order_by = django_filters.OrderingFilter(fields=("created_by",))


class TargetPopulationNode(DjangoObjectType):
    class Meta:
        model = models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(
        TargetPopulationNode, filterset_class=TargetPopulationFilter)
