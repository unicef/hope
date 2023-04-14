from django.test import TestCase

from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
from hct_mis_api.apps.registration_datahub.models import ImportedDocumentType


class TestImportedDocumentTypeModel(TestCase):
    databases = "__all__"

    def test_create_document_type(self) -> None:
        assert ImportedDocumentType.objects.create(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])
