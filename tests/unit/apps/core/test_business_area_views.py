import json
from typing import Any
from unittest.mock import patch

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    BusinessAreaFactory,
    CountryFactory,
    FlexibleAttributeChoiceFactory,
    FlexibleAttributeFactory,
    PartnerFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.models import FlexibleAttribute, PeriodicFieldData

pytestmark = pytest.mark.django_db


# === Fixtures ===


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def business_area_with_kobo_token():
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", kobo_token="123")


@pytest.fixture
def business_area_afghanistan():
    return BusinessAreaFactory(slug="afghanistan", name="Afghanistan", active=True)


@pytest.fixture
def business_area_ukraine():
    return BusinessAreaFactory(slug="ukraine", active=True)


@pytest.fixture
def business_area_syria():
    return BusinessAreaFactory(slug="syria", active=True)


@pytest.fixture
def business_area_croatia():
    return BusinessAreaFactory(slug="croatia", active=True)


@pytest.fixture
def business_area_sudan():
    return BusinessAreaFactory(slug="sudan", active=True)


@pytest.fixture
def business_area_somalia():
    return BusinessAreaFactory(slug="somalia", active=False)


@pytest.fixture
def partner():
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user_with_partner(partner):
    return UserFactory(partner=partner)


@pytest.fixture
def authenticated_client(api_client, user_with_partner):
    return api_client(user_with_partner)


@pytest.fixture
def setup_business_areas_with_permissions(
    business_area_afghanistan,
    business_area_ukraine,
    business_area_syria,
    business_area_croatia,
    business_area_somalia,
    user_with_partner,
    partner,
    create_user_role_with_permissions,
    create_partner_role_with_permissions,
):
    country_afg = CountryFactory(name="Afghanistan")
    business_area_afghanistan.countries.set([country_afg])

    create_user_role_with_permissions(
        user_with_partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_afghanistan,
        whole_business_area_access=True,
    )
    create_user_role_with_permissions(
        user_with_partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_ukraine,
        program=ProgramFactory(business_area=business_area_ukraine),
    )
    create_partner_role_with_permissions(
        partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_syria,
        whole_business_area_access=True,
    )
    create_partner_role_with_permissions(
        partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_croatia,
        program=ProgramFactory(business_area=business_area_croatia),
    )
    create_partner_role_with_permissions(
        partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_somalia,
        whole_business_area_access=True,
    )

    return {
        "afghanistan": business_area_afghanistan,
        "ukraine": business_area_ukraine,
        "syria": business_area_syria,
        "croatia": business_area_croatia,
        "somalia": business_area_somalia,
    }


@pytest.fixture
def setup_flexible_attributes(business_area_afghanistan):
    flex_field_1 = FlexibleAttributeFactory(
        type=FlexibleAttribute.STRING,
        label={"English(EN)": "Flex Field 1"},
        name="flex_field_1",
    )
    flex_field_2 = FlexibleAttributeFactory(
        type=FlexibleAttribute.INTEGER,
        label={"English(EN)": "Muac"},
        name="muac",
    )
    choice_1 = FlexibleAttributeChoiceFactory(
        label={"English(EN)": "Choice 1"},
        name="option_1",
        list_name="Option 1",
    )
    choice_2 = FlexibleAttributeChoiceFactory(
        label={"English(EN)": "Choice 2"},
        name="option_2",
        list_name="Option 2",
    )
    choice_1.flex_attributes.add(flex_field_1)
    choice_2.flex_attributes.add(flex_field_2)

    program = ProgramFactory(business_area=business_area_afghanistan)

    pdu_data = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING,
        number_of_rounds=1,
        rounds_names=["January"],
    )
    FlexibleAttributeFactory(
        label={"English(EN)": "PDU Field 1"},
        name="pdu_field_1",
        type=FlexibleAttribute.PDU,
        program=program,
        pdu_data=pdu_data,
    )

    return {
        "business_area": business_area_afghanistan,
        "program": program,
        "flex_field_1": flex_field_1,
        "flex_field_2": flex_field_2,
    }


# === Tests: Business Area List ===


def test_business_area_list_returns_accessible_areas(
    authenticated_client: Any,
    business_area_sudan: Any,
    setup_business_areas_with_permissions: dict,
) -> None:
    areas = setup_business_areas_with_permissions
    list_url = reverse("api:core:business-areas-list")

    response = authenticated_client.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 5
    business_area_ids = {ba["id"] for ba in response_data}
    assert str(areas["afghanistan"].id) in business_area_ids
    assert str(areas["ukraine"].id) in business_area_ids
    assert str(areas["syria"].id) in business_area_ids
    assert str(areas["croatia"].id) in business_area_ids
    assert str(areas["somalia"].id) in business_area_ids
    assert str(business_area_sudan.id) not in business_area_ids


