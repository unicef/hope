from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIRequestFactory

from hct_mis_api.api.endpoints import DataCollectingTypeViewSet
from hct_mis_api.apps.core.fixtures import DataCollectingTypeFactory, create_afghanistan


class TestDataCollectingTypeViewSet(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = create_afghanistan()

        cls.data_collecting_type_1 = DataCollectingTypeFactory(
            label="Partial", code="partial", business_areas=[cls.business_area]
        )
        cls.data_collecting_type_2 = DataCollectingTypeFactory(label="Full", code="full")
        cls.data_collecting_type_3 = DataCollectingTypeFactory(
            label="Unknown", code="unknown", business_areas=[cls.business_area]
        )

    def test_data_collecting_type_view_set(self) -> None:
        factory = APIRequestFactory()
        data_collecting_types_list = DataCollectingTypeViewSet.as_view(actions={"get": "list"})

        request = factory.get(reverse("api:data-collecting-types-list"), format="json")
        response = data_collecting_types_list(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            dict(response.data[0]),
            {
                "id": self.data_collecting_type_1.id,
                "label": "Partial",
                "code": "partial",
                "description": self.data_collecting_type_1.description,
                "active": True,
                "individual_filters_available": False,
                "household_filters_available": True,
                "recalculate_composition": False,
                "compatible_types": [],
                "limit_to": ["afghanistan"],
            },
        )
        self.assertEqual(
            dict(response.data[1]),
            {
                "id": self.data_collecting_type_2.id,
                "label": "Full",
                "code": "full",
                "description": self.data_collecting_type_2.description,
                "active": True,
                "individual_filters_available": False,
                "household_filters_available": True,
                "recalculate_composition": False,
                "compatible_types": [],
                "limit_to": [],
            },
        )
        self.assertEqual(
            dict(response.data[2]),
            {
                "id": self.data_collecting_type_3.id,
                "label": "Unknown",
                "code": "unknown",
                "description": self.data_collecting_type_3.description,
                "active": True,
                "individual_filters_available": False,
                "household_filters_available": True,
                "recalculate_composition": False,
                "compatible_types": [],
                "limit_to": ["afghanistan"],
            },
        )
