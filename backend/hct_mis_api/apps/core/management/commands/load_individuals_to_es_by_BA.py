from argparse import ArgumentParser
from typing import Any

from django.core.management import BaseCommand
from django.core.paginator import Paginator

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from hct_mis_api.apps.household.documents import (
    IndividualDocumentAfghanistan,
    IndividualDocumentOthers,
    IndividualDocumentUkraine,
)
from hct_mis_api.apps.household.models import Individual

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Re-index elasticsearch documents for given index and business_area"

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("business_area", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        from django.conf import settings

        business_area = options["business_area"]
        if business_area == "afghanistan":
            index = "individuals_afghanistan"
            es_document = IndividualDocumentAfghanistan
        elif business_area == "ukraine":
            index = "individuals_ukraine"
            es_document = IndividualDocumentUkraine
        else:
            index = "individuals_others"
            es_document = IndividualDocumentOthers

        es = Elasticsearch(settings.ELASTICSEARCH_HOST)

        queryset = Individual.objects.filter(registration_data_import__business_area__slug=business_area)
        document_list = []

        paginator = Paginator(queryset, BATCH_SIZE)
        number_of_pages = paginator.num_pages
        for page in paginator.page_range:
            print(f"Loading page {page} of {number_of_pages}")
            for individual in paginator.page(page).object_list:
                document = {**es_document().prepare(individual), "_id": individual.id}
                document_list.append(document)
            bulk(es, document_list, index=index)
            document_list = []

        self.stdout.write(f"Data for {business_area} loaded successfully.")
