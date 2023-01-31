from typing import Any

from django.core.management import BaseCommand

from hct_mis_api.apps.registration_data.models import RegistrationDataImport
from hct_mis_api.apps.registration_datahub.documents import (
    ImportedIndividualDocumentAfghanistan,
    ImportedIndividualDocumentOthers,
    ImportedIndividualDocumentUkraine,
)
from hct_mis_api.apps.utils.elasticsearch_utils import (
    remove_elasticsearch_documents_by_matching_ids,
)


class Command(BaseCommand):
    help = "Remove ImportedIndividuals from elasticsearch documents"

    def handle(self, *args: Any, **options: Any) -> None:
        es_documents = [
            ImportedIndividualDocumentAfghanistan,
            ImportedIndividualDocumentUkraine,
            ImportedIndividualDocumentOthers,
        ]

        for es_document in es_documents:
            print(f"Removing {es_document} index {es_document.Index.name}")

            qs = es_document().get_queryset().filter(registration_data_import__status=RegistrationDataImport.MERGED)
            print(f"Count {qs.count()}")
            remove_elasticsearch_documents_by_matching_ids(list(qs.values_list("id", flat=True)), es_document)

        print("Done")
