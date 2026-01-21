from django.test import TestCase

from extras.test_utils.factories.household import DocumentTypeFactory
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.household.const import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE


class TestDocumentTypeModel(TestCase):
    def test_create_document_type(self) -> None:
        assert DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])
