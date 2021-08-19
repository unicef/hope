from django.test import TestCase

from django_countries.fields import Country

from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    DocumentType,
)


class TestDocumentTypeModel(TestCase):
    multi_db = True

    def test_create_document_type_with_specific_country(self):
        document_type = DocumentType.objects.create(
            country=Country(code="PL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.assertEqual(document_type.country, Country(code="PL"))

    def test_create_document_type_without_specific_country(self):
        document_type = DocumentType.objects.create(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
        self.assertEqual(document_type.country, Country(code="U"))
