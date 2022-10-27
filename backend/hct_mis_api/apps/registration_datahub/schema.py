import json
from datetime import date

from django.db.models import Prefetch, Q

import graphene
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from graphene import relay
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from hct_mis_api.apps.account.permissions import (
    BaseNodePermissionMixin,
    DjangoPermissionFilterConnectionField,
    Permissions,
    hopePermissionClass,
)
from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import (
    encode_ids,
    get_model_choices_fields,
    resolve_flex_fields_choices_to_string,
    to_choice_object,
)
from hct_mis_api.apps.household.models import (
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DUPLICATE,
    DUPLICATE_IN_BATCH,
    NEEDS_ADJUDICATION,
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
)
from hct_mis_api.apps.registration_datahub.filters import (
    ImportedHouseholdFilter,
    ImportedIndividualFilter,
)
from hct_mis_api.apps.registration_datahub.models import (
    ImportData,
    ImportedDocument,
    ImportedDocumentType,
    ImportedHousehold,
    ImportedIndividual,
    ImportedIndividualIdentity,
    ImportedIndividualRoleInHousehold,
    KoboImportData,
    RegistrationDataImportDatahub,
)
from hct_mis_api.apps.utils.schema import Arg, FlexFieldsScalar


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


class ImportedHouseholdNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.RDI_VIEW_DETAILS,
        ),
    )
    flex_fields = Arg()
    country_origin = graphene.String(description="Country origin name")
    country = graphene.String(description="Country name")
    has_duplicates = graphene.Boolean(
        description="Mark household if any of individuals contains one of these statuses "
        "‘Needs adjudication’, ‘Duplicate in batch’ and ‘Duplicate’"
    )
    import_id = graphene.String()

    def resolve_country(parent, info):
        return parent.country.name

    def resolve_country_origin(parent, info):
        return parent.country_origin.name

    def resolve_has_duplicates(parent, info):
        return parent.individuals.filter(
            Q(deduplication_batch_status=DUPLICATE_IN_BATCH)
            | Q(deduplication_golden_record_status__in=(DUPLICATE, NEEDS_ADJUDICATION))
        ).exists()

    def resolve_flex_fields(parent, info):
        return resolve_flex_fields_choices_to_string(parent)

    def resolve_individuals(parent, info):
        imported_individuals_ids = list(parent.individuals.values_list("id", flat=True))
        collectors_ids = list(
            parent.individuals_and_roles.filter(role__in=[ROLE_PRIMARY, ROLE_ALTERNATE]).values_list(
                "individual_id", flat=True
            )
        )
        ids = list(set(imported_individuals_ids + collectors_ids))

        return ImportedIndividual.objects.filter(id__in=ids).prefetch_related(
            Prefetch(
                "households_and_roles",
                queryset=ImportedIndividualRoleInHousehold.objects.filter(household=parent.id),
            )
        )

    def resolve_import_id(parent, info):
        row = ""
        resp = str(parent.mis_unicef_id) if parent.mis_unicef_id else str(parent.id)

        if parent.kobo_asset_id:
            row = f" (Kobo {parent.kobo_asset_id})"
        if parent.row_id:
            row = f" (XLS row {parent.row_id})"

        return resp + row

    class Meta:
        model = ImportedHousehold
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualNode(BaseNodePermissionMixin, DjangoObjectType):
    permission_classes = (
        hopePermissionClass(
            Permissions.RDI_VIEW_DETAILS,
        ),
    )
    flex_fields = FlexFieldsScalar()
    estimated_birth_date = graphene.Boolean(required=False)
    role = graphene.String()
    relationship = graphene.String()
    deduplication_batch_results = graphene.List(DeduplicationResultNode)
    deduplication_golden_record_results = graphene.List(DeduplicationResultNode)
    observed_disability = graphene.List(graphene.String)
    age = graphene.Int()
    import_id = graphene.String()
    phone_no_valid = graphene.Boolean()
    phone_no_alternative_valid = graphene.Boolean()

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

    def resolve_flex_fields(parent, info):
        return resolve_flex_fields_choices_to_string(parent)

    @staticmethod
    def resolve_age(parent, info):
        return parent.age

    def resolve_import_id(parent, info):
        row = ""
        resp = str(parent.mis_unicef_id) if parent.mis_unicef_id else str(parent.id)

        if parent.kobo_asset_id:
            row = f" (Kobo {parent.kobo_asset_id})"
        if parent.row_id:
            row = f" (XLS row {parent.row_id})"

        return resp + row

    def resolve_phone_no_valid(parent, info):
        return parent.phone_no_valid

    def resolve_phone_no_alternative_valid(parent, info):
        return parent.phone_no_alternative_valid

    class Meta:
        model = ImportedIndividual
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection
        convert_choices_to_enum = get_model_choices_fields(
            ImportedIndividual,
            excluded=[
                "seeing_disability",
                "hearing_disability",
                "physical_disability",
                "memory_disability",
                "selfcare_disability",
                "comms_disability",
                "work_status",
                "collect_individual_data",
            ],
        )


