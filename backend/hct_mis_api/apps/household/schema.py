import graphene
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
    ModelMultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.filters import AgeRangeFilter, IntegerRangeFilter
from core.extended_connection import ExtendedConnection
from household.models import Household, Individual


class HouseholdFilter(FilterSet):
    business_area = CharFilter(field_name="location__business_area__slug")
    family_size = IntegerRangeFilter(field_name="family_size")

    class Meta:
        model = Household
        fields = {
            "business_area": ["exact", "icontains"],
            "nationality": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "representative__full_name": ["exact", "icontains"],
            "head_of_household__full_name": ["exact", "icontains"],
            "household_ca_id": ["exact"],
            "family_size": ["range", "lte", "gte"],
            "target_populations": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            "age",
            "sex",
            "household__id",
            "id",
            "household_ca_id",
            "family_size",
            "head_of_household__full_name",
            "location__title",
            "residence_status",
            "registration_data_import_id__",
        )
    )


class IndividualFilter(FilterSet):
    business_area = CharFilter(
        field_name="household__location__business_area__slug",
    )
    age = AgeRangeFilter(field_name="dob")
    sex = ModelMultipleChoiceFilter(
        to_field_name="sex", queryset=Individual.objects.all(),
    )

    class Meta:
        model = Individual
        fields = {
            "business_area": ["exact"],
            "full_name": ["exact", "icontains"],
            "age": ["range", "lte", "gte"],
            "sex": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            "id",
            "full_name",
            "household__id",
            "dob",
            "sex",
            "household__location__title",
        )
    )


class HouseholdNode(DjangoObjectType):
    class Meta:
        model = Household
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class IndividualNode(DjangoObjectType):
    class Meta:
        model = Individual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    household = relay.Node.Field(HouseholdNode)
    all_households = DjangoFilterConnectionField(
        HouseholdNode, filterset_class=HouseholdFilter,
    )
    individual = relay.Node.Field(IndividualNode)
    all_individuals = DjangoFilterConnectionField(
        IndividualNode, filterset_class=IndividualFilter,
    )
