import pytest

from hope.models import BusinessArea, User

BUSINESS_AREA_TIMEZONE = "Africa/Nairobi"
PERSONAL_TIMEZONE = "Europe/Warsaw"


@pytest.fixture
def nairobi_business_area(business_area: BusinessArea) -> BusinessArea:
    """Afghanistan on a non-UTC timezone.

    The shared fixture seeds "UTC", which is also the fallback used when
    resolution fails - a test asserting against it would pass even if
    inheritance were broken.
    """
    business_area.timezone = BUSINESS_AREA_TIMEZONE
    business_area.save(update_fields=["timezone"])
    return business_area


@pytest.fixture
def logged_in_user(nairobi_business_area: BusinessArea) -> User:
    """The user the `login` fixture authenticates as, with no timezone preference."""
    user = User.objects.get(username="superuser")
    user.timezone = None
    user.save(update_fields=["timezone"])
    return user


@pytest.fixture
def user_with_timezone_preference(logged_in_user: User) -> User:
    logged_in_user.timezone = PERSONAL_TIMEZONE
    logged_in_user.save(update_fields=["timezone"])
    return logged_in_user
