import django_filters
import graphene
from django_filters import (
    FilterSet,
    OrderingFilter,
    ModelMultipleChoiceFilter,
    CharFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from core.utils import decode_id_string
from core.filters import AgeRangeFilter, IntegerRangeFilter
from registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
    ImportData,
)


class ImportedHouseholdFilter(FilterSet):
    family_size = IntegerRangeFilter(field_name="family_size")
    rdi_id = CharFilter(
        field_name="household__programs__name", method="filter_rdi_id"
    )

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
            "id",
            "household_ca_id",
            "head_of_household__full_name",
            "residence_status",
            "nationality",
            "family_size",
            "location",
            "registration_date",
            "representative__full_name",
            "registration_data_import_id__name",
        )
    )

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(
            registration_data_import_id__hct_id=decode_id_string(value)
        )


class ImportedIndividualFilter(FilterSet):
    age = AgeRangeFilter(field_name="dob")
    sex = ModelMultipleChoiceFilter(
        to_field_name="sex", queryset=ImportedIndividual.objects.all(),
    )
    rdi_id = CharFilter(
        field_name="household__programs__name", method="filter_rdi_id"
    )
    household = django_filters.CharFilter(
        field_name="household__id", method="filter_household"
    )

    class Meta:
        model = ImportedIndividual
        fields = {
            "full_name": ["exact", "icontains"],
            "age": ["range", "lte", "gte"],
            "sex": ["exact"],
            "household": ["exact"],
        }

    order_by = OrderingFilter(
        fields=(
            "id",
            "full_name",
            "household__id",
            "age",
            "sex",
            "work_status",
            "dob",
        )
    )

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(
            registration_data_import_id__hct_id=decode_id_string(value)
        )

    def filter_household(self, queryset, model_field, value):
        return queryset.filter(household__id=decode_id_string(value))


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
