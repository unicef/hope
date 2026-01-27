"""Tests for Area API views."""

from typing import Callable

from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    PartnerFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import Area, AreaType, Country

pytestmark = pytest.mark.django_db


@pytest.fixture
def partner():
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def api(user, api_client: Callable):
    return api_client(user)


@pytest.fixture
def afghanistan():
    return BusinessAreaFactory(name="Afghanistan")


@pytest.fixture
def afghanistan_2():
    return BusinessAreaFactory(name="Afghanistan 2")


@pytest.fixture
def ukraine_with_area_tree():
    ukraine = BusinessAreaFactory(
        code="4410",
        name="Ukraine",
        long_name="UKRAINE",
        region_code="66",
        region_name="ECAR",
        slug="ukraine",
        has_data_sharing_agreement=True,
        kobo_token="YYY",
    )

    country = CountryFactory(name="Ukraine")
    ukraine.countries.add(country)

    parent_area_type = None
    parent_area = None

    for name, level in [
        ("Province", 1),
        ("State", 2),
        ("County", 3),
        ("Region", 4),
        ("District", 5),
    ]:
        area_type = AreaTypeFactory(
            parent=parent_area_type,
            name=name,
            country=country,
            area_level=level,
        )

        area = AreaFactory(
            area_type=area_type,
            parent=parent_area,
            p_code=f"UA{level}",
            name=f"{name} {level}",
        )

        parent_area_type = area_type
        parent_area = area

    # rebuild trees
    Area.objects.rebuild()
    AreaType.objects.rebuild()
    Country.objects.rebuild()

    return ukraine


@pytest.fixture
def geo_data(afghanistan, afghanistan_2):
    country_1 = CountryFactory(name="Afghanistan")
    country_1.business_areas.set([afghanistan, afghanistan_2])

    country_2 = CountryFactory(
        name="Afghanistan 2",
        short_name="Afg2",
        iso_code2="A2",
        iso_code3="AF2",
        iso_num="2222",
    )
    country_2.business_areas.set([afghanistan])

    area_type_1 = AreaTypeFactory(country=country_1, area_level=1)
    area_type_2 = AreaTypeFactory(country=country_1, area_level=2)
    area_type_3 = AreaTypeFactory(country=country_2, area_level=1)

    area_1_l1 = AreaFactory(area_type=area_type_1, p_code="AREA1-ARTYPE1")
    area_2_l1 = AreaFactory(area_type=area_type_1, p_code="AREA2-ARTYPE1")

    area_1_l2 = AreaFactory(area_type=area_type_2, parent=area_1_l1, p_code="AREA1-ARTYPE2")
    area_2_l2 = AreaFactory(area_type=area_type_2, parent=area_2_l1, p_code="AREA2-ARTYPE2")
    area_3_l2 = AreaFactory(area_type=area_type_2, parent=area_1_l1, p_code="AREA3-ARTYPE2")

    area_1_other = AreaFactory(area_type=area_type_3, p_code="AREA1-ARTYPE-AFG2")
    area_2_other = AreaFactory(area_type=area_type_3, p_code="AREA2-ARTYPE-AFG2")

    other_ba = BusinessAreaFactory(name="Other")
    other_country = CountryFactory(name="Other Country", iso_code3="OTH")
    other_country.business_areas.set([other_ba])
    other_area_type = AreaTypeFactory(country=other_country)
    other_area = AreaFactory(area_type=other_area_type, p_code="AREA-OTHER")

    return {
        "country_1": country_1,
        "country_2": country_2,
        "area_type_1": area_type_1,
        "area_type_2": area_type_2,
        "area_type_3": area_type_3,
        "areas": [
            area_1_l1,
            area_2_l1,
            area_1_l2,
            area_2_l2,
            area_3_l2,
            area_1_other,
            area_2_other,
        ],
        "excluded_area": other_area,
    }


@pytest.fixture
def areas_list_url(afghanistan):
    return reverse(
        "api:geo:areas-list",
        kwargs={"business_area_slug": "afghanistan"},
    )


@pytest.fixture
def grant_user_permissions(create_user_role_with_permissions, user, afghanistan):
    def _grant(perms):
        create_user_role_with_permissions(user, perms, afghanistan)

    return _grant


@pytest.fixture
def grant_partner_permissions(create_partner_role_with_permissions, partner, afghanistan):
    def _grant(perms):
        create_partner_role_with_permissions(partner, perms, afghanistan)

    return _grant


@pytest.mark.parametrize(
    ("user_perms", "partner_perms", "expected_status"),
    [
        ([], [], status.HTTP_403_FORBIDDEN),
        ([Permissions.GEO_VIEW_LIST], [], status.HTTP_200_OK),
        ([], [Permissions.GEO_VIEW_LIST], status.HTTP_200_OK),
        ([Permissions.GEO_VIEW_LIST], [Permissions.GEO_VIEW_LIST], status.HTTP_200_OK),
    ],
)
def test_areas_permissions(
    api,
    areas_list_url,
    grant_user_permissions,
    grant_partner_permissions,
    user_perms,
    partner_perms,
    expected_status,
):
    grant_user_permissions(user_perms)
    grant_partner_permissions(partner_perms)

    response = api.get(areas_list_url)
    assert response.status_code == expected_status


def test_list_areas(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    response = api.get(areas_list_url)
    assert response.status_code == status.HTTP_200_OK

    response_ids = {item["id"] for item in response.json()}
    expected_ids = {str(area.id) for area in geo_data["areas"]}

    assert response_ids == expected_ids


def test_list_areas_filter_by_level(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    response = api.get(areas_list_url, {"level": 1})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 4


def test_list_areas_filter_by_parent_id(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    parent = geo_data["areas"][0]
    response = api.get(areas_list_url, {"parent_id": parent.id})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


def test_list_areas_search_by_name(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    response = api.get(areas_list_url, {"name": "Area 1"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 7


def test_list_areas_caching(api, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        assert response.status_code == status.HTTP_200_OK
        etag = response.headers["etag"]
        assert len(ctx.captured_queries) == 10

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        assert response.headers["etag"] == etag
        assert len(ctx.captured_queries) == 5


def test_areas_tree(api, ukraine_with_area_tree, user, create_user_role_with_permissions):
    ba = ukraine_with_area_tree
    create_user_role_with_permissions(
        user,
        [Permissions.GEO_VIEW_LIST],
        ba,
    )
    response = api.get(
        reverse(
            "api:geo:areas-all-areas-tree",
            kwargs={"business_area_slug": "ukraine"},
        )
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    # Province
    assert data[0]["name"] == "Province 1"
    # State
    assert data[0]["areas"][0]["name"] == "State 2"
    # County
    assert data[0]["areas"][0]["areas"][0]["name"] == "County 3"
