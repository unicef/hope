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

    area_1_l1 = AreaFactory(area_type=area_type_1, p_code="AREA1-ARTYPE1", name="Area_1")
    area_2_l1 = AreaFactory(area_type=area_type_1, p_code="AREA2-ARTYPE1", name="Area_2")

    area_1_l2 = AreaFactory(area_type=area_type_2, parent=area_1_l1, p_code="AREA1-ARTYPE2", name="Area_21")
    area_2_l2 = AreaFactory(area_type=area_type_2, parent=area_2_l1, p_code="AREA2-ARTYPE2", name="Area_22")
    area_3_l2 = AreaFactory(area_type=area_type_2, parent=area_1_l1, p_code="AREA3-ARTYPE2", name="Area_23")

    area_1_other = AreaFactory(area_type=area_type_3, p_code="AREA1-ARTYPE-AFG2", name="Area_11")
    area_2_other = AreaFactory(area_type=area_type_3, p_code="AREA2-ARTYPE-AFG2", name="Area_12")

    other_ba = BusinessAreaFactory(name="Other")
    other_country = CountryFactory(name="Other Country", iso_code3="OTH")
    other_country.business_areas.set([other_ba])
    other_area_type = AreaTypeFactory(country=other_country)
    other_area = AreaFactory(area_type=other_area_type, p_code="AREA-OTHER", name="Other Area")

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
    area = geo_data["areas"][0]
    resp_area = response.json()[0]

    assert response_ids == expected_ids
    assert "id" in resp_area
    assert resp_area["id"] == str(area.id)
    assert "name" in resp_area
    assert resp_area["name"] == area.name
    assert "p_code" in resp_area
    assert resp_area["p_code"] == area.p_code
    assert "area_type" in resp_area
    assert resp_area["area_type"] == str(area.area_type.id)
    assert "updated_at" in resp_area
    assert resp_area["updated_at"] == f"{area.updated_at:%Y-%m-%dT%H:%M:%SZ}"


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


def test_list_areas_filter_by_parent_p_code(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])
    response = api.get(areas_list_url, {"parent_p_code": "AREA1-ARTYPE1"})

    assert response.status_code == status.HTTP_200_OK
    # Area_21, Area_23
    assert len(response.json()) == 2


def test_list_areas_search_by_name(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])
    area_name = Area.objects.filter(p_code="AREA1-ARTYPE1").first().name
    count = Area.objects.filter(name__startswith=area_name).count()
    response = api.get(areas_list_url, {"name": area_name})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == count


def test_list_areas_caching(api, geo_data, areas_list_url, grant_user_permissions):
    grant_user_permissions([Permissions.GEO_VIEW_LIST])

    def assert_cached_response(response, expected_queries):
        assert response.status_code == status.HTTP_200_OK
        return response.headers["etag"]

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_initial = assert_cached_response(response, expected_queries=10)
        assert len(ctx.captured_queries) == 10

    # Test that reoccurring requests use cached data
    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_second = assert_cached_response(response, expected_queries=5)
        assert len(ctx.captured_queries) == 5
        assert etag_second == etag_initial

    # After update of area, it does not use the cached data
    area_1_area_type_1 = geo_data["areas"][0]
    area_1_area_type_1.name = "Updated Area 1 Area Type 1"
    area_1_area_type_1.save()

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_after_area_update = assert_cached_response(response, expected_queries=6)
        assert len(ctx.captured_queries) == 6
        assert etag_after_area_update != etag_initial

    # After removing area_type, it does not use the cached data
    area_type_1_afg = geo_data["area_type_1"]
    area_type_1_afg.delete()

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_after_area_type_delete = assert_cached_response(response, expected_queries=6)
        assert len(ctx.captured_queries) == 6
        assert etag_after_area_type_delete != etag_after_area_update

    # After removing country, it does not use the cached data
    country_2_afg = geo_data["country_2"]
    country_2_afg.delete()

    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_after_country_delete = assert_cached_response(response, expected_queries=6)
        assert len(ctx.captured_queries) == 6
        assert etag_after_country_delete != etag_after_area_type_delete

    # Cached data again
    with CaptureQueriesContext(connection) as ctx:
        response = api.get(areas_list_url)
        etag_cached_again = assert_cached_response(response, expected_queries=5)
        assert len(ctx.captured_queries) == 5
        assert etag_cached_again == etag_after_country_delete

    # Different filter - does not use cached data
    with CaptureQueriesContext(connection):
        response = api.get(areas_list_url, {"level": 1})
        etag_with_filter = assert_cached_response(response, expected_queries=None)
        assert etag_with_filter != etag_cached_again


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
