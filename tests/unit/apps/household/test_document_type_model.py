from django.core.management import call_command
from django.test import TestCase

from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory
from hct_mis_api.apps.household.models import \
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE


class TestDocumentTypeModel(TestCase):
    databases = "__all__"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("init-geo-fixtures")

    def test_create_document_type(self) -> None:
        assert DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])
