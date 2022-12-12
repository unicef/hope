from django.test import TestCase

from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
from hct_mis_api.apps.registration_datahub.models import ImportedDocumentType


class TestImportedDocumentTypeModel(TestCase):
    databases = "__all__"

    def test_create_document_type(self):
        assert ImportedDocumentType.objects.create(type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE)
