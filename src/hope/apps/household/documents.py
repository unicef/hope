from django.conf import settings
from django.db.models import QuerySet
from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import AttrDict

from hope.apps.core.es_analyzers import name_synonym_analyzer, phonetic_analyzer
from hope.apps.utils.elasticsearch_utils import DEFAULT_SCRIPT
from hope.models import Household, Individual, IndividualIdentity, IndividualRoleInHousehold

RelatedInstanceType = Document | Household | IndividualIdentity | IndividualRoleInHousehold

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


class IndividualDocument(Document):
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


class HouseholdDocument(Document):
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


def _set_django_attr(doc_class: type, django_inner_class: type) -> None:
    """Manually set the 'django' attribute that django-elasticsearch-dsl normally sets via register_document."""
    django_attr = AttrDict({"model": django_inner_class.model})
    django_attr.ignore_signals = getattr(django_inner_class, "ignore_signals", False)
    django_attr.auto_refresh = getattr(
        django_inner_class, "auto_refresh", getattr(settings, "ELASTICSEARCH_DSL_AUTO_REFRESH", True)
    )
    django_attr.related_models = getattr(django_inner_class, "related_models", [])
    django_attr.queryset_pagination = getattr(django_inner_class, "queryset_pagination", None)
    doc_class.django = django_attr
    model_field_names = getattr(django_inner_class, "fields", [])
    mapping_fields = doc_class._doc_type.mapping.properties.properties.to_dict().keys()
    for field_name in model_field_names:
        if field_name not in mapping_fields:
            django_field = django_attr.model._meta.get_field(field_name)
            field_instance = doc_class.to_field(field_name, django_field)
            doc_class._doc_type.mapping.field(field_name, field_instance)
    doc_class._fields = doc_class._doc_type.mapping.properties.properties.to_dict()


def get_individual_doc(program_id: str) -> type[IndividualDocument]:
    """Get Individual ES document class for a specific program.

    Returns a dynamically configured Document class with per-program index.
    """
    from hope.models import Program

    try:
        program = Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        raise ValueError(f"Program {program_id} does not exist.")

    index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}individuals_{program.business_area.slug}_{program.slug}"

    class ProgramIndividualDocument(IndividualDocument):
        class Index:
            name = index_name
            settings = index_settings

        class Django(IndividualDocument.Django):
            pass

        def get_queryset(self):
            return Individual.all_merge_status_objects.filter(program_id=program_id)

    ProgramIndividualDocument.__name__ = f"IndividualDocument_{program.slug}"
    _set_django_attr(ProgramIndividualDocument, ProgramIndividualDocument.Django)
    return ProgramIndividualDocument


def get_household_doc(program_id: str) -> type[HouseholdDocument]:
    """Get Household document class for a specific program.

    Returns a dynamically configured Document class with per-program index.
    """
    from hope.models import Program

    try:
        program = Program.objects.get(id=program_id)
    except Program.DoesNotExist:
        raise ValueError(f"Program {program_id} does not exist.")

    index_name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}households_{program.business_area.slug}_{program.slug}"

    class ProgramHouseholdDocument(HouseholdDocument):
        class Index:
            name = index_name
            settings = {"number_of_shards": 1, "number_of_replicas": 0}

        class Django(HouseholdDocument.Django):
            pass

        def get_queryset(self):
            return Household.objects.filter(program_id=program_id)

    ProgramHouseholdDocument.__name__ = f"HouseholdDocument_{program.slug}"
    _set_django_attr(ProgramHouseholdDocument, ProgramHouseholdDocument.Django)
    return ProgramHouseholdDocument
