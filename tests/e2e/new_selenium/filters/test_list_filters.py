from typing import TYPE_CHECKING

import pytest

from extras.test_utils.selenium import HopeTestBrowser
from hope.models import Program

if TYPE_CHECKING:
    from e2e.new_selenium.filters.conftest import SearchPair

pytestmark = pytest.mark.django_db()

TABLE = "table"
BUTTON_APPLY = 'button[data-cy="button-filters-apply"]'
BUTTON_CLEAR = 'button[data-cy="button-filters-clear"]'
PAGE_HEADER_TITLE = 'h5[data-cy="page-header-title"]'


def program_url(program: Program, path: str) -> str:
    return f"/{program.business_area.slug}/programs/{program.code}/{path}"


def cy(*names: str) -> tuple[str, ...]:
    return tuple(f'[data-cy="{name}"]' for name in names)


@pytest.mark.parametrize(
    ("path", "filters"),
    [
        pytest.param(
            "registration-data-import",
            cy(
                "filter-search",
                "Imported By-input",
                "filter-status",
                "filter-size-min",
                "filter-size-max",
                "filter-import-date-range-min",
                "filter-import-date-range-max",
            ),
            id="registration-data-import",
        ),
        pytest.param(
            "population/household",
            cy(
                "hh-filters-search",
                "filters-document-type",
                "filters-document-number",
                "hh-filters-residence-status",
                "hh-filters-admin2",
                "hh-filters-household-size-from",
                "hh-filters-household-size-to",
                "hh-filters-order-by",
                "hh-filters-status",
            ),
            id="households",
        ),
        pytest.param(
            "population/individuals",
            cy(
                "ind-filters-search",
                "filters-document-type",
                "filters-document-number",
                "ind-filters-gender",
                "ind-filters-age-from",
                "ind-filters-age-to",
                "ind-filters-flags",
                "ind-filters-order-by",
                "ind-filters-status",
                "ind-filters-reg-date-from",
                "ind-filters-reg-date-to",
            ),
            id="individuals",
        ),
        pytest.param(
            "target-population",
            cy(
                "filters-search",
                "filters-status",
                "filters-total-households-count-min",
                "filters-total-households-count-max",
                "date-picker-filter-From",
                "date-picker-filter-To",
            ),
            id="targeting",
        ),
        pytest.param(
            "payment-module/payment-plans",
            cy("filter-search", "date-picker-filter-From", "date-picker-filter-To"),
            id="payment-plans",
        ),
        pytest.param(
            "payment-verification",
            cy(
                "filter-search",
                "filter-status",
                "filter-fsp",
                "filter-Modality",
                "filter-start-date",
                "filter-end-date",
            ),
            id="payment-verification",
        ),
        pytest.param(
            "grievance/tickets/user-generated",
            cy(
                "filters-search",
                "filters-document-type",
                "filters-document-number",
                "filters-status",
                "filters-fsp",
                "filters-creation-date-from",
                "filters-creation-date-to",
                "filters-category",
                "filters-admin-level-2",
                "filters-assignee",
                "Assigned To-input",
                "filters-created-by-autocomplete",
                "filters-registration-data-import",
                "filters-preferred-language",
                "filters-priority",
                "filters-urgency",
                "filters-active-tickets",
            ),
            id="grievance-tickets",
        ),
        pytest.param(
            "grievance/feedback",
            cy(
                "filters-search",
                "filters-issue-type",
                "filters-created-by-autocomplete",
                "filters-creation-date-from",
                "filters-creation-date-to",
            ),
            id="feedback",
        ),
        pytest.param(
            "accountability/communication",
            cy(
                "filters-target-population-autocomplete",
                "Target Population-input",
                "Created by-input",
                "filters-creation-date-from",
                "filters-creation-date-to",
            ),
            id="communication",
        ),
        pytest.param(
            "accountability/surveys",
            cy(
                "filters-search",
                "filters-target-population-autocomplete",
                "Target Population-input",
                "Created by-input",
                "filters-creation-date-from",
                "filters-creation-date-to",
            ),
            id="surveys",
        ),
        pytest.param(
            "activity-log",
            cy("filters-search", "filters-residence-status", "User-input"),
            id="programme-log",
        ),
    ],
)
def test_list_page_shows_filters(program: Program, login: HopeTestBrowser, path: str, filters: tuple[str, ...]) -> None:
    login.open(program_url(program, path))

    login.assert_elements(*filters)


@pytest.mark.parametrize(
    ("pair_fixture", "path", "title", "search_input"),
    [
        pytest.param(
            "rdi_pair",
            "registration-data-import",
            "Registration Data Import",
            "filter-search",
            id="registration-data-import",
        ),
        pytest.param("target_population_pair", "target-population", "Targeting", "filters-search", id="targeting"),
        pytest.param(
            "verification_pair",
            "payment-verification",
            "Payment Verification",
            "filter-search",
            id="payment-verification",
        ),
        pytest.param(
            "grievance_ticket_pair",
            "grievance/tickets/user-generated",
            "Grievance Tickets",
            "filters-search",
            id="grievance-tickets",
        ),
        pytest.param(
            "payment_plan_pair", "payment-module/payment-plans", "Payment Module", "filter-search", id="payment-plans"
        ),
        pytest.param("household_pair", "population/household", "Households", "hh-filters-search", id="households"),
    ],
)
def test_search_filter(
    request: pytest.FixtureRequest,
    program: Program,
    login: HopeTestBrowser,
    pair_fixture: str,
    path: str,
    title: str,
    search_input: str,
) -> None:
    pair: SearchPair = request.getfixturevalue(pair_fixture)
    search = f'[data-cy="{search_input}"] input'
    login.open(program_url(program, path))
    login.assert_text(title, PAGE_HEADER_TITLE)
    login.wait_for_text(pair.shown, TABLE)
    login.wait_for_text(pair.hidden, TABLE)

    login.type(search, "Wrong value")
    login.click(BUTTON_APPLY)
    login.wait_for_text_not_visible(pair.shown, TABLE)
    login.assert_text_not_visible(pair.hidden, TABLE)

    login.click(BUTTON_CLEAR)
    login.wait_for_text(pair.shown, TABLE)
    login.wait_for_text(pair.hidden, TABLE)

    login.type(search, pair.shown)
    login.click(BUTTON_APPLY)
    login.wait_for_text_not_visible(pair.hidden, TABLE)
    login.assert_text(pair.shown, TABLE)
