from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory

from hct_mis_api.api.endpoints.rdi.program import DataCollectingTypeViewSet
from hct_mis_api.apps.account.fixtures import BusinessAreaFactory
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan


class TestDataCollectingTypeViewSet(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = BusinessAreaFactory(slug="some-slug")
        DataCollectingTypeFactory(
            label="Partial", code="partial", business_areas=[cls.business_area]
        )

    def test_data_collecting_type_view_set(self) -> None:
        factory = APIRequestFactory()
        data_collecting_types_list = DataCollectingTypeViewSet.as_view(actions={"get": "list"})

        request = factory.get(reverse("api:data-collecting-types-list"), format="json")
        response = data_collecting_types_list(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
