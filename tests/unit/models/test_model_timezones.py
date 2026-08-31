from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories import BusinessAreaFactory, CountryFactory, UserFactory
from hope.apps.core.timezones import resolve_timezone_name
from hope.models import BusinessArea, Country, User

pytestmark = pytest.mark.django_db


@pytest.fixture
def poland_country(db: None) -> Country:
    return CountryFactory(iso_code2="PL", iso_code3="POL")


@pytest.fixture
def unmapped_country(db: None) -> Country:
    return CountryFactory(iso_code2="XX", iso_code3="XXX")


@pytest.fixture
def united_states_country(db: None) -> Country:
    return CountryFactory(iso_code2="US", iso_code3="USA")


@pytest.fixture
def poland_business_area(poland_country: Country) -> BusinessArea:
    return BusinessAreaFactory(office_country=poland_country, timezone="Europe/Warsaw")


@pytest.fixture
def initialized_business_area(poland_country: Country) -> BusinessArea:
    return BusinessAreaFactory(office_country=poland_country, timezone=None)


@pytest.fixture
def business_area_without_office_country(db: None) -> BusinessArea:
    return BusinessAreaFactory(office_country=None, timezone=None)


@pytest.fixture
def business_area_with_unmapped_country(unmapped_country: Country) -> BusinessArea:
    return BusinessAreaFactory(office_country=unmapped_country, timezone=None)


@pytest.fixture
def business_area_with_explicit_timezone(poland_country: Country) -> BusinessArea:
    return BusinessAreaFactory(office_country=poland_country, timezone="America/New_York")


@pytest.fixture
def user_without_timezone(db: None) -> User:
    return UserFactory()


def test_business_area_timezone_is_initialized_from_office_country(initialized_business_area: BusinessArea) -> None:
    assert str(initialized_business_area.timezone) == "Europe/Warsaw"


def test_business_area_timezone_defaults_to_utc_without_office_country(
    business_area_without_office_country: BusinessArea,
) -> None:
    assert str(business_area_without_office_country.timezone) == "UTC"


def test_business_area_timezone_defaults_to_utc_for_unmapped_office_country(
    business_area_with_unmapped_country: BusinessArea,
) -> None:
    assert str(business_area_with_unmapped_country.timezone) == "UTC"


def test_business_area_explicit_timezone_takes_precedence_over_office_country(
    business_area_with_explicit_timezone: BusinessArea,
) -> None:
    assert str(business_area_with_explicit_timezone.timezone) == "America/New_York"


def test_business_area_timezone_is_not_replaced_when_office_country_changes(
    initialized_business_area: BusinessArea,
    united_states_country: Country,
) -> None:
    initialized_business_area.office_country = united_states_country
    initialized_business_area.save()

    assert str(initialized_business_area.timezone) == "Europe/Warsaw"


def test_user_timezone_takes_precedence(
    user_without_timezone: User,
    poland_business_area: BusinessArea,
) -> None:
    user_without_timezone.timezone = "America/New_York"

    assert resolve_timezone_name(user=user_without_timezone, business_area=poland_business_area) == "America/New_York"


def test_business_area_timezone_is_used_for_user_without_preference(
    user_without_timezone: User,
    poland_business_area: BusinessArea,
) -> None:
    assert resolve_timezone_name(user=user_without_timezone, business_area=poland_business_area) == "Europe/Warsaw"


def test_user_timezone_rejects_invalid_iana_identifier(user_without_timezone: User) -> None:
    user_without_timezone.timezone = "Mars/Olympus"

    with pytest.raises(ValidationError, match="Invalid timezone"):
        user_without_timezone.full_clean()


def test_business_area_timezone_rejects_invalid_iana_identifier(
    poland_business_area: BusinessArea,
) -> None:
    poland_business_area.timezone = "Mars/Olympus"

    with pytest.raises(ValidationError, match="Invalid timezone"):
        poland_business_area.full_clean()
