import functools
import json

import django_filters
import graphene
import targeting.models as target_models
from core.permissions import is_authenticated
from core.schema import ExtendedConnection
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from household.models import Household
from registration_data.models import RegistrationDataImport


class IntakeGroupType(DjangoObjectType):
    class Meta:
        model = RegistrationDataImport
        fields = ("name", )


class HouseHoldType(DjangoObjectType):
    class Meta:
        model = Household
        fields = (
            "household_ca_id",
            "head_of_household",
            "family_size",
            "address",
            "location",
            "registration_data_import_id",
        )


class TargetPopulationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name",
                                     lookup_expr="icontains")
    created_by_name = django_filters.CharFilter(
        field_name="created_by", method='filter_created_by_name')
    num_individuals_min = django_filters.NumberFilter(
        field_name="target_filters__num_individuals_min",
        lookup_expr="gte")
    num_individuals_max = django_filters.NumberFilter(
        field_name="target_filters__num_individuals_max",
        lookup_expr="lte")
    # TODO(codecakes): waiting on dist to school and adminlevel clarification.

    @staticmethod
    def filter_created_by_name(queryset, model_field, value):
        """Gets full name of the associated user from query."""
        return queryset.filter(**{
            f'{model_field}__first_name__icontains': value,
        }).filter(**{
            f'{model_field}__last_name__icontains': value,
        }).filter(**{
            f'{model_field}__full_name__icontains': value,
        })

    class Meta:
        model = target_models.TargetPopulation
        fields = (
            "name",
            "status",
            "created_by_name",
            "created_at",
            "last_edited_at",
            "households",
            "target_filters",
        )

        filter_overrides = {
            target_models.IntegerRangeField: {
                'filter_class': django_filters.NumericRangeFilter,
            },
            target_models.models.DateTimeField: {
                'filter_class': django_filters.DateTimeFilter,
            },
        }

    # TODO(codecakes): how to order?
    order_by = django_filters.OrderingFilter(fields=("created_at", ))


class TargetPopulationNode(DjangoObjectType):
    class Meta:
        model = target_models.TargetPopulation
        interfaces = (relay.Node, )
        connection_class = ExtendedConnection
        filterset_class = TargetPopulationFilter


class Query(graphene.ObjectType):
    target_population = relay.Node.Field(TargetPopulationNode)
    all_target_population = DjangoFilterConnectionField(TargetPopulationNode)
    target_filers = graphene.List(
        HouseHoldType,
        serialized_list=graphene.String(),
        description="json dump of filters containing key value pairs.")

    @classmethod
    @is_authenticated
    def resolve_target_filters(cls, info, serialized_list):
        """Resolver for target_filters.
        args:
            info: object, HTTPRequestObject.
            serialized_list: list, check below.

        Arguments in serialized_list are of type:
        intake_group = graphene.Field(IntakeGroupType)
        sex = graphene.String()
        age_min = graphene.Int()
        age_max = graphene.Int()
        # school_distance_min = graphene.Int()
        # school_distance_max = graphene.Int()
        num_individuals_household_min = graphene.Int()
        num_individuals_household_max = graphene.Int()
        """
        filter_lists = json.loads(serialized_list)
        queryset = functools.reduce(
            lambda f_1, f_2: f_1 | f_2,
            cls.get_households_from_filter(filter_lists))
        return queryset.all()

    @staticmethod
    def get_households_from_filter(filter_lists):
        for filter_list in filter_lists:
            # TODO(codecakes): Add dist to school field once mapping known.
            yield Household.objects.filter(
                **{
                    "head_of_household__sex":
                    filter_list["sex"],
                    "family_size__gte":
                    filter_list["num_individuals_household_min"],
                    "family_size__lte":
                    filter_list["num_individuals_household_max"],
                    "head_of_household__age__gte":
                    filter_list["age_min"],
                    "head_of_household__age_lte":
                    filter_list["age_max"],
                    "registration_data_import_id__name":
                    filter_list["intake_group"],
                })
