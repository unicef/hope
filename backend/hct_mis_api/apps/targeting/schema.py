import django_filters
import graphene
import targeting.models as target_models
from core.schema import ExtendedConnection
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField


class TargetPopulationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name",
                                     lookup_expr="icontains")
    created_by_name = django_filters.CharFilter(
        field_name="created_by", method='filter_created_by_name')
    min_num_individuals = django_filters.NumericRangeFilter(
        field_name="num_individuals_household", lookup_expr="gte")
    max_num_individuals = django_filters.NumericRangeFilter(
        field_name="num_individuals_household", lookup_expr="lte")

    @staticmethod
    def filter_created_by_name(self, queryset, model_field, value):
        """Gets full name of the associated user from query."""
        return queryset.filter(
            **{
                f'{model_field}__first_name__contains': value,
                f'{model_field}_last_name__contains': value,
            })

    class Meta:
        model = target_models.TargetPopulation
        fields = (
            "name",
            "status",
            "created_by_name",
            "created_at",
            "last_edited_at",
            "num_individuals_household",
            "households",
        )
        filter_overrides = {
            target_models.IntegerRangeField: {
                'filter_class': django_filters.NumericRangeFilter,
            },
            target_models.models.DateTimeField: {
                'filter_class': django_filters.DateTimeFilter,
            },
        }

    order_by = django_filters.OrderingFilter(fields=("created_by",))


class TargetPopulationNode(DjangoObjectType):
    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
