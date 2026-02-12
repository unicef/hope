from io import BytesIO
from pathlib import Path
from typing import Any, List
from unittest.mock import patch

from django.conf import settings
from django.urls import reverse
import pytest
from rest_framework import status

from extras.test_utils.factories import BusinessAreaFactory, PartnerFactory, SanctionListIndividualFactory, UserFactory
from hope.apps.account.permissions import Permissions
from hope.apps.registration_datahub.validators import XlsxError
from hope.apps.sanction_list.api.views import SanctionListIndividualViewSet

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area():
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def partner():
    return PartnerFactory(name="unittest")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def client(api_client: Any, user):
    return api_client(user)


@pytest.fixture
def sanction_individual():
    return SanctionListIndividualFactory(
        full_name="Individual FullName",
        reference_number="123",
    )


@pytest.fixture
def url_list(business_area, sanction_individual):
    return reverse(
        "api:sanction-list:sanction-list-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_list_count(business_area, sanction_individual):
    return reverse(
        "api:sanction-list:sanction-list-count",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def url_details(business_area, sanction_individual):
    return reverse(
        "api:sanction-list:sanction-list-detail",
        kwargs={
            "pk": str(sanction_individual.pk),
            "business_area_slug": business_area.slug,
        },
    )


@pytest.fixture
def url_check(business_area):
    return reverse(
        "api:sanction-list:sanction-list-check-against-sanction-list",
        kwargs={"business_area_slug": business_area.slug},
    )


@pytest.fixture
def sanction_file():
    file = BytesIO(
        Path(
            f"{settings.TESTS_ROOT}/apps/sanction_list/test_files/TestSanctionList.xlsx"
        ).read_bytes()
    )
    file.name = "unordered_columns_1.xlsx"
    return file


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_sanction_list(
    permissions: List,
    expected_status: int,
    client,
    business_area,
    url_list,
    create_user_role_with_permissions: Any,
    user,
):
    create_user_role_with_permissions(user, permissions, business_area)
    response = client.get(url_list)

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:

        resp_data = response.json()
        assert len(resp_data["results"]) == 1
        individual = resp_data["results"][0]
        assert "id" in individual
        assert "documents" in individual
        assert "dates_of_birth" in individual
        assert individual["full_name"] == "Individual FullName"
        assert individual["reference_number"] == "123"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_sanction_list_count(
    permissions: List,
    expected_status: int,
    client,
    business_area,
    url_list_count,
    create_user_role_with_permissions: Any,
    user,
):
    create_user_role_with_permissions(user, permissions, business_area)
    response = client.get(url_list_count)

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        assert response.json()["count"] == 1


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_get_sanction_list_details(
    permissions: List,
    expected_status: int,
    client,
    business_area,
    url_details,
    create_user_role_with_permissions: Any,
    user,
):
    create_user_role_with_permissions(user, permissions, business_area)
    response = client.get(url_details)

    assert response.status_code == expected_status

    if expected_status == status.HTTP_200_OK:
        resp_data = response.data
        assert "id" in resp_data
        assert "documents" in resp_data
        assert "dates_of_birth" in resp_data
        assert resp_data["full_name"] == "Individual FullName"
        assert resp_data["reference_number"] == "123"


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_202_ACCEPTED),
        ([], status.HTTP_403_FORBIDDEN),
    ],
)
def test_check_against_sanction_list(
    permissions: List,
    expected_status: int,
    client,
    business_area,
    url_check,
    sanction_file,
    create_user_role_with_permissions: Any,
    user,
):
    create_user_role_with_permissions(user, permissions, business_area)

    response = client.post(url_check, {"file": sanction_file}, format="multipart")

    assert response.status_code == expected_status

    if expected_status == status.HTTP_202_ACCEPTED:
        resp_data = response.data
        assert resp_data["ok"] is False
        assert resp_data["errors"] == []


def test_check_against_sanction_list_validation_error(
    client,
    business_area,
    url_check,
    sanction_file,
    create_user_role_with_permissions: Any,
    user,
):
    create_user_role_with_permissions(
        user,
        [Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area,
    )

    error_payload = [{"header": "name", "message": "Invalid value name for user22"}]

    with patch.object(
        SanctionListIndividualViewSet,
        "validate",
        side_effect=XlsxError(error_payload),
    ):
        response = client.post(url_check, {"file": sanction_file}, format="multipart")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["ok"] is False
    assert response.data["errors"] == error_payload
