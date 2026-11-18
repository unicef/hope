import pytest

from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.selenium import HopeTestBrowser
from hope.models import BusinessArea, Program

from .conftest import details_url

pytestmark = pytest.mark.django_db()

NAV_PROGRAMME_USERS = 'a[data-cy="nav-Programme Users"]'
TABLE_TITLE = 'h6[data-cy="table-title"]'
TABLE_HEAD = "thead"
TABLE_BODY = "tbody"
STATUS = 'div[data-cy="status-container"]'
SORTED_DESC_HEADER = 'th[aria-sort="descending"]'
TABLE_PAGINATION = 'div[data-cy="table-pagination"]'
TABLE_PAGINATION_SELECT = f"{TABLE_PAGINATION} .MuiTablePagination-select"
ARROW_DOWN = 'button[data-cy="arrow-down"]'
COUNTRY_ROLE = 'div[data-cy="country-role"]'
MAPPED_COUNTRY_ROLE = 'div[data-cy="mapped-country-role"]'


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


def test_programme_users_lists_user_with_roles(program: Program, login: HopeTestBrowser) -> None:
    login.open(details_url(program))
    login.wait_for_element_clickable(NAV_PROGRAMME_USERS, timeout=60).click()

    login.assert_text("Users List", TABLE_TITLE)
    login.assert_text("Name", TABLE_HEAD)
    login.assert_text("Status", TABLE_HEAD)
    login.assert_text("Partner", TABLE_HEAD)
    login.assert_text("Email", TABLE_HEAD)
    login.assert_text("Last Login", TABLE_HEAD)
    # The only user in the business area is the superuser from create_super_user
    login.assert_text("Test Selenium", TABLE_BODY)
    login.assert_text("INVITED", STATUS)
    login.assert_text("UNICEF HQ", TABLE_BODY)
    login.assert_text("test@example.com", TABLE_BODY)
    login.assert_text("Status", SORTED_DESC_HEADER)
    login.assert_text("sorted descending", SORTED_DESC_HEADER)
    login.assert_text("Rows per page:", TABLE_PAGINATION)
    login.assert_text("10", TABLE_PAGINATION_SELECT)
    login.assert_text("1–1 of 1", TABLE_PAGINATION)

    login.click(ARROW_DOWN)
    login.assert_text("Country / Program / Role", COUNTRY_ROLE)
    login.assert_text("Afghanistan / All / Role", MAPPED_COUNTRY_ROLE)