def test_business_area_list_returns_correct_fields_for_area(
    authenticated_client: Any,
    setup_business_areas_with_permissions: dict,
) -> None:
    areas = setup_business_areas_with_permissions
    afghanistan = areas["afghanistan"]
    list_url = reverse("api:core:business-areas-list")

    response = authenticated_client.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    afghanistan_data = next(ba for ba in response_data if ba["slug"] == "afghanistan")
    assert afghanistan_data["id"] == str(afghanistan.id)
    assert afghanistan_data["name"] == afghanistan.name
    assert afghanistan_data["code"] == afghanistan.code
    assert afghanistan_data["long_name"] == afghanistan.long_name
    assert afghanistan_data["slug"] == afghanistan.slug
    assert afghanistan_data["parent"] == afghanistan.parent
    assert afghanistan_data["is_split"] == afghanistan.is_split
    assert afghanistan_data["active"] == afghanistan.active
    assert len(afghanistan_data["countries"]) == 1
    assert afghanistan_data["countries"][0]["name"] == "Afghanistan"


def test_business_area_count_returns_correct_number(
    authenticated_client: Any,
    business_area_sudan: Any,
    setup_business_areas_with_permissions: dict,
) -> None:
    count_url = reverse("api:core:business-areas-count")

    response = authenticated_client.get(count_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 5


def test_business_area_list_caching_works_correctly(
    authenticated_client: Any,
    user_with_partner: Any,
    business_area_sudan: Any,
    setup_business_areas_with_permissions: dict,
    create_user_role_with_permissions: Any,
) -> None:
    areas = setup_business_areas_with_permissions
    list_url = reverse("api:core:business-areas-list")

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 5
        assert len(ctx.captured_queries) == 7

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 5

    areas["afghanistan"].active = False
    areas["afghanistan"].save()
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_third_call = response.headers["etag"]
        assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
        assert etag_third_call not in [etag, etag_second_call]
        assert len(ctx.captured_queries) == 7

    create_user_role_with_permissions(
        user_with_partner,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        business_area_sudan,
        whole_business_area_access=True,
    )
    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fourth_call = response.headers["etag"]
        assert json.loads(cache.get(etag_fourth_call)[0].decode("utf8")) == response.json()
        assert etag_fourth_call not in [etag, etag_second_call, etag_third_call]
        assert len(response.json()["results"]) == 6
        assert len(ctx.captured_queries) == 7

    with CaptureQueriesContext(connection) as ctx:
        response = authenticated_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fifth_call = response.headers["etag"]
        assert etag_fifth_call == etag_fourth_call
        assert len(ctx.captured_queries) == 5


# === Tests: Business Area Detail ===


def test_business_area_detail_returns_correct_data(
    api_client: Any,
    user: Any,
    business_area_with_kobo_token: Any,
    create_user_role_with_permissions: Any,
) -> None:
    afghanistan = business_area_with_kobo_token
    client = api_client(user)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        whole_business_area_access=True,
    )
    detail_url = reverse("api:core:business-areas-detail", kwargs={"slug": afghanistan.slug})

    response = client.get(detail_url)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == str(afghanistan.id)
    assert response_data["name"] == afghanistan.name
    assert response_data["code"] == afghanistan.code
    assert response_data["long_name"] == afghanistan.long_name
    assert response_data["slug"] == afghanistan.slug
    assert response_data["parent"] == afghanistan.parent
    assert response_data["is_split"] == afghanistan.is_split
    assert response_data["active"] == afghanistan.active


# === Tests: Business Area Filter ===


def test_filter_by_active_true_returns_only_active_areas(
    authenticated_client: Any,
    business_area_sudan: Any,
    setup_business_areas_with_permissions: dict,
) -> None:
    areas = setup_business_areas_with_permissions
    list_url = reverse("api:core:business-areas-list")

    response = authenticated_client.get(list_url, {"active": True})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 4
    business_area_ids = {ba["id"] for ba in response_data}
    assert str(areas["afghanistan"].id) in business_area_ids
    assert str(areas["ukraine"].id) in business_area_ids
    assert str(areas["syria"].id) in business_area_ids
    assert str(areas["croatia"].id) in business_area_ids
    assert str(business_area_sudan.id) not in business_area_ids
    assert str(areas["somalia"].id) not in business_area_ids


