from django.conf import settings
from django.db import IntegrityError
from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.models import Country
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory, create_household
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestDocumentConstraint(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    @classmethod
    def setUpTestData(cls) -> None:
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
