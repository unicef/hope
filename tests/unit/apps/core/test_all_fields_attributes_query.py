from typing import Any

from django.core.management import call_command

import pytest
from parameterized import parameterized
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.payment.fixtures import generate_delivery_mechanisms

pytestmark = pytest.mark.django_db()


class TestMetaDataFilterType(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadflexfieldsattributes")
        # graph query to be called.
        cls.user = UserFactory.create()

    @parameterized.expand(
        [
            ("afghanistan",),
            ("ukraine",),
        ]
    )
    def test_rest_endpoint_all_fields_attributes(self, business_area: BusinessArea) -> None:
        client = APIClient()
        response = client.get(reverse("fields_attributes"), data={"business_area_slug": business_area})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestGetCollectorFieldsAttributes:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.user = UserFactory()
        self.api_client = api_client(self.user)

        generate_delivery_mechanisms()

    def test_get_all_collector_fields_attributes(self) -> None:
        response = self.api_client.get(reverse("api:core:business-areas-all-collector-fields-attributes"))
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()
        assert len(response_results) == 2
        assert response_results[0]["id"] == "bank__number"
        assert response_results[1]["id"] == "mobile__number"