def test_filter_by_active_false_returns_only_inactive_areas(
    authenticated_client: Any,
    business_area_sudan: Any,
    setup_business_areas_with_permissions: dict,
) -> None:
    areas = setup_business_areas_with_permissions
    list_url = reverse("api:core:business-areas-list")

    response = authenticated_client.get(list_url, {"active": False})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()["results"]
    assert len(response_data) == 1
    business_area_ids = {ba["id"] for ba in response_data}
    assert str(areas["somalia"].id) in business_area_ids
    assert str(areas["afghanistan"].id) not in business_area_ids
    assert str(areas["ukraine"].id) not in business_area_ids
    assert str(areas["syria"].id) not in business_area_ids
    assert str(areas["croatia"].id) not in business_area_ids
    assert str(business_area_sudan.id) not in business_area_ids


# === Tests: Kobo Asset List ===


@patch("hope.apps.core.kobo.api.KoboAPI.__init__")
@patch("hope.apps.core.kobo.api.KoboAPI.get_all_projects_data")
def test_get_kobo_asset_list_returns_projects(
    mock_get_all_projects_data: Any,
    mock_kobo_init: Any,
    api_client: Any,
    user: Any,
    business_area_with_kobo_token: Any,
    create_user_role_with_permissions: Any,
) -> None:
    afghanistan = business_area_with_kobo_token
    client = api_client(user)
    create_user_role_with_permissions(
        user,
        [Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS],
        afghanistan,
        whole_business_area_access=True,
    )
    mock_kobo_init.return_value = None
    mock_get_all_projects_data.return_value = [
        {
            "name": "Registration 2025",
            "uid": "123",
            "has_deployment": True,
            "asset_type": "Type",
            "deployment__active": True,
            "downloads": [{"format": "xls", "url": "xlsx_url"}],
            "settings": {
                "sector": {"label": "Sector 123"},
                "country": {"label": "Country Test"},
            },
            "date_modified": "2022-02-22",
        },
        {
            "name": "Campain 123",
            "uid": "222",
            "has_deployment": True,
            "asset_type": "Type",
            "deployment__active": True,
            "downloads": [{"format": "xls", "url": "xlsx_url"}],
            "settings": {
                "sector": {"label": "Sector 123"},
                "country": {"label": "Country Test"},
            },
            "date_modified": "2022-02-22",
        },
    ]
    kobo_url = reverse("api:core:business-areas-all-kobo-projects", kwargs={"slug": afghanistan.slug})

    response = client.post(kobo_url, {"only_deployed": True}, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 2


# === Tests: All Fields Attributes ===


def test_all_fields_attributes_without_program(
    api_client: Any,
    user: Any,
    setup_flexible_attributes: dict,
) -> None:
    business_area = setup_flexible_attributes["business_area"]
    client = api_client(user)
    url = reverse("api:core:business-areas-all-fields-attributes", kwargs={"slug": business_area.slug})

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    response_data = response.data

    flex_field_names = {item["name"] for item in response_data if item["is_flex_field"]}
    assert "flex_field_1" in flex_field_names
    assert "muac" in flex_field_names

    core_fields = [item for item in response_data if not item["is_flex_field"]]
    assert len(core_fields) > 0

    assert "pdu_field_1" not in flex_field_names


def test_all_fields_attributes_with_program(
    api_client: Any,
    user: Any,
    setup_flexible_attributes: dict,
) -> None:
    business_area = setup_flexible_attributes["business_area"]
    program = setup_flexible_attributes["program"]
    client = api_client(user)
    url = reverse("api:core:business-areas-all-fields-attributes", kwargs={"slug": business_area.slug})

    response = client.get(url, {"program_id": str(program.id)})

    assert response.status_code == status.HTTP_200_OK
    response_data = response.data

    flex_field_names = {item["name"] for item in response_data if item["is_flex_field"]}
    assert "flex_field_1" in flex_field_names
    assert "muac" in flex_field_names

    assert "pdu_field_1" in flex_field_names

    pdu_field = next(item for item in response_data if item["name"] == "pdu_field_1")
    assert pdu_field["pdu_data"] is not None
    assert pdu_field["pdu_data"]["subtype"] == PeriodicFieldData.STRING
    assert pdu_field["pdu_data"]["number_of_rounds"] == 1
    assert pdu_field["pdu_data"]["rounds_names"] == ["January"]
