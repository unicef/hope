import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import User

from .conftest import BUSINESS_AREA_TIMEZONE, PERSONAL_TIMEZONE

pytestmark = pytest.mark.django_db()

PROFILE_MENU = 'button[data-cy="menu-user-profile"]'
TIMEZONE_INPUT = 'input[data-cy="input-timezone-select"]'
CURRENT_LOCAL_TIME = '[data-cy="current-local-time"]'

INHERIT_OPTION = f"Use Afghanistan timezone ({BUSINESS_AREA_TIMEZONE})"

# The data fixtures must precede `login` in every signature below: `login` loads
# the SPA, which fetches the profile once. A fixture that writes timezones after
# that runs against an already-rendered page.


def _pick_timezone(browser: HopeTestBrowser, option_name: str) -> None:
    """Filter the timezone list down to `option_name`, then select it.

    The choice list holds every IANA identifier, so typing first keeps the
    listbox small enough that the option click cannot land on a re-render.
    """
    browser.set_value(TIMEZONE_INPUT, option_name)
    browser.select_listbox_element(option_name)


def test_user_selects_a_personal_timezone(logged_in_user: User, login: HopeTestBrowser) -> None:
    login.click(PROFILE_MENU)

    # With no preference stored, the effective timezone comes from the Business Area.
    login.assert_text(f"({BUSINESS_AREA_TIMEZONE})", CURRENT_LOCAL_TIME)
    login.assert_text("Inherited from Afghanistan", CURRENT_LOCAL_TIME)

    _pick_timezone(login, PERSONAL_TIMEZONE)

    login.assert_text(f"({PERSONAL_TIMEZONE})", CURRENT_LOCAL_TIME)
    login.assert_text("Personal timezone preference", CURRENT_LOCAL_TIME)

    logged_in_user.refresh_from_db()
    assert str(logged_in_user.timezone) == PERSONAL_TIMEZONE


def test_user_clears_the_preference_to_inherit_from_business_area(
    user_with_timezone_preference: User, login: HopeTestBrowser
) -> None:
    login.click(PROFILE_MENU)

    login.assert_text(f"({PERSONAL_TIMEZONE})", CURRENT_LOCAL_TIME)
    login.assert_text("Personal timezone preference", CURRENT_LOCAL_TIME)

    # Selecting the inheritance entry sends timezone=null, which is the only way
    # a user can go back to following the Business Area.
    _pick_timezone(login, INHERIT_OPTION)

    login.assert_text(f"({BUSINESS_AREA_TIMEZONE})", CURRENT_LOCAL_TIME)
    login.assert_text("Inherited from Afghanistan", CURRENT_LOCAL_TIME)

    user_with_timezone_preference.refresh_from_db()
    assert user_with_timezone_preference.timezone is None
