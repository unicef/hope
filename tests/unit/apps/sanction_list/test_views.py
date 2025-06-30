from io import BytesIO
from pathlib import Path
from typing import Any, List
from unittest.mock import patch

from django.conf import settings
from django.urls import reverse

import pytest
from rest_framework import status

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.registration_datahub.validators import XlsxException
from hct_mis_api.apps.sanction_list.api.views import SanctionListIndividualViewSet
from hct_mis_api.apps.sanction_list.fixtures import SanctionListIndividualFactory

pytestmark = pytest.mark.django_db


class TestSanctionListIndividualViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="unittest")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        sanction_list_individual = SanctionListIndividualFactory(
            full_name="Individual FullName", reference_number="123"
        )

        self.url_list = reverse(
            "api:sanction-list:sanction-list-list", kwargs={"business_area_slug": self.afghanistan.slug}
        )
        self.url_list_count = reverse(
            "api:sanction-list:sanction-list-count", kwargs={"business_area_slug": self.afghanistan.slug}
        )
        self.url_details = reverse(
            "api:sanction-list:sanction-list-detail",
            kwargs={"pk": str(sanction_list_individual.pk), "business_area_slug": self.afghanistan.slug},
        )
        self.url_check = reverse(
            "api:sanction-list:sanction-list-check-against-sanction-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_get_sanction_list(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan)
        response = self.client.get(self.url_list)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.json()
            assert len(resp_data["results"]) == 1
            individual = resp_data["results"][0]
            assert "id" in individual
            assert "documents" in individual
            assert "dates_of_birth" in individual
            assert "Individual FullName" == individual["full_name"]
            assert "123" == individual["reference_number"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_get_sanction_list_count(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan)
        response = self.client.get(self.url_list_count)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            assert response.json()["count"] == 1

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_get_sanction_list_details(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan)
        response = self.client.get(self.url_details)

        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.status_code == status.HTTP_200_OK
            resp_data = response.data
            assert "id" in resp_data
            assert "documents" in resp_data
            assert "dates_of_birth" in resp_data
            assert "Individual FullName" == resp_data["full_name"]
            assert "123" == resp_data["reference_number"]

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_202_ACCEPTED),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_check_against_sanction_list(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan)

        file = BytesIO(Path(f"{settings.TESTS_ROOT}/apps/sanction_list/test_files/TestSanctionList.xlsx").read_bytes())
        file.name = "unordered_columns_1.xlsx"
        response = self.client.post(self.url_check, {"file": file}, format="multipart")

        assert response.status_code == expected_status
        if expected_status == status.HTTP_202_ACCEPTED:
            assert response.status_code == status.HTTP_202_ACCEPTED
            resp_data = response.data
            assert resp_data["ok"] is False
            assert resp_data["errors"] == []

    def test_check_against_sanction_list_validation_error(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], self.afghanistan)
        file = BytesIO(Path(f"{settings.TESTS_ROOT}/apps/sanction_list/test_files/TestSanctionList.xlsx").read_bytes())
        file.name = "unordered_columns_1.xlsx"

        error_payload = [{"header": "name", "message": "Invalid value name for user22"}]

        with patch.object(SanctionListIndividualViewSet, "validate", side_effect=XlsxException(error_payload)):
            response = self.client.post(self.url_check, {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["ok"] is False
        assert response.data["errors"] == error_payload
