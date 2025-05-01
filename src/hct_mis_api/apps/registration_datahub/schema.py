import json
from typing import Any

import graphene
from graphene import relay
from graphene_django import DjangoObjectType

from hct_mis_api.apps.core.extended_connection import ExtendedConnection
from hct_mis_api.apps.core.schema import ChoiceObject
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.household.models import (
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DocumentType,
    PendingDocument,
    PendingIndividualIdentity,
)
from hct_mis_api.apps.registration_data.models import (
    ImportData,
    KoboImportData,
    RegistrationDataImportDatahub,
)


class ImportedDocumentNode(DjangoObjectType):
    country = graphene.String(description="Document country")
    photo = graphene.String(description="Photo url")

    def resolve_country(self, info: Any) -> str:
        return getattr(self.country, "name", "")

    def resolve_photo(self, info: Any) -> str | None:
        if self.photo:
            return self.photo.url
        return None

    class Meta:
        model = PendingDocument
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


class ImportedIndividualIdentityNode(DjangoObjectType):
    partner = graphene.String(description="Partner")
    country = graphene.String(description="Country")

    @staticmethod
    def resolve_country(parent: PendingIndividualIdentity, info: Any) -> str:
        return getattr(parent.country, "name", "")

    class Meta:
        model = PendingIndividualIdentity
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = ExtendedConnection


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

    @staticmethod
    def resolve_xlsx_validation_errors(parent: ImportData, info: Any) -> list[str]:
        errors = []
        if parent.validation_errors:
            errors.extend(json.loads(parent.validation_errors))
        return errors


class KoboImportDataNode(DjangoObjectType):
    kobo_validation_errors = graphene.List(KoboErrorNode)

    class Meta:
        model = KoboImportData
        filter_fields = []
        interfaces = (relay.Node,)

    def resolve_kobo_validation_errors(self, info: Any) -> list[str]:
        if not self.validation_errors:
            return []
        return json.loads(self.validation_errors)


class ImportedDocumentTypeNode(DjangoObjectType):
    class Meta:
        model = DocumentType


class Query(graphene.ObjectType):
    registration_data_import_datahub = relay.Node.Field(RegistrationDataImportDatahubNode)
    import_data = relay.Node.Field(ImportDataNode)
    kobo_import_data = relay.Node.Field(KoboImportDataNode)
    deduplication_batch_status_choices = graphene.List(ChoiceObject)
    deduplication_golden_record_status_choices = graphene.List(ChoiceObject)

    def resolve_deduplication_batch_status_choices(self, info: Any) -> list[dict[str, Any]]:
        return to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE)

    def resolve_deduplication_golden_record_status_choices(self, info: Any) -> list[dict[str, Any]]:
        return to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE)
