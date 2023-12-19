from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory, create_household
from hct_mis_api.apps.household.models import Document, Individual
from hct_mis_api.one_time_scripts.fix_documents_duplicates import (
    fix_documents_duplicates,
)


class TestFixDocumentsDuplicates(TestCase):
    def test_fix_documents_duplicates(self) -> None:
        create_afghanistan()
        document_numbers = [
            "7694387",
            "9006937",
            "41559916",
            "4762976",
            "7694387",
            "12639298",
            "41559916",
            "7684736",
            "12639298",
            "7684736",
            "34834238",
            "9006937",
            "28070941",
            "28070941",
            "41559916",
            "4762976",
            "34834238",
        ]
        document_type = DocumentTypeFactory(name="National ID")
        [create_household({"size": 1}) for _ in range(17)]
        individuals = Individual.objects.all()[:17]
        documents = []
        for individual, document_number in zip(individuals, document_numbers):
            # Duplicated documents
            documents.append(
                Document(
                    type=document_type,
                    individual=individual,
                    document_number=document_number,
                    status=Document.STATUS_VALID,
                )
            )
        # Unique document
        documents.append(
            Document(
                type=document_type, individual=individuals[0], document_number="1234", status=Document.STATUS_VALID
            )
        )
        Document.objects.bulk_create(documents)

        self.assertEquals(GrievanceTicket.objects.count(), 0)
        self.assertEquals(Document.objects.filter(status=Document.STATUS_VALID).count(), 18)
        self.assertEquals(Document.objects.filter(status=Document.STATUS_PENDING).count(), 0)

        fix_documents_duplicates()
        self.assertEquals(GrievanceTicket.objects.count(), 8)
        self.assertEquals(Document.objects.filter(status=Document.STATUS_VALID).count(), 1)
        self.assertEquals(Document.objects.filter(status=Document.STATUS_PENDING).count(), 17)
