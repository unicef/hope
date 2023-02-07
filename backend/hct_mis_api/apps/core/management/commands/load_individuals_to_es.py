from argparse import ArgumentParser
from typing import Any, Type

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
from hct_mis_api.apps.registration_datahub.documents import (
    ImportedIndividualDocumentAfghanistan,
    ImportedIndividualDocumentOthers,
    ImportedIndividualDocumentUkraine,
)
from hct_mis_api.apps.registration_datahub.models import ImportedIndividual

BATCH_SIZE = 1000

models_to_documents_mapping = {
    "individual": {
        "afghanistan": IndividualDocumentAfghanistan,
        "ukraine": IndividualDocumentUkraine,
    },
    "imported_individual": {
        "afghanistan": ImportedIndividualDocumentAfghanistan,
        "ukraine": ImportedIndividualDocumentUkraine,
    },
}


def get_document_type(model: str, business_area: str) -> Type[object]:
    if model == "individual":
        return models_to_documents_mapping["individual"].get(business_area, IndividualDocumentOthers)
    else:
        return models_to_documents_mapping["imported_individual"].get(business_area, ImportedIndividualDocumentOthers)


class Command(BaseCommand):
    from django.conf import settings

    help = "Load elasticsearch documents (individuals) for given business_area"
    es = Elasticsearch(settings.ELASTICSEARCH_HOST)

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--business_areas", nargs="+", type=str)
        parser.add_argument("--model", type=str)

    def handle(self, *args: Any, **options: Any) -> None:
        business_areas = options["business_areas"]
        model = options["model"]

        for business_area in business_areas:
            document_type = get_document_type(model, business_area)
            self.load_to_es(business_area, document_type)

    def load_to_es(self, business_area: str, document_type: Type[object]) -> None:
        if document_type in (IndividualDocumentAfghanistan, IndividualDocumentUkraine, IndividualDocumentOthers):
            queryset = Individual.objects.filter(registration_data_import__business_area__slug=business_area)
        else:
            queryset = ImportedIndividual.objects.filter(registration_data_import__business_area_slug=business_area)

        document_list = []
        paginator = Paginator(queryset, BATCH_SIZE)
        number_of_pages = paginator.num_pages

        for page in paginator.page_range:
            print(f"Loading page {page} of {number_of_pages}")

            for individual in paginator.page(page).object_list:
                document = {**document_type().prepare(individual), "_id": individual.id}
                document_list.append(document)
            bulk(self.es, document_list, index=document_type.Index.name)
            document_list = []

        self.stdout.write(f"Data for {business_area} loaded successfully.")
