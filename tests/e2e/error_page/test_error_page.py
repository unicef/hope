import pytest

from e2e.helpers.fixtures import get_program_with_dct_type_and_name
from e2e.page_object.error_page.error_page import ErrorPage
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db()


@pytest.fixture
def program() -> Program:
    return get_program_with_dct_type_and_name("Test Program", "NORM")


@pytest.mark.usefixtures("login")
def test_page_not_found_for_missing_program(page_error: ErrorPage, business_area: BusinessArea) -> None:
    page_error.navigate_to_non_existent_program(business_area.slug)
    page_error.wait_for_text("Oops! Page Not Found", page_error.page_not_found_title)
    assert "REFRESH PAGE" in page_error.get_button_refresh_page().text
    assert "GO TO PROGRAMME MANAGEMENT" in page_error.get_button_go_to_programme_management().text


@pytest.mark.usefixtures("login")
def test_page_not_found_for_unknown_route(page_error: ErrorPage, business_area: BusinessArea, program: Program) -> None:
    page_error.navigate_to_unknown_route(business_area.slug, program.code)
    page_error.wait_for_text("Oops! Page Not Found", page_error.page_not_found_title)
    assert "REFRESH PAGE" in page_error.get_button_refresh_page().text
    assert "GO TO PROGRAMME MANAGEMENT" in page_error.get_button_go_to_programme_management().text
