import graphene
from django_filters import (
    FilterSet,
    OrderingFilter,
    ModelMultipleChoiceFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.filters import AgeRangeFilter, IntegerRangeFilter
from core.schema import ExtendedConnection
from registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
)


class ImportedHouseholdFilter(FilterSet):
    family_size = IntegerRangeFilter(field_name="family_size")

    class Meta:
        model = ImportedHousehold
        fields = {
            "nationality": ["exact", "icontains"],
            "address": ["exact", "icontains"],
            "representative__full_name": ["exact", "icontains"],
            "head_of_household__full_name": ["exact", "icontains"],
            "household_ca_id": ["exact"],
            "family_size": ["range", "lte", "gte"],
        }

    order_by = OrderingFilter(
        fields=(
            "household_ca_id",
            "residence_status",
            "nationality",
            "family_size",
            "representative__full_name",
            "registration_data_import_id__name",
        )
    )


class ImportedIndividualFilter(FilterSet):
    age = AgeRangeFilter(field_name="dob")
    sex = ModelMultipleChoiceFilter(
        to_field_name="sex", queryset=ImportedIndividual.objects.all(),
    )

    class Meta:
        model = ImportedIndividual
        fields = {
            "full_name": ["exact", "icontains"],
            "age": ["range", "lte", "gte"],
            "sex": ["exact"],
        }

    order_by = OrderingFilter(
        fields=("individual__id", "full_name", "household__id", "age", "sex",)
    )


class ImportedHouseholdNode(DjangoObjectType):
    class Meta:
        model = ImportedHousehold
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualNode(DjangoObjectType):
    class Meta:
        model = ImportedIndividual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class RegistrationDataImportDatahubNode(DjangoObjectType):
    class Meta:
        model = RegistrationDataImportDatahub
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    imported_household = relay.Node.Field(ImportedHouseholdNode)
    all_imported_households = DjangoFilterConnectionField(
        ImportedHouseholdNode, filterset_class=ImportedHouseholdFilter,
    )
    registration_data_import_datahub = relay.Node.Field(
        RegistrationDataImportDatahubNode,
    )
    all_registration_data_imports_datahub = DjangoFilterConnectionField(
        RegistrationDataImportDatahubNode,
    )
    imported_individual = relay.Node.Field(ImportedIndividualNode)
    all_imported_individuals = DjangoFilterConnectionField(
        ImportedIndividualNode, filterset_class=ImportedIndividualFilter,
    )
