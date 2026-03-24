from unittest.mock import MagicMock, patch

import pytest

from hope.api.endpoints.rdi.lax import CreateLaxHouseholds


@pytest.fixture
def mock_household():
    return MagicMock()


@patch("hope.api.endpoints.rdi.lax.PendingHousehold")
@patch("hope.api.endpoints.rdi.lax.Country")
def test_resolve_countries_empty_country_codes(mock_country, mock_pending_household_cls, mock_household):
    """When country_codes is empty, Country.objects.filter should NOT be called."""
    CreateLaxHouseholds._resolve_countries_and_persist([{"instance": mock_household}], set())

    mock_country.objects.filter.assert_not_called()
    mock_pending_household_cls.objects.bulk_create.assert_called_once()
    args = mock_pending_household_cls.objects.bulk_create.call_args
    assert args[0][0] == [mock_household]


@patch("hope.api.endpoints.rdi.lax.PendingHousehold")
@patch("hope.api.endpoints.rdi.lax.Country")
def test_resolve_countries_payload_without_country_code(mock_country, mock_pending_household_cls, mock_household):
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
def test_resolve_countries_with_country_and_origin(mock_country, mock_pending_household_cls, mock_household):
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
