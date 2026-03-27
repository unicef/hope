import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import RoleFactory
from extras.test_utils.factories.api import APITokenFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from hope.models import APIToken, BusinessArea, User
from hope.models.utils import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def read_only_api_token(api_user: User, business_area: BusinessArea) -> APIToken:
    grants = [Grant.API_READ_ONLY.name]
    role = RoleFactory(name="read-only-role", permissions=grants)
    api_user.role_assignments.create(role=role, business_area=business_area)
    token = APITokenFactory(user=api_user, grants=grants)
    token.valid_for.set([business_area])
    return token


@pytest.fixture
def read_only_api_client(read_only_api_token: APIToken) -> APIClient:
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + read_only_api_token.key)
    return client


@pytest.fixture
def business_area_list_url() -> str:
    return reverse("api:core:business-areas-list")


@pytest.fixture
def three_business_areas(
    business_area: BusinessArea, api_user: User, read_only_api_token: APIToken
) -> list[BusinessArea]:
    ba1 = BusinessAreaFactory(
        slug="ukraine11",
        code="1234",
        name="Ukraine",
        long_name="the long name of Ukraine",
        active=True,
    )
    ba2 = BusinessAreaFactory(
        slug="ba-2",
        code="5678",
        name="Bus Area 2",
        long_name="Business Area 2",
        active=False,
        parent=business_area,
    )
    role = read_only_api_token.user.role_assignments.first().role
    api_user.role_assignments.create(role=role, business_area=ba1)
    api_user.role_assignments.create(role=role, business_area=ba2)
    read_only_api_token.valid_for.add(ba1, ba2)
    return [business_area, ba1, ba2]


def test_list_business_area_without_grant_returns_403(
    token_api_client: APIClient,
    business_area_list_url: str,
) -> None:
    response = token_api_client.get(business_area_list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_business_area_returns_all_areas(
    read_only_api_client: APIClient,
    business_area_list_url: str,
    three_business_areas: list[BusinessArea],
) -> None:
    ba_base, ba_ukraine, ba_child = three_business_areas

    response = read_only_api_client.get(business_area_list_url)

    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 3
    assert {
        "id": str(ba_base.id),
        "name": ba_base.name,
        "code": ba_base.code,
        "long_name": ba_base.long_name,
        "slug": ba_base.slug,
        "parent": None,
        "is_split": ba_base.is_split,
        "active": ba_base.active,
        "is_accountability_applicable": ba_base.is_accountability_applicable,
        "rdi_import_xlsx_disabled": ba_base.rdi_import_xlsx_disabled,
        "countries": [],
    } in results
    assert {
        "id": str(ba_ukraine.id),
        "name": ba_ukraine.name,
        "code": ba_ukraine.code,
        "long_name": ba_ukraine.long_name,
        "slug": ba_ukraine.slug,
        "parent": None,
        "is_split": ba_ukraine.is_split,
        "active": ba_ukraine.active,
        "is_accountability_applicable": ba_ukraine.is_accountability_applicable,
        "rdi_import_xlsx_disabled": ba_ukraine.rdi_import_xlsx_disabled,
        "countries": [],
    } in results
    assert {
        "id": str(ba_child.id),
        "name": ba_child.name,
        "code": ba_child.code,
        "long_name": ba_child.long_name,
        "slug": ba_child.slug,
        "parent": str(ba_child.parent.id),
        "is_split": ba_child.is_split,
        "active": ba_child.active,
        "is_accountability_applicable": ba_child.is_accountability_applicable,
        "rdi_import_xlsx_disabled": ba_child.rdi_import_xlsx_disabled,
        "countries": [],
    } in results
