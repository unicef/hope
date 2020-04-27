import graphene
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from core.utils import decode_id_string
from registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
    ImportData,
    ImportedDocumentType,
    ImportedDocument,
)


class ImportedHouseholdFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")

    class Meta:
        model = ImportedHousehold
        fields = ()

    order_by = OrderingFilter(
        fields=("id", "head_of_household", "size", "registration_date",)
    )

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(
            registration_data_import__hct_id=decode_id_string(value)
        )


class ImportedIndividualFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")

    class Meta:
        model = ImportedIndividual
        fields = ("household",)

    order_by = OrderingFilter(fields=("id", "full_name", "birth_date", "sex",))

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(
            registration_data_import__hct_id=decode_id_string(value)
        )


class ImportedHouseholdNode(DjangoObjectType):

    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")

    def resolve_country(parrent, info):
        return parrent.country.name

    def resolve_country_origin(parrent, info):
        return parrent.country_origin.name

    class Meta:
        model = ImportedHousehold
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualNode(DjangoObjectType):
    estimated_birth_date = graphene.Boolean(required=False)

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


class ImportedDocumentTypeNode(DjangoObjectType):
    class Meta:
        model = ImportedDocumentType


class ImportedDocumentNode(DjangoObjectType):
    class Meta:
        model = ImportedDocument
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


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
