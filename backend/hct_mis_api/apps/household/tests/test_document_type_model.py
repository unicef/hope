from django.conf import settings

from hct_mis_api.apps.core.base_test_case import DefaultTestCase
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.household.fixtures import DocumentTypeFactory
from hct_mis_api.apps.household.models import IDENTIFICATION_TYPE_BIRTH_CERTIFICATE


class TestDocumentTypeModel(DefaultTestCase):
    databases = "__all__"
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    def test_create_document_type(self) -> None:
        assert DocumentTypeFactory(key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE])
