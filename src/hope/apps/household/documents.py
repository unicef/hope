from django.conf import settings
from django.db.models import Q, QuerySet
from django_elasticsearch_dsl import Document as ESDocument, fields
from django_elasticsearch_dsl.registries import registry

from hope.apps.core.es_analyzers import name_synonym_analyzer, phonetic_analyzer
from hope.apps.household.models import (
    Document,
    Household,
    Individual,
    IndividualIdentity,
    IndividualRoleInHousehold,
)
from hope.apps.utils.elasticsearch_utils import DEFAULT_SCRIPT

RelatedInstanceType = ESDocument | Household | IndividualIdentity | IndividualRoleInHousehold

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


class IndividualDocument(ESDocument):
    id = fields.KeywordField()  # The boost parameter on field mappings has been removed
    given_name = fields.TextField(
        analyzer=name_synonym_analyzer,
        fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)},
    )
    middle_name = fields.TextField(analyzer=phonetic_analyzer)
    family_name = fields.TextField(fields={"phonetic": fields.TextField(analyzer=phonetic_analyzer)})
    full_name = fields.TextField(analyzer=phonetic_analyzer)
    birth_date = fields.DateField()  # Before es 8, similarity parameter on DateField failed silently
    phone_no = fields.KeywordField("phone_no.__str__", similarity="boolean")
    phone_no_alternative = fields.KeywordField("phone_no_alternative.__str__", similarity="boolean")
    phone_no_text = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    phone_no_alternative_text = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    business_area = fields.KeywordField(similarity="boolean")
    admin1 = fields.KeywordField()
    admin2 = fields.KeywordField()
    unicef_id = fields.TextField()
    household = fields.ObjectField(
        properties={
            "unicef_id": fields.TextField(),
        }
    )
    documents = fields.ObjectField(
        properties={
            "number": fields.KeywordField(attr="document_number", similarity="boolean"),
            "key": fields.KeywordField(attr="type.key", similarity="boolean"),
            "country": fields.KeywordField(attr="country.iso_code3", similarity="boolean"),
        }
    )
    identities = fields.ObjectField(
        properties={
            "number": fields.KeywordField(similarity="boolean"),
            "partner": fields.KeywordField(attr="partner.name", similarity="boolean"),
        }
    )
    program_id = fields.KeywordField(attr="program.id")
    detail_id = fields.TextField()
    program_registration_id = fields.TextField()
    registration_data_import_id = fields.KeywordField(attr="registration_data_import.id")
    rdi_merge_status = fields.KeywordField()

    def prepare_phone_no_text(self, instance: Individual) -> str:
        return str(instance.phone_no).replace(" ", "")

    def prepare_phone_no_alternative_text(self, instance: Individual) -> str:
        return str(instance.phone_no).replace(" ", "")

    def prepare_admin1(self, instance: Individual) -> str | None:
        household = instance.household
        if household and household.admin1:
            return household.admin1.name
        return None

    def prepare_admin2(self, instance: Individual) -> str | None:
        household = instance.household
        if household and household.admin2:
            return household.admin2.name
        return None

    def prepare_hash_key(self, instance: Individual) -> str:
        return instance.get_hash_key

    def prepare_business_area(self, instance: Individual) -> str:
        return instance.business_area.slug

    class Django:
        model = Individual

        fields = [
            "relationship",
            "sex",
            "created_at",
            "updated_at",
        ]

        related_models = [Household, Document, IndividualIdentity]

    def get_instances_from_related(
        self, related_instance: RelatedInstanceType
    ) -> Individual | QuerySet[Individual] | None:
        if isinstance(related_instance, Document | IndividualIdentity):
            return related_instance.individual
        if isinstance(related_instance, Household):
            return related_instance.individuals.all()

        return None


@registry.register_document
class IndividualDocumentAfghanistan(IndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}individuals_afghanistan"
        settings = index_settings

    def get_queryset(self) -> QuerySet[Individual]:
        return Individual.all_merge_status_objects.filter(business_area__slug="afghanistan")


@registry.register_document
class IndividualDocumentUkraine(IndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}individuals_ukraine"
        settings = index_settings

    def get_queryset(self) -> QuerySet[Individual]:
        return Individual.all_merge_status_objects.filter(business_area__slug="ukraine")


@registry.register_document
class IndividualDocumentOthers(IndividualDocument):
    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}individuals_others"
        settings = index_settings

    def get_queryset(self) -> QuerySet[Individual]:
        return Individual.all_merge_status_objects.exclude(
            Q(business_area__slug="ukraine") | Q(business_area__slug="afghanistan")
        )


def get_individual_doc(
    business_area_slug: str,
) -> type[IndividualDocument]:
    documents: dict[str, type[IndividualDocument]] = {
        "afghanistan": IndividualDocumentAfghanistan,
        "ukraine": IndividualDocumentUkraine,
    }
    return documents.get(business_area_slug, IndividualDocumentOthers)


@registry.register_document
class HouseholdDocument(ESDocument):
    head_of_household = fields.ObjectField(
        properties={
            "unicef_id": fields.TextField(),
            "full_name": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "given_name": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "middle_name": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "family_name": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "phone_no_text": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "phone_no_alternative_text": fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10}),
            "documents": fields.ObjectField(
                properties={
                    "number": fields.KeywordField(attr="document_number", similarity="boolean"),
                    "key": fields.KeywordField(attr="type.key", similarity="boolean"),
                    "country": fields.KeywordField(attr="country.iso_code3", similarity="boolean"),
                }
            ),
        }
    )
    unicef_id = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    residence_status = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    admin1 = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    admin2 = fields.TextField(index_prefixes={"min_chars": 1, "max_chars": 10})
    business_area = fields.KeywordField(similarity="boolean")
    program_id = fields.KeywordField(attr="program.id")
    detail_id = fields.TextField()
    program_registration_id = fields.TextField()

    def prepare_admin1(self, household: Household) -> str | None:
        if household and household.admin1:
            return household.admin1.name
        return None

    def prepare_admin2(self, household: Household) -> str | None:
        if household and household.admin2:
            return household.admin2.name
        return None

    def prepare_business_area(self, instance: Household) -> str:
        return instance.business_area.slug

    class Django:
        model = Household
        fields = []
        related_models = [Individual]

    def get_instances_from_related(self, related_instance: Individual) -> Household:
        if isinstance(related_instance, Individual):
            return related_instance.household
        return None

    class Index:
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}households"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }
