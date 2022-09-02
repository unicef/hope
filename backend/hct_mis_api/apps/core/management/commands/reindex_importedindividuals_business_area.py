from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

from hct_mis_api.apps.registration_datahub.documents import ImportedIndividualDocument
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual


class Command(BaseCommand):
    help = "Re-index elasticsearch importedindividuals' documents for given business_area"

    ELASTICSEARCH_HOST = "http://elasticsearch:9200"

    def add_arguments(self, parser):
        parser.add_argument("business_area", type=str)

    def handle(self, *args, **options):
        es = Elasticsearch(self.ELASTICSEARCH_HOST)

        business_area = options["business_area"]
        query_body = {
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                            "business_area": business_area
                        }
                    }
                }
            }
        }

        bulk_deletes = []
        for result in scan(
            client=es, query=query_body, index="importedindividuals", _source=False, track_scores=False, scroll="5m"
        ):
            result["_op_type"] = "delete"
            bulk_deletes.append(result)

        bulk(es, bulk_deletes)
        self.stdout.write(self.style.SUCCESS(
            f"Documents ({len(bulk_deletes)}) with business_area {business_area} removed")
        )

        qs = ImportedIndividual.objects.filter(registration_data_import__business_area_slug=business_area)
        document_list = []

        for individual in qs:
            document = ImportedIndividualDocument().prepare(individual)
            document_list.append(document)

        bulk(es, document_list, index="importedindividuals")
        self.stdout.write(self.style.SUCCESS(
            f"Documents ({len(document_list)}) with business_area {business_area} created")
        )
