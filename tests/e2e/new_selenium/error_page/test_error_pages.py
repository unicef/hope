from collections.abc import Callable

import pytest

from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Program, User

pytestmark = pytest.mark.django_db()

PAGE_NOT_FOUND_TITLE = '[data-cy="page-not-found-title"]'
ACCESS_DENIED_TITLE = '[data-cy="access-denied-title"]'
BUTTON_REFRESH_PAGE = '[data-cy="button-refresh-page"]'
BUTTON_GO_TO_PROGRAMME_MANAGEMENT = '[data-cy="go-to-programme-management"]'
BUTTON_GO_BACK = '[data-cy="button-go-back"]'


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


def missing_program_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/NONEXISTENT/country-dashboard"


def unknown_route_url(program: Program) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/this-route-does-not-exist"


@pytest.mark.parametrize(
    "build_url",
    [
        pytest.param(missing_program_url, id="missing-program"),
        pytest.param(unknown_route_url, id="unknown-route"),
    ],
)
def test_page_not_found(program: Program, login: HopeTestBrowser, build_url: Callable[[Program], str]) -> None:
    login.open(build_url(program))

    login.assert_text("Oops! Page Not Found", PAGE_NOT_FOUND_TITLE)
    login.assert_text("REFRESH PAGE", BUTTON_REFRESH_PAGE)
    login.assert_text("GO TO PROGRAMME MANAGEMENT", BUTTON_GO_TO_PROGRAMME_MANAGEMENT)


def test_access_denied_for_user_without_business_area(browser: HopeTestBrowser, user_with_no_permissions: User) -> None:
    browser.login(user_with_no_permissions.username, wait_for_drawer=False)
    browser.open("/")

    browser.assert_text("Access Denied", ACCESS_DENIED_TITLE)
    browser.assert_text("REFRESH PAGE", BUTTON_REFRESH_PAGE)
    browser.assert_text("GO BACK", BUTTON_GO_BACK)
