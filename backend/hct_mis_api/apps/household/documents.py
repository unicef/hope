from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from core.es_analyzers import phonetic_analyzer
from .models import Individual


@registry.register_document
class IndividualDocument(Document):
    id = fields.TextField()
    given_name = fields.TextField(analyzer=phonetic_analyzer)
    middle_name = fields.TextField(analyzer=phonetic_analyzer)
    family_name = fields.TextField(analyzer=phonetic_analyzer)
    full_name = fields.TextField()
    birth_date = fields.TextField()
    phone_no = fields.TextField("phone_no.__str__")
    phone_no_alternative = fields.TextField("phone_no_alternative.__str__")
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

    class Index:
        name = "individuals"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Individual

        fields = [
            "relationship",
            "sex",
            "created_at",
            "updated_at",
        ]
