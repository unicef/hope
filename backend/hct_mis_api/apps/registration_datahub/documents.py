from typing import TYPE_CHECKING, Dict, Optional, Type

from django.conf import settings
from django.db.models import Q, QuerySet

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from hct_mis_api.apps.core.es_analyzers import name_synonym_analyzer, phonetic_analyzer
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual
from hct_mis_api.apps.utils.elasticsearch_utils import DEFAULT_SCRIPT

if TYPE_CHECKING:
    from hct_mis_api.apps.geo.models import Area


index_settings = {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "similarity": {
        "default": {
            "type": "scripted",
            "script": {
                "source": DEFAULT_SCRIPT,
            },
        },
    },
}


class ImportedIndividualDocument(Document):
    id = fields.KeywordField(boost=0)
    given_name = fields.TextField(
        analyzer=name_synonym_analyzer, fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)}
    )
    middle_name = fields.TextField(analyzer=phonetic_analyzer)
    family_name = fields.TextField(fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)})
    full_name = fields.TextField(analyzer=phonetic_analyzer)
    birth_date = fields.DateField(similarity="boolean")
    phone_no = fields.KeywordField("phone_no.__str__", similarity="boolean")
    phone_no_alternative = fields.KeywordField("phone_no_alternative.__str__", similarity="boolean")
    business_area = fields.KeywordField(similarity="boolean", attr="business_area")
    admin1 = fields.KeywordField()
    admin2 = fields.KeywordField()
    registration_data_import_id = fields.KeywordField(
        "registration_data_import.id.__str__",
    )
    documents = fields.ObjectField(
        properties={
            "number": fields.KeywordField(attr="document_number", similarity="boolean"),
            "key ": fields.KeywordField(attr="type.key", similarity="boolean"),
            "country": fields.KeywordField(attr="country.alpha3", similarity="boolean"),
        }
    )
    identities = fields.ObjectField(
        properties={
            "number": fields.KeywordField(attr="document_number", similarity="boolean"),
            "partner": fields.KeywordField(attr="partner", similarity="boolean"),
        }
    )

    def prepare_admin1(self, instance: ImportedIndividual) -> Optional["Area"]:
        household = instance.household
        if household:
            return instance.household.admin1
        return None

    def prepare_admin2(self, instance: ImportedIndividual) -> Optional["Area"]:
        household = instance.household
        if household:
            return instance.household.admin2
        return None

    def prepare_hash_key(self, instance: ImportedIndividual) -> str:
        return instance.get_hash_key

    def prepare_business_area(self, instance: ImportedIndividual) -> str:
        return instance.registration_data_import.business_area_slug

    class Django:
        model = ImportedIndividual

        fields = [
            "relationship",
            "sex",
        ]


@registry.register_document
class ImportedIndividualDocumentAfghanistan(ImportedIndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}importedindividuals_afghanistan"
        settings = index_settings

    def get_queryset(self) -> QuerySet:
        return ImportedIndividual.objects.filter(registration_data_import__business_area_slug="afghanistan")


@registry.register_document
class ImportedIndividualDocumentUkraine(ImportedIndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}importedindividuals_ukraine"
        settings = index_settings

    def get_queryset(self) -> QuerySet:
        return ImportedIndividual.objects.filter(registration_data_import__business_area_slug="ukraine")


@registry.register_document
class ImportedIndividualDocumentOthers(ImportedIndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}importedindividuals_others"
        settings = index_settings

    def get_queryset(self) -> QuerySet:
        return ImportedIndividual.objects.exclude(
            Q(registration_data_import__business_area_slug="ukraine")
            | Q(registration_data_import__business_area_slug="afghanistan")
        )


def get_imported_individual_doc(business_area_slug: str) -> Type[ImportedIndividualDocument]:
    documents: Dict[str, Type[ImportedIndividualDocument]] = {
        "afghanistan": ImportedIndividualDocumentAfghanistan,
        "ukraine": ImportedIndividualDocumentUkraine,
    }
    return documents.get(business_area_slug, ImportedIndividualDocumentOthers)
