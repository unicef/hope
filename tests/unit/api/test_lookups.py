from datetime import UTC, datetime, timedelta

from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.payment import FinancialInstitutionFactory
from hope.models import APIToken, Area, AreaType, Country, FinancialInstitution, Program
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------
# Response helpers
# ---------------------------------------------------------------------------


def _country_response(country: Country) -> dict:
    return {
        "id": str(country.id),
        "name": country.name,
        "short_name": country.short_name,
        "iso_code2": country.iso_code2,
        "iso_code3": country.iso_code3,
        "iso_num": country.iso_num,
        "updated_at": country.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_from": country.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_until": country.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def _area_response(area: Area) -> dict:
    return {
        "id": str(area.id),
        "created_at": area.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_at": area.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "original_id": area.original_id,
        "name": area.name,
        "p_code": area.p_code,
        "valid_from": area.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_until": area.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extras": area.extras,
        "lft": area.lft,
        "rght": area.rght,
        "tree_id": area.tree_id,
        "level": area.level,
        "latitude": area.latitude,
        "longitude": area.longitude,
        "parent": str(area.parent.id) if area.parent else None,
        "area_type": str(area.area_type.id),
    }


def _area_type_response(area_type: AreaType) -> dict:
    return {
        "id": str(area_type.id),
        "created_at": area_type.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_at": area_type.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "original_id": area_type.original_id,
        "name": area_type.name,
        "area_level": area_type.area_level,
        "valid_from": area_type.valid_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "valid_until": area_type.valid_until.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "extras": area_type.extras,
        "lft": area_type.lft,
        "rght": area_type.rght,
        "tree_id": area_type.tree_id,
        "level": area_type.level,
        "country": str(area_type.country.id),
        "parent": str(area_type.parent.id) if area_type.parent else None,
    }


def _fi_response(fi: FinancialInstitution) -> dict:
    return {
        "id": fi.id,
        "name": fi.name,
        "type": fi.type,
        "swift_code": fi.swift_code or "",
        "country_iso_code3": fi.country.iso_code3 if fi.country else None,
        "updated_at": fi.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ") if fi.updated_at else None,
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client_read(api_token: APIToken, token_api_client: APIClient) -> APIClient:
    api_token.grants = [Grant.API_READ_ONLY.name]
    api_token.save(update_fields=["grants"])
    return token_api_client


@pytest.fixture
def poland_country(db) -> Country:
    country = CountryFactory(
        name="Poland",
        short_name="Poland",
        iso_code2="PL",
        iso_code3="POL",
        iso_num="0620",
    )
    country.valid_from = datetime(2020, 1, 1, tzinfo=UTC)
    country.valid_until = datetime(2020, 12, 31, tzinfo=UTC)
    country.save(update_fields=["valid_from", "valid_until"])
    return country


@pytest.fixture
def afghanistan_country_lookups(db) -> Country:
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="0004",
    )
    country.valid_from = datetime(2019, 1, 1, tzinfo=UTC)
    country.valid_until = datetime(2021, 12, 31, tzinfo=UTC)
    country.save(update_fields=["valid_from", "valid_until"])
    return country


@pytest.fixture
def area_type_poland(poland_country: Country) -> AreaType:
    at = AreaTypeFactory(name="areatype1", country=poland_country, area_level=1)
    at.valid_until = datetime(2010, 12, 31, tzinfo=UTC)
    at.save(update_fields=["valid_until"])
    return at


@pytest.fixture
def area_type_afghanistan(afghanistan_country_lookups: Country, area_type_poland: AreaType) -> AreaType:
    at = AreaTypeFactory(
        name="areatype2",
        country=afghanistan_country_lookups,
        area_level=2,
        parent=area_type_poland,
    )
    at.valid_until = datetime(2010, 12, 31, tzinfo=UTC)
    at.save(update_fields=["valid_until"])
    return at


@pytest.fixture
def area_poland(area_type_poland: AreaType) -> Area:
    area = AreaFactory(name="area1", area_type=area_type_poland)
    area.valid_from = datetime(2010, 1, 1, tzinfo=UTC)
    area.valid_until = datetime(2010, 12, 31, tzinfo=UTC)
    area.save(update_fields=["valid_from", "valid_until"])
    return area


@pytest.fixture
def area_afghanistan(area_type_afghanistan: AreaType, area_poland: Area) -> Area:
    area = AreaFactory(name="area2", area_type=area_type_afghanistan, parent=area_poland)
    area.valid_from = datetime(2020, 1, 1, tzinfo=UTC)
    area.valid_until = datetime(2020, 12, 31, tzinfo=UTC)
    area.save(update_fields=["valid_from", "valid_until"])
    return area


@pytest.fixture
def fi_bank(poland_country: Country) -> FinancialInstitution:
    return FinancialInstitutionFactory(
        name="Test Bank",
        type=FinancialInstitution.FinancialInstitutionType.BANK,
        country=poland_country,
        swift_code="TESTBANK123",
    )


@pytest.fixture
def fi_telco(afghanistan_country_lookups: Country) -> FinancialInstitution:
    return FinancialInstitutionFactory(
        name="Test Telco",
        type=FinancialInstitution.FinancialInstitutionType.TELCO,
        country=afghanistan_country_lookups,
        swift_code="TESTTELCO456",
    )


@pytest.fixture
def fi_other(db) -> FinancialInstitution:
    return FinancialInstitutionFactory(
        name="Test Other Institution",
        type=FinancialInstitution.FinancialInstitutionType.OTHER,
        country=None,
        swift_code="",
    )


# ===========================================================================
# Program statuses
# ===========================================================================


def test_get_program_statuses(api_client_read: APIClient) -> None:
    url = reverse("api:program-statuses-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dict(Program.STATUS_CHOICE)


# ===========================================================================
# Countries
# ===========================================================================


def test_get_countries(
    api_client_read: APIClient,
    poland_country: Country,
    afghanistan_country_lookups: Country,
) -> None:
    url = reverse("api:country-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["results"] == [
        _country_response(afghanistan_country_lookups),
        _country_response(poland_country),
    ]
    assert "next" in response.json()


@pytest.mark.parametrize(
    ("filter_params", "expected_count"),
    [
        pytest.param({"valid_from_before": "2019-01-02"}, 1, id="valid_from_before"),
        pytest.param({"valid_from_after": "2019-01-02"}, 1, id="valid_from_after"),
        pytest.param({"valid_until_before": "2022-01-01"}, 2, id="valid_until_before"),
        pytest.param({"valid_until_after": "2021-12-30"}, 1, id="valid_until_after"),
    ],
)
def test_get_countries_filter_valid_from_until(
    api_client_read: APIClient,
    poland_country: Country,
    afghanistan_country_lookups: Country,
    filter_params: dict,
    expected_count: int,
) -> None:
    url = reverse("api:country-list")
    response = api_client_read.get(url, filter_params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == expected_count


@pytest.mark.parametrize(
    ("search_term", "expected_name"),
    [
        pytest.param("Afghanistan", "Afghanistan", id="by_short_name_af"),
        pytest.param("0004", "Afghanistan", id="by_iso_num_af"),
        pytest.param("Poland", "Poland", id="by_short_name_pl"),
        pytest.param("PL", "Poland", id="by_iso_code2_pl"),
        pytest.param("POL", "Poland", id="by_iso_code3_pl"),
    ],
)
def test_get_countries_search(
    api_client_read: APIClient,
    poland_country: Country,
    afghanistan_country_lookups: Country,
    search_term: str,
    expected_name: str,
) -> None:
    url = reverse("api:country-list")
    response = api_client_read.get(url, {"search": search_term})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == expected_name


# ===========================================================================
# Areas
# ===========================================================================


def test_get_area_list(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
) -> None:
    url = reverse("api:area-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert _area_response(area_poland) in results
    assert _area_response(area_afghanistan) in results


@pytest.mark.parametrize(
    ("filter_params", "expected_names"),
    [
        pytest.param({"country_iso_code2": "PL"}, ["area1"], id="country_iso2_pl"),
        pytest.param({"country_iso_code2": "AF"}, ["area2"], id="country_iso2_af"),
        pytest.param({"country_iso_code3": "POL"}, ["area1"], id="country_iso3_pol"),
        pytest.param({"country_iso_code3": "AFG"}, ["area2"], id="country_iso3_afg"),
        pytest.param({"valid_from_before": "2011-01-01"}, ["area1"], id="valid_from_before"),
        pytest.param({"valid_from_after": "2011-01-01"}, ["area2"], id="valid_from_after"),
        pytest.param({"valid_until_before": "2021-01-01"}, ["area1", "area2"], id="valid_until_before"),
        pytest.param({"valid_until_after": "2021-01-01"}, [], id="valid_until_after"),
        pytest.param({"area_type_area_level": 1}, ["area1"], id="area_level_1"),
        pytest.param({"area_type_area_level": 2}, ["area2"], id="area_level_2"),
    ],
)
def test_get_area_list_filter(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
    filter_params: dict,
    expected_names: list[str],
) -> None:
    url = reverse("api:area-list")
    response = api_client_read.get(url, filter_params)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == len(expected_names)
    result_names = {r["name"] for r in results}
    assert result_names == set(expected_names)


def test_get_area_list_filter_by_parent_with_children(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
) -> None:
    url = reverse("api:area-list")

    response = api_client_read.get(url, {"parent_id": str(area_poland.id)})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == "area2"

    response = api_client_read.get(url, {"parent_p_code": area_poland.p_code})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == "area2"


def test_get_area_list_filter_by_parent_without_children(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
) -> None:
    url = reverse("api:area-list")

    response = api_client_read.get(url, {"parent_id": str(area_afghanistan.id)})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 0

    response = api_client_read.get(url, {"parent_p_code": area_afghanistan.p_code})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 0


@pytest.mark.parametrize(
    ("search_term", "expected_name"),
    [
        pytest.param("area1", "area1", id="by_name_area1"),
        pytest.param("area2", "area2", id="by_name_area2"),
    ],
)
def test_get_area_list_search_by_name(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
    search_term: str,
    expected_name: str,
) -> None:
    url = reverse("api:area-list")
    response = api_client_read.get(url, {"search": search_term})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == expected_name


def test_get_area_list_search_by_p_code(
    api_client_read: APIClient,
    area_poland: Area,
    area_afghanistan: Area,
) -> None:
    url = reverse("api:area-list")

    response = api_client_read.get(url, {"search": area_poland.p_code})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == "area1"

    response = api_client_read.get(url, {"search": area_afghanistan.p_code})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == "area2"


# ===========================================================================
# Area types
# ===========================================================================


def test_get_area_type_list(
    api_client_read: APIClient,
    area_type_poland: AreaType,
    area_type_afghanistan: AreaType,
) -> None:
    url = reverse("api:areatype-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert _area_type_response(area_type_poland) in results
    assert _area_type_response(area_type_afghanistan) in results


@pytest.mark.parametrize(
    ("filter_params", "expected_count"),
    [
        pytest.param({"country_iso_code2": "PL"}, 1, id="country_iso2_pl"),
        pytest.param({"country_iso_code2": "AF"}, 1, id="country_iso2_af"),
        pytest.param({"country_iso_code3": "POL"}, 1, id="country_iso3_pol"),
        pytest.param({"country_iso_code3": "AFG"}, 1, id="country_iso3_afg"),
        pytest.param({"area_level": 1}, 1, id="area_level_1"),
        pytest.param({"area_level": 2}, 1, id="area_level_2"),
        pytest.param({"parent_area_level": 1}, 1, id="parent_level_1"),
        pytest.param({"parent_area_level": 2}, 0, id="parent_level_2"),
    ],
)
def test_get_area_type_list_filter(
    api_client_read: APIClient,
    area_type_poland: AreaType,
    area_type_afghanistan: AreaType,
    filter_params: dict,
    expected_count: int,
) -> None:
    url = reverse("api:areatype-list")
    response = api_client_read.get(url, filter_params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == expected_count


@pytest.mark.parametrize(
    ("search_term", "expected_name"),
    [
        pytest.param("areatype1", "areatype1", id="areatype1"),
        pytest.param("areatype2", "areatype2", id="areatype2"),
    ],
)
def test_get_area_type_list_search(
    api_client_read: APIClient,
    area_type_poland: AreaType,
    area_type_afghanistan: AreaType,
    search_term: str,
    expected_name: str,
) -> None:
    url = reverse("api:areatype-list")
    response = api_client_read.get(url, {"search": search_term})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["name"] == expected_name


# ===========================================================================
# Financial institutions
# ===========================================================================


def test_get_financial_institution_list(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
    fi_telco: FinancialInstitution,
    fi_other: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert _fi_response(fi_bank) in results
    assert _fi_response(fi_telco) in results
    assert _fi_response(fi_other) in results


def test_get_financial_institution_list_ordering(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
    fi_telco: FinancialInstitution,
    fi_other: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    names = [r["name"] for r in response.json()["results"]]
    assert names == sorted(names)


def test_get_financial_institution_list_pagination(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
    fi_telco: FinancialInstitution,
    fi_other: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "next" in data
    assert "previous" in data
    assert "results" in data


@pytest.mark.parametrize(
    ("institution_type", "expected_name"),
    [
        pytest.param("bank", "Test Bank", id="bank"),
        pytest.param("telco", "Test Telco", id="telco"),
        pytest.param("other", "Test Other Institution", id="other"),
    ],
)
def test_get_financial_institution_list_filter_by_type(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
    fi_telco: FinancialInstitution,
    fi_other: FinancialInstitution,
    institution_type: str,
    expected_name: str,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url, {"type": institution_type})
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 1
    assert results[0]["name"] == expected_name
    assert results[0]["type"] == institution_type


_now = timezone.now()
_yesterday = (_now - timedelta(days=1)).strftime("%Y-%m-%d")
_tomorrow = (_now + timedelta(days=1)).strftime("%Y-%m-%d")


@pytest.mark.parametrize(
    ("filter_params", "expected_count"),
    [
        pytest.param({"updated_at_after": _yesterday}, 3, id="after_yesterday"),
        pytest.param({"updated_at_before": _tomorrow}, 3, id="before_tomorrow"),
        pytest.param(
            {"updated_at_after": _yesterday, "updated_at_before": _tomorrow},
            3,
            id="between_yesterday_and_tomorrow",
        ),
    ],
)
def test_get_financial_institution_list_filter_by_updated_at(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
    fi_telco: FinancialInstitution,
    fi_other: FinancialInstitution,
    filter_params: dict,
    expected_count: int,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url, filter_params)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == expected_count


def test_get_financial_institution_list_filter_invalid_type(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    response = api_client_read.get(url, {"type": "invalid_type"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_get_financial_institution_list_filter_future_date_returns_empty(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    future_date = (timezone.now() + timedelta(days=365)).strftime("%Y-%m-%d")
    response = api_client_read.get(url, {"updated_at_after": future_date})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 0


def test_get_financial_institution_list_filter_past_date_returns_empty(
    api_client_read: APIClient,
    fi_bank: FinancialInstitution,
) -> None:
    url = reverse("api:financial-institution-list")
    past_date = (timezone.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    response = api_client_read.get(url, {"updated_at_before": past_date})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 0
