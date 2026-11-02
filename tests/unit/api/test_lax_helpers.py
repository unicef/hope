from unittest.mock import MagicMock, patch

from django.core.exceptions import SuspiciousOperation
import pytest

from hope.api.endpoints.rdi.lax import CreateLaxHouseholds, clean_image_flex_fields, get_storage_file_error


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


def test_get_storage_file_error_existing_file(stored_image: str) -> None:
    assert get_storage_file_error(stored_image) is None


def test_get_storage_file_error_missing_file() -> None:
    assert get_storage_file_error("cw_files/missing.png") == "File 'cw_files/missing.png' does not exist in storage."


@pytest.mark.parametrize(
    "file_name",
    [
        "",
        "../etc/passwd.png",
        "cw_files/../x.png",
        "cw_files/./x.png",
        "cw_files//x.png",
        "cw_files\\x.png",
        "x\x00.png",
    ],
)
def test_get_storage_file_error_invalid_file_name(file_name: str) -> None:
    assert get_storage_file_error(file_name) == f"Invalid file name '{file_name}'."


def test_get_storage_file_error_not_an_image() -> None:
    assert get_storage_file_error("cw_files/x.exe") == "File 'cw_files/x.exe' is not a supported image type."


def test_get_storage_file_error_too_long() -> None:
    assert get_storage_file_error("cw_files/x.png", max_length=10) == "File name must have no more than 10 characters."


@pytest.mark.parametrize("storage_error", [SuspiciousOperation, ValueError])
@patch("hope.api.endpoints.rdi.lax.default_storage")
def test_get_storage_file_error_storage_rejects_name(mock_storage: MagicMock, storage_error: type[Exception]) -> None:
    mock_storage.exists.side_effect = storage_error

    assert get_storage_file_error("cw_files/x.png") == "Invalid file name 'cw_files/x.png'."


def test_clean_image_flex_fields_normalizes_valid_value(stored_image: str) -> None:
    flex_fields = {"photo": f"/{stored_image}", "note": "/not/an/image"}

    errors = clean_image_flex_fields(flex_fields, {"photo"})

    assert errors == {}
    assert flex_fields == {"photo": stored_image, "note": "/not/an/image"}


def test_clean_image_flex_fields_missing_file() -> None:
    flex_fields = {"photo": "cw_files/missing.png"}

    errors = clean_image_flex_fields(flex_fields, {"photo"})

    assert errors == {"photo": ["File 'cw_files/missing.png' does not exist in storage."]}
    assert flex_fields == {"photo": "cw_files/missing.png"}


def test_clean_image_flex_fields_non_string_value() -> None:
    assert clean_image_flex_fields({"photo": 12345}, {"photo"}) == {"photo": ["Expected a file name."]}


@pytest.mark.parametrize("flex_fields", [None, {}, {"photo": ""}, {"photo": None}, {"other": "x"}])
def test_clean_image_flex_fields_nothing_to_check(flex_fields: dict | None) -> None:
    assert clean_image_flex_fields(flex_fields, {"photo"}) == {}
