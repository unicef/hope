from django.core.management.base import BaseCommand
from django.db.models import Q

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from hct_mis_api.apps.household.documents import IndividualDocument
from hct_mis_api.apps.household.models import Individual

BATCH_SIZE = 5_000


class Command(BaseCommand):
    help = "Re-index elasticsearch individuals' documents per business_area (index)"
    es = Elasticsearch("http://elasticsearch:9200")

    def add_arguments(self, parser):
        parser.add_argument("business_area", type=str, default=None)

    def load_batches(self, index, business_area_slug):
        if business_area_slug in ("afghanistan", "ukraine"):
            qs = Individual.objects.filter(business_area__slug=business_area_slug)
        else:
            qs = Individual.objects.exclude(Q(business_area__slug="afghanistan") | Q(business_area__slug="ukraine"))

        i, count = 0, qs.count() // BATCH_SIZE + 1
        document_list = []

        self.stdout.write(index)

        while i <= count:
            self.stdout.write(f"{i}/{count}")
            batch = qs[BATCH_SIZE * i : BATCH_SIZE * (i + 1)]
            for item in batch:
                document = {**IndividualDocument().prepare(item), "_id": item.id}
                document_list.append(document)
            bulk(self.es, document_list, index=index)
            document_list = []
            i += 1

    def reindex_business_area(self, business_area_slug):
        index = f"individuals_{business_area_slug}"
        if self.es.indices.exists(index=index):
            self.es.delete_by_query(index=index, body={"query": {"match_all": {}}})
            self.load_batches(index, business_area_slug)
        else:
            self.es.indices.create(index=index)
            self.load_batches(index, business_area_slug)

        self.stdout.write(self.style.SUCCESS(f"Documents for index: {index} created"))

    def handle(self, *args, **options):
        business_area_slug = options.pop("business_area", None)
        indices_options = ("afghanistan", "ukraine", "others")

        if business_area_slug is None:  # Reindex all indices
            for slug in indices_options:
                self.reindex_business_area(slug)
        else:
            if business_area_slug not in ("afghanistan", "ukraine", "others"):
                self.stdout.write(f"You can choose one of: {indices_options}")
            self.reindex_business_area(business_area_slug)
