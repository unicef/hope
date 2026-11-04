from collections.abc import Callable
from unittest.mock import MagicMock, patch

import pytest

from hope.api.endpoints.rdi.lax import CreateLaxHouseholds, clean_image_flex_fields


@pytest.fixture
def mock_household() -> MagicMock:
    return MagicMock()


@patch("hope.api.endpoints.rdi.lax.PendingHousehold")
@patch("hope.api.endpoints.rdi.lax.Country")
def test_resolve_countries_empty_country_codes(
    mock_country: MagicMock, mock_pending_household_cls: MagicMock, mock_household: MagicMock
) -> None:
    """When country_codes is empty, Country.objects.filter should NOT be called."""
    CreateLaxHouseholds._resolve_countries_and_persist([{"instance": mock_household}], set())

    mock_country.objects.filter.assert_not_called()
    mock_pending_household_cls.objects.bulk_create.assert_called_once()
    args = mock_pending_household_cls.objects.bulk_create.call_args
    assert args[0][0] == [mock_household]


@patch("hope.api.endpoints.rdi.lax.PendingHousehold")
@patch("hope.api.endpoints.rdi.lax.Country")
def test_resolve_countries_payload_without_country_code(
    mock_country: MagicMock, mock_pending_household_cls: MagicMock, mock_household: MagicMock
) -> None:
    """When payload has no country_code/country_origin_code keys, hh attrs stay unchanged."""
    mock_household.country = "original_country"
    mock_household.country_origin = "original_origin"

    us_country = MagicMock()
    us_country.iso_code2 = "US"
    mock_country.objects.filter.return_value = [us_country]

    CreateLaxHouseholds._resolve_countries_and_persist([{"instance": mock_household}], {"US"})

    mock_country.objects.filter.assert_called_once_with(iso_code2__in={"US"})
    assert mock_household.country == "original_country"
    assert mock_household.country_origin == "original_origin"
    mock_pending_household_cls.objects.bulk_create.assert_called_once()


@patch("hope.api.endpoints.rdi.lax.PendingHousehold")
@patch("hope.api.endpoints.rdi.lax.Country")
def test_resolve_countries_with_country_and_origin(
    mock_country: MagicMock, mock_pending_household_cls: MagicMock, mock_household: MagicMock
) -> None:
    """When payload has country_code and country_origin_code, hh attrs are set from country_map."""
    us_country = MagicMock()
    us_country.iso_code2 = "US"
    ca_country = MagicMock()
    ca_country.iso_code2 = "CA"
    mock_country.objects.filter.return_value = [us_country, ca_country]

    CreateLaxHouseholds._resolve_countries_and_persist(
        [{"instance": mock_household, "country_code": "US", "country_origin_code": "CA"}], {"US", "CA"}
    )

    mock_country.objects.filter.assert_called_once_with(iso_code2__in={"US", "CA"})
    assert mock_household.country == us_country
    assert mock_household.country_origin == ca_country
    mock_pending_household_cls.objects.bulk_create.assert_called_once()


PREFIX = "AFG/ab12/"


def test_clean_image_flex_fields_normalizes_valid_value(store_image: Callable[[str], str]) -> None:
    file_name = store_image(f"{PREFIX}CW_ind_1_photo.png")
    flex_fields = {"photo": f"/{file_name}", "note": "/not/an/image"}

    errors = clean_image_flex_fields(flex_fields, {"photo"}, PREFIX)

    assert errors == {}
    assert flex_fields == {"photo": file_name, "note": "/not/an/image"}


def test_clean_image_flex_fields_missing_file() -> None:
    flex_fields = {"photo": f"{PREFIX}missing.png"}

    errors = clean_image_flex_fields(flex_fields, {"photo"}, PREFIX)

    assert errors == {"photo": [f"File '{PREFIX}missing.png' does not exist in storage."]}
    assert flex_fields == {"photo": f"{PREFIX}missing.png"}


def test_clean_image_flex_fields_file_of_another_program(store_image: Callable[[str], str]) -> None:
    file_name = store_image("OTH/zz99/CW_ind_1_photo.png")

    errors = clean_image_flex_fields({"photo": file_name}, {"photo"}, PREFIX)

    assert errors == {"photo": [f"File name must start with '{PREFIX}'."]}


def test_clean_image_flex_fields_name_longer_than_flex_field_limit() -> None:
    errors = clean_image_flex_fields({"photo": f"{PREFIX}{'a' * 1024}.png"}, {"photo"}, PREFIX)

    assert errors == {"photo": ["File name must have no more than 1024 characters."]}


def test_clean_image_flex_fields_non_string_value() -> None:
    assert clean_image_flex_fields({"photo": 12345}, {"photo"}, PREFIX) == {"photo": ["Expected a file name."]}


@pytest.mark.parametrize("flex_fields", [None, {}, {"photo": ""}, {"photo": None}, {"other": "x"}])
def test_clean_image_flex_fields_nothing_to_check(flex_fields: dict | None) -> None:
    assert clean_image_flex_fields(flex_fields, {"photo"}, PREFIX) == {}
