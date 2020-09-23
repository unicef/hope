from datetime import date

import graphene
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django_filters import (
    FilterSet,
    OrderingFilter,
    CharFilter,
    BooleanFilter,
)
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from core.extended_connection import ExtendedConnection
from core.schema import ChoiceObject
from core.utils import decode_id_string, to_choice_object, encode_ids
from household.models import (
    ROLE_NO_ROLE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DUPLICATE,
    NEEDS_ADJUDICATION,
    DUPLICATE_IN_BATCH,
    DEDUPLICATION_BATCH_STATUS_CHOICE,
)
from registration_datahub.models import (
    ImportedHousehold,
    ImportedIndividual,
    RegistrationDataImportDatahub,
    ImportData,
    ImportedDocumentType,
    ImportedDocument,
    ImportedIndividualIdentity,
)


class DeduplicationResultNode(graphene.ObjectType):
    hit_id = graphene.ID()
    full_name = graphene.String()
    score = graphene.Float()
    proximity_to_score = graphene.Float()
    location = graphene.String()
    age = graphene.Int()

    def resolve_age(self, info):
        date_of_birth = self.get("dob")
        if date_of_birth:
            today = date.today()
            return relativedelta(today, parse(date_of_birth)).years

    def resolve_location(self, info):
        return self.get("location") or "Not provided"


class ImportedHouseholdFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")

    class Meta:
        model = ImportedHousehold
        fields = ()

    order_by = OrderingFilter(fields=("id", "head_of_household", "size", "registration_date",))

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(registration_data_import__hct_id=decode_id_string(value))


class ImportedIndividualFilter(FilterSet):
    rdi_id = CharFilter(method="filter_rdi_id")
    duplicates_only = BooleanFilter(method="filter_duplicates_only")

    class Meta:
        model = ImportedIndividual
        fields = ("household",)

    order_by = OrderingFilter(
        fields=(
            "id",
            "full_name",
            "birth_date",
            "sex",
            "deduplication_batch_status",
            "deduplication_golden_record_status",
        )
    )

    def filter_rdi_id(self, queryset, model_field, value):
        return queryset.filter(registration_data_import__hct_id=decode_id_string(value))

    def filter_duplicates_only(self, queryset, model_field, value):
        if value is True:
            return queryset.filter(
                Q(deduplication_golden_record_status=DUPLICATE) | Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            )
        return queryset


class ImportedHouseholdNode(DjangoObjectType):
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    has_duplicates = graphene.Boolean(
        description="Mark household if any of individuals contains one of these statuses "
        "‘Needs adjudication’, ‘Duplicate in batch’ and ‘Duplicate’"
    )

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_origin(parent, info):
        return parent.country_origin.name

    def resolve_has_duplicates(parent, info):
        return parent.individuals.filter(
            Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            | Q(deduplication_golden_record_status__in=(DUPLICATE, NEEDS_ADJUDICATION))
        ).exists()

    class Meta:
        model = ImportedHousehold
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualNode(DjangoObjectType):
    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    relationship = graphene.String()
    deduplication_batch_results = graphene.List(DeduplicationResultNode)
    deduplication_golden_record_results = graphene.List(DeduplicationResultNode)

    def resolve_role(parent, info):
        role = parent.households_and_roles.first()
        if role is not None:
            return role.role
        return ROLE_NO_ROLE

    def resolve_deduplication_batch_results(parent, info):
        key = "duplicates" if parent.deduplication_batch_status == DUPLICATE_IN_BATCH else "possible_duplicates"
        results = parent.deduplication_batch_results.get(key, {})
        return encode_ids(results, "ImportedIndividual", "hit_id")

    def resolve_deduplication_golden_record_results(parent, info):
        key = "duplicates" if parent.deduplication_golden_record_status == DUPLICATE else "possible_duplicates"
        results = parent.deduplication_golden_record_results.get(key, {})
        return encode_ids(results, "Individual", "hit_id")

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


class ImportedIndividualIdentityNode(DjangoObjectType):
    type = graphene.String(description="Agency type")

    def resolve_type(parent, info):
        return parent.agency.type

    class Meta:
        model = ImportedIndividualIdentity


class XlsxRowErrorNode(graphene.ObjectType):
    row_number = graphene.Int()
    header = graphene.String()
    message = graphene.String()


class KoboErrorNode(graphene.ObjectType):
    header = graphene.String()
    message = graphene.String()


class Query(graphene.ObjectType):
    imported_household = relay.Node.Field(ImportedHouseholdNode)
    all_imported_households = DjangoFilterConnectionField(
        ImportedHouseholdNode, filterset_class=ImportedHouseholdFilter,
    )
    registration_data_import_datahub = relay.Node.Field(RegistrationDataImportDatahubNode)
    all_registration_data_imports_datahub = DjangoFilterConnectionField(RegistrationDataImportDatahubNode)
    imported_individual = relay.Node.Field(ImportedIndividualNode)
    all_imported_individuals = DjangoFilterConnectionField(
        ImportedIndividualNode, filterset_class=ImportedIndividualFilter,
    )
    import_data = relay.Node.Field(ImportDataNode)
    deduplication_batch_status_choices = graphene.List(ChoiceObject)
    deduplication_golden_record_status_choices = graphene.List(ChoiceObject)

    def resolve_deduplication_batch_status_choices(self, info, **kwargs):
        return to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE)

    def resolve_deduplication_golden_record_status_choices(self, info, **kwargs):
        return to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE)
