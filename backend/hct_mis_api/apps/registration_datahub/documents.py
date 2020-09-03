from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from core.es_analyzers import phonetic_analyzer
from .models import ImportedIndividual


@registry.register_document
class ImportedIndividualDocument(Document):
    id = fields.KeywordField(boost=0)
    given_name = fields.TextField(analyzer=phonetic_analyzer)
    middle_name = fields.TextField(analyzer=phonetic_analyzer)
    family_name = fields.TextField(analyzer=phonetic_analyzer)
    full_name = fields.TextField(boost=2.0)
    birth_date = fields.DateField()
    phone_no = fields.KeywordField("phone_no.__str__")
    phone_no_alternative = fields.KeywordField("phone_no_alternative.__str__")
    hash_key = fields.KeywordField(boost=3.0)
    business_area = fields.KeywordField()
    household = fields.ObjectField(
        properties={
            "size": fields.IntegerField(),
            "address": fields.TextField(),
            "created_at": fields.DateField(),
            "updated_at": fields.DateField(),
            "country_origin": fields.TextField(attr="country_origin.__str__"),
            "country": fields.TextField(attr="country.__str__"),
        }
    )
    registration_data_import_id = fields.KeywordField(
        "registration_data_import.id.__str__",
    )

    def prepare_hash_key(self, instance):
        return instance.get_hash_key

    def prepare_business_area(self, instance):
        return instance.registration_data_import.business_area_slug

    class Index:
        name = "importedindividuals"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = ImportedIndividual

        fields = [
            "relationship",
            "sex",
            "created_at",
            "updated_at",
        ]
