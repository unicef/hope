from django.test import TestCase

from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    DocumentType,
)


class TestDocumentTypeModel(TestCase):
    databases = "__all__"
    fixtures = ("hct_mis_api/apps/geo/fixtures/data.json",)

    def test_create_document_type_with_specific_country(self):
        country = geo_models.Country.objects.get(iso_code2="PL")
        document_type = DocumentType.objects.create(country=country, type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
        self.assertEqual(document_type.country, country)

    def test_create_document_type_without_specific_country(self):
        document_type = DocumentType.objects.create(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
        self.assertEqual(document_type.country, None)
