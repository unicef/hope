from django.core.management.base import BaseCommand

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, scan

from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.documents import HouseholdDocument, IndividualDocument
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.registration_datahub.documents import ImportedIndividualDocument
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual

BATCH_SIZE = 5_000

ES_MAPPING_INDEX_MODEL = {
    "households": (Household, HouseholdDocument),
    "individuals": (Individual, IndividualDocument),
    "importedindividuals": (ImportedIndividual, ImportedIndividualDocument),
}


class Command(BaseCommand):
    help = "Re-index elasticsearch documents for given index and business_area"

    ELASTICSEARCH_HOST = "http://elasticsearch:9200"

    def add_arguments(self, parser):
        parser.add_argument("index", type=str)
        parser.add_argument("business_area", type=str)

    def handle(self, *args, **options):
        es = Elasticsearch(self.ELASTICSEARCH_HOST)

        index = options["index"]
        es_mapping = ES_MAPPING_INDEX_MODEL.get(index)
        if not es_mapping:
            self.stdout.write(f"{index} does not exist.")
            return

        business_area = options["business_area"]
        if not BusinessArea.objects.filter(slug=business_area).exists():
            self.stdout.write(f"{business_area} does not exist.")
            return

        query_body = {"query": {"bool": {"filter": {"term": {"business_area": business_area}}}}}

        bulk_deletes = []
        total = 0

        for result in scan(client=es, query=query_body, index=index, _source=False, track_scores=False, scroll="1m"):
            result["_op_type"] = "delete"
            bulk_deletes.append(result)

            if len(bulk_deletes) >= BATCH_SIZE:
                bulk(es, bulk_deletes, index=index)
                total += len(bulk_deletes)
                self.stdout.write(f"{total} documents removed")
                bulk_deletes = []

        bulk(es, bulk_deletes, index=index)
        self.stdout.write(self.style.SUCCESS(f"{total + len(bulk_deletes)} documents removed"))

        model, es_document = es_mapping
        if model == ImportedIndividual:
            qs = model.objects.filter(registration_data_import__business_area_slug=business_area)
        else:
            qs = model.objects.filter(registration_data_import__business_area__slug=business_area)

        i, count = 0, qs.count() // BATCH_SIZE + 1
        document_list = []

        while i <= count:
            self.stdout.write(f"{i}/{count}")
            batch = qs[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
            for item in batch:
                document = {**es_document().prepare(item), "_id": item.id}
                document_list.append(document)
            bulk(es, document_list, index=index)
            document_list = []
            i += 1

        self.stdout.write(self.style.SUCCESS(f"Documents for index: {index}, business_area: {business_area} created"))
