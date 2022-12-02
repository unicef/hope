from django.conf import settings
from django.test import TestCase

from hct_mis_api.apps.household.fixtures import DocumentTypeFactory
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE


class TestDocumentTypeModel(TestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    def test_create_document_type(self) -> None:
        assert DocumentTypeFactory(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
