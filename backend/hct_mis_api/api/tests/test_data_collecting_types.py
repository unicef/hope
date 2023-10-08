from django.test import TestCase
from rest_framework.test import APIRequestFactory

from hct_mis_api.api.endpoints import DataCollectingTypeViewSet
from hct_mis_api.apps.core.fixtures import create_afghanistan, DataCollectingTypeFactory
from hct_mis_api.apps.core.models import BusinessArea


class TestDataCollectingTypeViewSet(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()

        DataCollectingTypeFactory(
            label="Partial",
            code="partial",
            description="collect partial",
            business_areas=[BusinessArea.objects.first()]
        )
        DataCollectingTypeFactory(
            label="Full",
            code="full",
            description="collect full"
        )

    def test_data_collecting_type_view_set(self) -> None:
        request = APIRequestFactory().get("")
        data_collecting_types_list = DataCollectingTypeViewSet.as_view({'get': 'list'})
        response = data_collecting_types_list(request)
        self.assertEqual(response.status_code, 200)
