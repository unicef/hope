from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from .models import SanctionListIndividual


@registry.register_document
class SanctionListIndividualESDocument(Document):
    full_name = fields.TextField()
    active = fields.BooleanField()
    dates_of_birth = fields.ObjectField(
        properties={
            "date": fields.DateField(),
        }
    )

    def prepare_hash_key(self, instance):
        return instance.get_hash_key

    class Index:
        name = "sanctionlistindividuals"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = SanctionListIndividual
