import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import RoleFactory
from extras.test_utils.factories.api import APITokenFactory
from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from hope.models import APIToken, Area, BusinessArea
from hope.models.utils import Grant

pytestmark = pytest.mark.django_db


@pytest.fixture
def read_only_api_token(api_user, business_area: BusinessArea) -> APIToken:
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
def area_list_url(business_area: BusinessArea) -> str:
    return reverse("api:geo:areas-list", kwargs={"business_area_slug": business_area.slug})


@pytest.fixture
def areas_for_business_area(business_area: BusinessArea) -> list[Area]:
    country_1 = CountryFactory(name="Afghanistan")
    country_1.business_areas.set([business_area])
    country_2 = CountryFactory(name="Afghanistan 2")
    country_2.business_areas.set([business_area])

    area_type_1 = AreaTypeFactory(name="Area Type in Afg", country=country_1, area_level=1)
    area_type_2 = AreaTypeFactory(name="Area Type 2 in Afg", country=country_1, area_level=2)
    area_type_3 = AreaTypeFactory(name="Area Type in Afg 2", country=country_2, area_level=1)

    areas = [
        AreaFactory(name="Area 1 AT1", area_type=area_type_1),
        AreaFactory(name="Area 2 AT1", area_type=area_type_1),
        AreaFactory(name="Area 1 AT2", area_type=area_type_2),
        AreaFactory(name="Area 2 AT2", area_type=area_type_2),
        AreaFactory(name="Area 1 AT3", area_type=area_type_3),
        AreaFactory(name="Area 2 AT3", area_type=area_type_3),
    ]

    # Area belonging to a different business area — should be excluded
    other_ba = BusinessAreaFactory(name="Other")
    other_country = CountryFactory(name="Other Country")
    other_country.business_areas.set([other_ba])
    other_area_type = AreaTypeFactory(name="Area Type Other", country=other_country)
    AreaFactory(name="Area Other", area_type=other_area_type)

    return areas


def test_list_areas_returns_403_without_read_only_grant(token_api_client: APIClient, area_list_url: str) -> None:
    response = token_api_client.get(area_list_url)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_areas_returns_only_areas_for_business_area(
    read_only_api_client: APIClient, area_list_url: str, areas_for_business_area: list[Area]
) -> None:
    response = read_only_api_client.get(area_list_url)
    assert response.status_code == status.HTTP_200_OK

    response_json = response.json()
    assert len(response_json) == 6

    expected = [
        {
            "id": str(area.id),
            "name": area.name,
            "p_code": area.p_code,
            "area_type": str(area.area_type_id),
            "updated_at": area.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        for area in areas_for_business_area
    ]
    assert sorted(response_json, key=lambda x: x["id"]) == sorted(expected, key=lambda x: x["id"])
