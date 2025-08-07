from django.core.management import call_command
from django.db import IntegrityError
from django.test import TestCase

from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import DocumentTypeFactory, create_household
from extras.test_utils.factories.program import ProgramFactory

from hope.apps.geo.models import Country
from hope.apps.household.models import Document
from hope.apps.utils.models import MergeStatusModel


class TestDocumentConstraint(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")
        create_afghanistan()

        cls.programs = ProgramFactory.create_batch(2)

        _, individuals1 = create_household()
        _, individuals2 = create_household()
        individuals = [individuals1[0], individuals2[0]]
        country = Country.objects.first()
        document_type = DocumentTypeFactory()

        cls.document_data = {
            "document_number": "test",
            "type": document_type,
            "individual": individuals[0],
            "country": country,
            "status": Document.STATUS_VALID,
            "rdi_merge_status": MergeStatusModel.MERGED,
        }

    def test_allow_create_the_same_document_for_different_program(self) -> None:
        try:
            Document.objects.create(program=self.programs[0], **self.document_data)
            Document.objects.create(program=self.programs[1], **self.document_data)
        except IntegrityError:
            self.fail("Shouldn't raise any errors!")

    def test_disallow_create_the_same_document_for_the_same_program(self) -> None:
        with self.assertRaises(IntegrityError):
            Document.objects.create(program=self.programs[0], **self.document_data)
            Document.objects.create(program=self.programs[0], **self.document_data)
