import graphene
from django_filters import (
    FilterSet,
    OrderingFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
    ImportData,
)


class ImportedHouseholdFilter(FilterSet):
    class Meta:
        model = ImportedHousehold
        fields = ()

    order_by = OrderingFilter(
        fields=("id", "head_of_household", "size", "registration_date",)
    )


class ImportedIndividualFilter(FilterSet):
    class Meta:
        model = ImportedIndividual
        fields = ()

    order_by = OrderingFilter(fields=("id", "full_name", "birth_date", "sex",))


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


class ImportDataNode(DjangoObjectType):
    class Meta:
        model = ImportData
        filter_fields = []
        interfaces = (relay.Node,)


class XlsxRowErrorNode(graphene.ObjectType):
    row_number = graphene.Int()
    header = graphene.String()
    message = graphene.String()


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
    import_data = relay.Node.Field(ImportDataNode)