class RegistrationDataImportDatahubNode(DjangoObjectType):
    class Meta:
        model = RegistrationDataImportDatahub
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class KoboErrorNode(graphene.ObjectType):
    header = graphene.String()
    message = graphene.String()


class XlsxRowErrorNode(graphene.ObjectType):
    row_number = graphene.Int()
    header = graphene.String()
    message = graphene.String()


class ImportDataNode(DjangoObjectType):
    xlsx_validation_errors = graphene.List(XlsxRowErrorNode)

    class Meta:
        model = ImportData
        filter_fields = []
        interfaces = (relay.Node,)

    def resolve_xlsx_validation_errors(parrent, info):
        if not parrent.validation_errors:
            return []
        return json.loads(parrent.validation_errors)


class KoboImportDataNode(DjangoObjectType):
    kobo_validation_errors = graphene.List(KoboErrorNode)

    class Meta:
        model = KoboImportData
        filter_fields = []
        interfaces = (relay.Node,)

    def resolve_kobo_validation_errors(parrent, info):
        if not parrent.validation_errors:
            return []
        return json.loads(parrent.validation_errors)


class ImportedDocumentTypeNode(DjangoObjectType):
    class Meta:
        model = ImportedDocumentType


class ImportedDocumentNode(DjangoObjectType):
    country = graphene.String(description="Document country")
    photo = graphene.String(description="Photo url")

    def resolve_country(parent, info):
        return getattr(parent.country, "name", parent.country)

    def resolve_photo(parent, info):
        if parent.photo:
            return parent.photo.url
        return

    class Meta:
        model = ImportedDocument
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualIdentityNode(DjangoObjectType):
    type = graphene.String(description="Agency type")
    country = graphene.String(description="Agency country")

    def resolve_type(parent, info):
        return parent.agency.type

    def resolve_country(parent, info):
        return getattr(parent.agency.country, "name", parent.agency.country)

    class Meta:
        model = ImportedIndividualIdentity
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class Query(graphene.ObjectType):
    imported_household = relay.Node.Field(ImportedHouseholdNode)
    all_imported_households = DjangoPermissionFilterConnectionField(
        ImportedHouseholdNode,
        filterset_class=ImportedHouseholdFilter,
        permission_classes=(
            hopePermissionClass(
                Permissions.RDI_VIEW_DETAILS,
            ),
        ),
    )
    registration_data_import_datahub = relay.Node.Field(RegistrationDataImportDatahubNode)
    all_registration_data_imports_datahub = DjangoFilterConnectionField(RegistrationDataImportDatahubNode)
    imported_individual = relay.Node.Field(ImportedIndividualNode)
    all_imported_individuals = DjangoPermissionFilterConnectionField(
        ImportedIndividualNode,
        filterset_class=ImportedIndividualFilter,
        permission_classes=(
            hopePermissionClass(
                Permissions.RDI_VIEW_DETAILS,
            ),
        ),
    )
    import_data = relay.Node.Field(ImportDataNode)
    kobo_import_data = relay.Node.Field(KoboImportDataNode)
    deduplication_batch_status_choices = graphene.List(ChoiceObject)
    deduplication_golden_record_status_choices = graphene.List(ChoiceObject)

    def resolve_deduplication_batch_status_choices(self, info, **kwargs):
        return to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE)

    def resolve_deduplication_golden_record_status_choices(self, info, **kwargs):
        return to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE)
