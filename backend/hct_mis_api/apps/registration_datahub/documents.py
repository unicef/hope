from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import ImportedIndividual


@registry.register_document
class ImportedIndividualDocument(Document):
    phone_no = fields.TextField("phone_no.__str__")
    phone_no_alternative = fields.TextField("phone_no_alternative.__str__")
    household = fields.ObjectField(properties={
        'size': fields.IntegerField(),
        'address': fields.TextField(),
        'created_at': fields.DateField(),
        'updated_at': fields.DateField(),
        "country_origin": fields.TextField(attr="country_origin.__str__"),
        "country": fields.TextField(attr="country.__str__"),
    })

    class Index:
        name = "importedindividuals"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = ImportedIndividual

        fields = [
            "full_name",
            "given_name",
            "middle_name",
            "family_name",
            "relationship",
            "role",
            "sex",
            "birth_date",
            "created_at",
            "updated_at",
        ]
