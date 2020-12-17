from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from core.es_analyzers import phonetic_analyzer
from household.elasticsearch_utils import DEFAULT_SCRIPT
from .models import SanctionListIndividual


@registry.register_document
class SanctionListIndividualESDocument(Document):
    full_name = fields.TextField(analyzer=phonetic_analyzer)
    active = fields.BooleanField()
    dates_of_birth = fields.ObjectField(properties={"date": fields.DateField()})
    alias_name = fields.ObjectField(
        properties={
            "name": fields.TextField()
        }
    )

    def prepare_hash_key(self, instance):
        return instance.get_hash_key

    class Index:
        name = "sanctionlistindividuals"
        settings = {
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

    class Django:
        model = SanctionListIndividual
